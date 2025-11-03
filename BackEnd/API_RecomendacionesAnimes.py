from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
import os
import html
import random

# ===================== CONFIGURACIÓN BASE =====================
MODEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_corrMatrix.pkl")

# Flask busca automáticamente los templates y los estáticos en carpetas llamadas "templates" y "static"
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=os.path.join(base_dir, "templates"), static_folder=os.path.join(base_dir, "static"))
CORS(app)

vers = "0.0.5"
corrMatrix = None
anime = None
ratings = None


# ===================== ENTRENAMIENTO DEL MODELO =====================
def entrenar_modelo(force=False):
    """Entrena o carga el modelo de correlación de animes"""
    global corrMatrix, anime, ratings

    base_path = os.path.dirname(os.path.abspath(__file__))
    anime_file = os.path.join(base_path, "anime.csv")
    ratings_file = os.path.join(base_path, "rating.csv")

    if not force and os.path.exists(MODEL_FILE):
        print("\033[36m### Cargando modelo entrenado desde archivo...\033[0m")
        with open(MODEL_FILE, "rb") as f:
            data = pickle.load(f)
            corrMatrix = data["corrMatrix"]
            anime = data["anime"]
            ratings = data["ratings"]
        print("\033[32m### Modelo cargado correctamente.\033[0m")
        return

    print("\033[33m### Entrenando modelo desde cero...\033[0m")

    anime_cols = ['anime_id', 'name', 'genre', 'type', 'episodes', 'rating', 'members']
    ratings_cols = ['user_id', 'anime_id', 'rating']

    anime = pd.read_csv(anime_file, names=anime_cols, header=0, encoding="utf-8")
    ratings = pd.read_csv(ratings_file, names=ratings_cols, header=0, encoding="utf-8")

    anime['name'] = anime['name'].apply(html.unescape)
    anime['episodes'] = anime['episodes'].replace('Unknown', np.nan).astype(float)
    anime['genre'] = anime['genre'].fillna('Unknown')
    anime['rating'] = anime['rating'].fillna(anime['rating'].mean())
    anime['type'] = anime['type'].fillna('Unknown')

    anime = anime.dropna(subset=['episodes', 'rating', 'type', 'genre'])
    ratings = ratings[ratings['rating'] != -1].dropna(subset=['user_id', 'anime_id', 'rating'])

    ratings = ratings.rename(columns={"rating": "user_rating"})
    anime = anime.rename(columns={"rating": "anime_rating"})

    ratings_with_id = ratings.merge(anime[['anime_id', 'name']], on='anime_id', how='inner')
    ratings_with_id['anime_id'] = ratings_with_id['anime_id'].astype('category')
    ratings_with_id['user_id'] = ratings_with_id['user_id'].astype('category')

    anime_counts = ratings_with_id['anime_id'].value_counts()
    popular_animes = anime_counts[anime_counts > 300].index
    filtered = ratings_with_id[ratings_with_id['anime_id'].isin(popular_animes)]

    ratings_pivot = filtered.pivot_table(
        index='user_id',
        columns='anime_id',
        values='user_rating',
        aggfunc='mean',
        observed=True
    ).astype('float32')

    corrMatrix = ratings_pivot.corr(method='pearson', min_periods=250)

    print("\033[33m### Guardando modelo entrenado en archivo...\033[0m")
    with open(MODEL_FILE, "wb") as f:
        pickle.dump({
            "corrMatrix": corrMatrix,
            "anime": anime,
            "ratings": ratings
        }, f)
    print(f"\033[32m### Modelo guardado en {MODEL_FILE}\033[0m")


# ===================== ENDPOINTS =====================

@app.route("/", methods=["GET"])
def home():
    """Sirve el index.html principal"""
    return render_template("index.html")


@app.route("/version", methods=["GET"])
def version():
    return jsonify({"version": vers}), 200


@app.route("/entrenar", methods=["GET", "POST"])
def entrenar():
    try:
        force = request.args.get("force", "false").lower() == "true"
        entrenar_modelo(force=force)
        mensaje = "✅ Modelo cargado o entrenado correctamente"

        if request.method == "GET":
            return f"""
            <html>
              <head><title>OtakuDB Entrenamiento</title></head>
              <body style="background:#0b0d11;color:#e9ecef;font-family:Roboto;text-align:center;padding-top:40px">
                <h2 style="color:#00b4d8;">{mensaje}</h2>
                <p>Ahora puedes volver a <a href="/" style="color:#f94144;">OtakuDB</a> y obtener tus recomendaciones ⚡</p>
              </body>
            </html>
            """, 200

        return jsonify({"mensaje": mensaje}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error durante el entrenamiento: {str(e)}"}), 500


@app.route("/recomendar", methods=["POST"])
def recomendar():
    global corrMatrix, anime

    if corrMatrix is None:
        return jsonify({"error": "El modelo no está entrenado. Llama primero a /entrenar"}), 400

    try:
        user_ratings = request.json
        if not user_ratings:
            return jsonify({"error": "Debes enviar un JSON con las calificaciones del usuario (anime_id: rating)"}), 400

        available_ids = [int(aid) for aid in user_ratings.keys() if int(aid) in corrMatrix.columns]
        if not available_ids:
            return jsonify({"error": "Ninguno de los animes enviados está en el modelo"}), 400

        myRatings = pd.Series({int(aid): user_ratings[str(aid)] for aid in available_ids})

        simCandidates = pd.Series(dtype='float64')
        for anime_id, rating_value in myRatings.items():
            sims = corrMatrix[anime_id].dropna()
            sims = sims.map(lambda x: x * rating_value)
            simCandidates = pd.concat([simCandidates, sims])

        simCandidates = simCandidates.groupby(simCandidates.index).sum()
        simCandidates.sort_values(inplace=True, ascending=False)
        filteredSims = simCandidates.drop(myRatings.index, errors='ignore')

        top_recommendations = (
            filteredSims
            .head(10)
            .reset_index()
            .rename(columns={"index": "anime_id", 0: "puntaje"})
        )

        top_recommendations = top_recommendations.merge(
            anime[['anime_id', 'name']], on='anime_id', how='left'
        )

        user_data = (
            pd.DataFrame({
                "anime_id": list(map(int, myRatings.index)),
                "rating": list(myRatings.values)
            })
            .merge(anime[['anime_id', 'name']], on='anime_id', how='left')
        )

        return jsonify({
            "usuario_ratings": user_data.to_dict(orient='records'),
            "recomendaciones_top_10": top_recommendations.to_dict(orient='records')
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error generando recomendaciones: {str(e)}"}), 500


@app.route("/animes", methods=["GET"])
def obtener_animes():
    global anime, corrMatrix

    if anime is None or corrMatrix is None:
        return jsonify({"error": "Los datos no están cargados. Llama primero a /entrenar"}), 400

    try:
        disponibles = anime[anime['anime_id'].isin(corrMatrix.columns)]
        sample = disponibles.sample(n=min(100, len(disponibles)), random_state=random.randint(0, 9999))
        lista = sample[['anime_id', 'name']].values.tolist()
        return jsonify({"animes": lista}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"No se pudieron obtener los animes: {str(e)}"}), 500


# ===================== MAIN =====================
if __name__ == "__main__":
    print("\033[36mServidor Flask del Recomendador de Animes 2000 en ejecución...\033[0m")
    print("\033[33mAbre tu frontend en el navegador para interactuar: http://localhost:5000\033[0m")
    app.run(debug=True)
