from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
import os
import html
import random
import mysql.connector
import bcrypt

# ===================== CONFIGURACIÓN BASE =====================
MODEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_corrMatrix.pkl")
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=os.path.join(base_dir, "templates"), static_folder=os.path.join(base_dir, "static"))
CORS(app)
app.secret_key = "clave_super_segura"

vers = "0.0.6"
corrMatrix = None
anime = None
ratings = None

# ===================== CONFIGURACIÓN MYSQL DINÁMICA =====================
DB_CONFIG = {
    "host": None,
    "user": None,
    "password": None,
    "database": None
}

def get_db_connection():
    try:
        if not DB_CONFIG["user"]:
            raise Exception("Configuración MySQL no establecida aún.")
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("❌ Error conectando a MySQL:", e)
        return None


@app.route("/set_db_config", methods=["POST"])
def set_db_config():
    data = request.get_json()
    DB_CONFIG["host"] = data.get("host", "localhost")
    DB_CONFIG["user"] = data.get("user")
    DB_CONFIG["password"] = data.get("password", "")
    DB_CONFIG["database"] = data.get("database", "logins_api_anime")

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()
        print(f"✅ Conexión MySQL correcta: {DB_CONFIG['user']}@{DB_CONFIG['host']}")
        return jsonify({"status": "ok", "message": "Conexión MySQL correcta"})
    except Exception as e:
        print("❌ Error conectando a MySQL:", e)
        return jsonify({"status": "error", "message": str(e)}), 400


# =====================================================
# 🔐 LOGIN Y REGISTRO REALES CON MYSQL
# =====================================================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    usuario = data.get("usuario")
    contrasenya = data.get("contrasenya")

    if not usuario or not contrasenya:
        return jsonify({"status": "error", "message": "Por favor, completa usuario y contraseña"}), 400

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT contrasenya FROM usuario_contrasenyas WHERE usuario = %s", (usuario,))
        user = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Error de conexión MySQL:", e)
        return jsonify({"status": "error", "message": "Error conectando a la base de datos"}), 500

    if not user:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    hash_guardado = user["contrasenya"]
    if not bcrypt.checkpw(contrasenya.encode("utf-8"), hash_guardado.encode("utf-8")):
        return jsonify({"status": "error", "message": "Contraseña incorrecta"}), 401

    return jsonify({"status": "ok", "message": f"Bienvenido {usuario}"}), 200



@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    usuario = data.get("usuario")
    contrasenya = data.get("contrasenya")

    if not usuario or not contrasenya:
        return jsonify({"status": "error", "message": "Por favor, completa todos los campos"}), 400

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idUsuario_contrasenya FROM usuario_contrasenyas WHERE usuario = %s", (usuario,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"status": "error", "message": "El usuario ya existe"}), 409

        hash_contra = bcrypt.hashpw(contrasenya.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute("INSERT INTO usuario_contrasenyas (usuario, contrasenya) VALUES (%s, %s)", (usuario, hash_contra))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "ok", "message": "Usuario registrado correctamente"}), 201
    except Exception as e:
        print("❌ Error al registrar:", e)
        return jsonify({"status": "error", "message": "Error registrando el usuario"}), 500



# ===================== ENTRENAMIENTO DEL MODELO =====================
def entrenar_modelo(force=False):
    """Entrena o carga el modelo de correlación de animes"""
    global corrMatrix, anime, ratings

    base_path = os.path.dirname(os.path.abspath(__file__))
    anime_file = os.path.join(base_path, "anime.csv")
    ratings_file = os.path.join(base_path, "rating.csv")

    if not force and os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, "rb") as f:
            data = pickle.load(f)
            corrMatrix = data["corrMatrix"]
            anime = data["anime"]
            ratings = data["ratings"]
        return

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

    with open(MODEL_FILE, "wb") as f:
        pickle.dump({
            "corrMatrix": corrMatrix,
            "anime": anime,
            "ratings": ratings
        }, f)


# ===================== ENDPOINTS EXISTENTES =====================
@app.route("/", methods=["GET"])
def home():
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
            return f"<h3 style='color:#00b4d8;text-align:center'>{mensaje}</h3>", 200

        return jsonify({"mensaje": mensaje}), 200
    except Exception as e:
        return jsonify({"error": f"Error durante el entrenamiento: {str(e)}"}), 500


@app.route("/recomendar", methods=["POST"])
def recomendar():
    global corrMatrix, anime
    if corrMatrix is None:
        return jsonify({"error": "El modelo no está entrenado. Llama primero a /entrenar"}), 400

    try:
        user_ratings = request.json
        if not user_ratings:
            return jsonify({"error": "Debes enviar calificaciones"}), 400

        available_ids = [int(aid) for aid in user_ratings.keys() if int(aid) in corrMatrix.columns]
        if not available_ids:
            return jsonify({"error": "Animes no válidos"}), 400

        myRatings = pd.Series({int(aid): user_ratings[str(aid)] for aid in available_ids})

        simCandidates = pd.Series(dtype='float64')
        for anime_id, rating_value in myRatings.items():
            sims = corrMatrix[anime_id].dropna()
            sims = sims.map(lambda x: x * rating_value)
            simCandidates = pd.concat([simCandidates, sims])

        simCandidates = simCandidates.groupby(simCandidates.index).sum()
        simCandidates.sort_values(inplace=True, ascending=False)
        filteredSims = simCandidates.drop(myRatings.index, errors='ignore')

        top = filteredSims.head(10).reset_index()
        top.columns = ["anime_id", "puntaje"]
        top = top.merge(anime[['anime_id', 'name']], on='anime_id', how='left')

        return jsonify({"recomendaciones_top_10": top.to_dict(orient='records')}), 200

    except Exception as e:
        return jsonify({"error": f"Error generando recomendaciones: {str(e)}"}), 500


@app.route("/animes", methods=["GET"])
def obtener_animes():
    global anime, corrMatrix
    if anime is None or corrMatrix is None:
        return jsonify({"error": "Los datos no están cargados. Llama primero a /entrenar"}), 400

    disponibles = anime[anime['anime_id'].isin(corrMatrix.columns)]
    sample = disponibles.sample(n=min(100, len(disponibles)), random_state=random.randint(0, 9999))
    lista = sample[['anime_id', 'name']].values.tolist()
    return jsonify({"animes": lista}), 200


if __name__ == "__main__":
    print("🚀 Servidor Flask de OtakuDB corriendo en http://localhost:5000")
    app.run(debug=True)