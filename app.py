from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

# Simulando el DataFrame con datos de películas
# Puedes reemplazar esto con tu propia lógica para obtener el DataFrame real
# Lee el archivo CSV omitiendo las primeras 5 millones de filas y leyendo las siguientes 5 millones de filas
data_parte_otra_instancia = pd.read_csv('ratings.csv', skiprows=range(1, 10000001), nrows=5000000, header=0)

# Asignar IDs automáticamente a las películas del JSON
pelicula_ids = {f"pelicula{i}": id for i, id in zip(range(1, 6), [296, 778, 912, 1089, 1200])}

# Crear objetos para cada usuario del DataFrame
usuarios = []

for user_id, group in data_parte_otra_instancia.groupby('userId'):
    calificaciones = {row['movieId']: row['rating'] for _, row in group.iterrows()}
    usuarios.append({'userId': user_id, 'calificaciones': calificaciones})

# Crear un diccionario para acceder a los usuarios por su ID
usuarios_dict = {usuario['userId']: usuario for usuario in usuarios}

@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        user_data = request.json
        app.logger.info('Usuario recibido en la otra instancia: %s', user_data)

        # Asignar automáticamente IDs a las películas del JSON
        user_ratings = {key: {"movieId": pelicula_ids[key], "rating": float(user_data[key])} for key in pelicula_ids}

        # Crear un DataFrame a partir de los datos del usuario
        df_usuario = pd.DataFrame.from_dict(user_ratings, orient='index').reset_index()
        df_usuario.columns = ['pelicula', 'movieId', 'rating']

        # Calcular la distancia euclidiana entre el usuario recibido y cada usuario en el conjunto de datos
        distancias = []

        for usuario in usuarios:
            # Obtener las calificaciones del usuario actual
            calificaciones_usuario = [usuario['calificaciones'].get(movie_id, 0) for movie_id in df_usuario['movieId']]
            
            # Calcular la distancia euclidiana
            distancia = np.linalg.norm(
                df_usuario['rating'].values - np.array(calificaciones_usuario)
            )
            distancias.append({'userId': usuario['userId'], 'distancia': distancia})

        # Encontrar el usuario más cercano
        usuario_mas_cercano = min(distancias, key=lambda x: x['distancia'])
        app.logger.info(f'Usuario más cercano: {usuario_mas_cercano}')

        # Obtener las calificaciones del usuario más cercano
        calificaciones_usuario_mas_cercano = usuarios_dict[usuario_mas_cercano['userId']]['calificaciones']

        # Imprimir las calificaciones del usuario más cercano para las películas específicas
        app.logger.info('Calificaciones del usuario más cercano para las películas específicas:')
        app.logger.info(calificaciones_usuario_mas_cercano)

        # Filtrar las películas recomendadas (con rating 5) y que no estén en la lista prohibida
        recomendaciones = {movie_id: rating for movie_id, rating in calificaciones_usuario_mas_cercano.items() if rating == 5 and movie_id not in [296, 778, 912, 1089, 1200]}

        # Obtener las primeras 10 películas recomendadas
        recomendaciones = dict(sorted(recomendaciones.items(), key=lambda item: item[1], reverse=True)[:10])

        # Imprimir las calificaciones del usuario más cercano para las películas específicas
        app.logger.info('Calificaciones del usuario más cercano para las películas específicas:')
        app.logger.info(recomendaciones)

        respuesta = {
            "vecino": usuario_mas_cercano,
            "peliculas": recomendaciones,
            "usuario": user_data['usuario'],
        }

        # Resto del código...

        return jsonify(respuesta)

    except Exception as e:
        app.logger.error('Error en la función procesar en la otra instancia: %s', str(e))
        return jsonify({'error': 'Error interno en la otra instancia'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Puerto diferente para la otra instancia

