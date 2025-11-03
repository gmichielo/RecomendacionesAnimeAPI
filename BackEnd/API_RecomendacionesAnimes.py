from flask import Flask, request, jsonify
import pickle #Libreria para guardar/cargar el modelo
import pandas as pd
import numpy as np
import os
import html
import random

# Ruta unica de busqueda del modelo_corrMatrix.pkl en la misma carpeta que este .py
MODEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_corrMatrix.pkl")

app = Flask(__name__)

vers = "0.0.5"

corrMatrix = None
anime = None
ratings = None

def entrenar_modelo(force=False):
    # Si force=False, intenta cargar desde archivo. Si no existe, entrena y guarda.
    global corrMatrix, anime, ratings

    # Archivos dentro de la carpeta "RecomendacionesAnime" relativa al notebook 
    base_path = os.path.dirname(os.path.abspath(__file__))
    anime_file = os.path.join(base_path, "anime.csv")
    ratings_file = os.path.join(base_path, "rating.csv")

    # Intentar cargar modelo existente
    if not force and os.path.exists(MODEL_FILE): # Comprobacion de existencia del .pkl y no es forzado a volver a entrenar
        print("\033[36m### Cargando modelo entrenado desde archivo...\033[0m")
        # Carga del archivo/modelo
        with open(MODEL_FILE, "rb") as f:
            data = pickle.load(f) # Lectura y deserializacion los datos guardados
            corrMatrix = data["corrMatrix"] # Recupera si existe corrMatrix
            anime = data["anime"] # Recupera si existe anime
            ratings = data["ratings"] # Recupera si existe ratings
        print("\033[32m### Modelo cargado correctamente.\033[0m")
        return
    
    # Si no existe el modelo entrenar desde cero
    print("\033[33m### Entrenando modelo desde cero...\033[0m")

    anime_cols = ['anime_id', 'name', 'genre', 'type', 'episodes', 'rating', 'members']
    ratings_cols = ['user_id', 'anime_id', 'rating']

    # Cargar los CSVs
    # El encoding="utf-8" lo que hace es controlar los caracteres raros estilo ñ
    anime = pd.read_csv(anime_file, names=anime_cols, header=0, encoding="utf-8")
    ratings = pd.read_csv(ratings_file, names=ratings_cols, header=0, encoding="utf-8")

    # El html lo que hace es por si haya algun caracter raro pues lo ponga de forma normal
    anime['name'] = anime['name'].apply(html.unescape)

    # Se sabe que alguno de estos no los usamos pero los limpiamos y arregalos por si acaso se desea utilizar a futuro
    anime['episodes'] = anime['episodes'].replace('Unknown', np.nan).astype(float)
    anime['genre'] = anime['genre'].fillna('Unknown')
    anime['rating'] = anime['rating'].fillna(anime['rating'].mean())
    anime['type'] = anime['type'].fillna('Unknown')

    # Eliminamos y/o tratamos los que tengan alguna columna vacia o en otras diferente (ejemplo un caso de un anime que parte de sus datos estaba en la B del csv)
    anime = anime.dropna(subset=['episodes', 'rating', 'type', 'genre'])
    ratings = ratings[ratings['rating'] != -1]
    ratings = ratings.dropna(subset=['user_id', 'anime_id', 'rating'])

    # Cambio de nombres para tenerlos mas claros
    ratings = ratings.rename(columns={"rating": "user_rating"})
    anime = anime.rename(columns={"rating": "anime_rating"})

    # Estas lineas cambian el tipo de datos de las columnas introducidas a category
    # Los category ocupan menos espacio que object o int
    ratings_with_id = ratings.merge(anime[['anime_id', 'name']], on='anime_id', how='inner')
    ratings_with_id['anime_id'] = ratings_with_id['anime_id'].astype('category')
    ratings_with_id['user_id'] = ratings_with_id['user_id'].astype('category')

    # Filtrar por los animes más puntuados
    anime_counts = ratings_with_id['anime_id'].value_counts()
    popular_animes = anime_counts[anime_counts > 300].index
    filtered = ratings_with_id[ratings_with_id['anime_id'].isin(popular_animes)]

    # Creacion de tabla en donde cada fila es un usuario y cada columna es un anume, y las celdas los rating
    ratings_pivot = filtered.pivot_table(
        index='user_id', # Filas
        columns='anime_id', # Columnas
        values='user_rating', # Valores
        aggfunc='mean', # Sacar promedio si hay repetidos
        observed=True # Optimizacion si hay categorias
    ).astype('float32')

    corrMatrix = ratings_pivot.corr(method='pearson', min_periods=250) # Minimo 250 que evaluaron los animes

    # Guardar modelo
    print("\033[33m###Guardando modelo entrenado en archivo...\033[0m")
    with open(MODEL_FILE, "wb") as f: # Abre el archivo en modo escritura binaria (wb = write binary)
        pickle.dump({ # Guardado de datos
            "corrMatrix": corrMatrix,
            "anime": anime,
            "ratings": ratings
        }, f)
    print(f"\033[32m### Modelo guardado en {MODEL_FILE}\033[0m")

###     EndPoints
@app.route("/version", methods=["GET"])
def version():
    return jsonify({"version": vers}), 200


@app.route("/entrenar", methods=["POST"])
def entrenar():
    try:
        force = request.args.get("force", "false").lower() == "true"
        entrenar_modelo(force=force)
        return jsonify({"mensaje": "Modelo cargado o entrenado correctamente"}), 200
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
        user_ratings = request.json  # Diccionario enviado desde consola {anime_id: calificación}
        if not user_ratings:
            return jsonify({"error": "Debes enviar un JSON con las calificaciones del usuario (anime_id: rating)"}), 400

        # Filtrar solo animes conocidos
        available_ids = [int(aid) for aid in user_ratings.keys() if int(aid) in corrMatrix.columns]
        if not available_ids:
            return jsonify({"error": "Ninguno de los animes enviados está en el modelo"}), 400

        myRatings = pd.Series({int(aid): user_ratings[str(aid)] for aid in available_ids})

        simCandidates = pd.Series(dtype='float64') # Creacion de serie vacia
        for anime_id, rating_value in myRatings.items():
            # Recuperar las similitudes del anime actual
            sims = corrMatrix[anime_id].dropna()
            # Escalar la similaridad multiplicando la correlación por la calificación de la persona
            sims = sims.map(lambda x: x * rating_value)
            # Agregar al conjunto de candidatos
            simCandidates = pd.concat([simCandidates, sims])

        # Agrupar y ordenar resultados
        simCandidates = simCandidates.groupby(simCandidates.index).sum() # Agrupamos para sumar puntaje por que salen repetidos
        simCandidates.sort_values(inplace=True, ascending=False)
        filteredSims = simCandidates.drop(myRatings.index, errors='ignore')

        # Convertir a DataFrame para mantener orden y serializar
        top_recommendations = (
            filteredSims
            .head(10)
            .reset_index()
            .rename(columns={"index": "anime_id", 0: "puntaje"})
        )

        # Agregar nombres a las recomendaciones
        top_recommendations = top_recommendations.merge(
            anime[['anime_id', 'name']], on='anime_id', how='left'
        )

        # Agregar nombres a los animes del usuario
        user_data = (
            pd.DataFrame({
                "anime_id": list(map(int, myRatings.index)),
                "rating": list(myRatings.values)
            })
            .merge(anime[['anime_id', 'name']], on='anime_id', how='left')
        )

        # El .to_dict convierte un DataFrame de Pandas en una lista de diccionarios
        usuario_ratings_list = user_data.to_dict(orient='records')
        recomendaciones_list = top_recommendations.to_dict(orient='records')

        return jsonify({
            "usuario_ratings": usuario_ratings_list,
            "recomendaciones_top_10": recomendaciones_list
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
        # Filtrar solo los animes que están en la matriz de correlación
        disponibles = anime[anime['anime_id'].isin(corrMatrix.columns)]
        sample = disponibles.sample(n=min(100, len(disponibles)), random_state=random.randint(0, 9999)) # Seleccionar aleatoriamente 100 entre todos
        
        # Convertir en lista para enviarlo por json
        lista = sample[['anime_id', 'name']].values.tolist()
        return jsonify({"animes": lista}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"No se pudieron obtener los animes: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
