from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

# Simulando el DataFrame con datos de películas
# Puedes reemplazar esto con tu propia lógica para obtener el DataFrame real
data_parte_otra_instancia = pd.read_csv('ratings.csv', nrows=25000000)

# Asignar IDs automáticamente a las películas del JSON
pelicula_ids = {f"pelicula{i}": id for i, id in zip(range(1, 6), [296, 778, 912, 1089, 1200])}

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

        # Filtrar películas del vecino más cercano con los movieId específicos
        peliculas_vecino_mas_cercano = data_parte_otra_instancia[
            (data_parte_otra_instancia['movieId'].isin(pelicula_ids.values())) &
            (data_parte_otra_instancia['userId'] != 1)  # Excluir el usuario actual
        ]

        # Filtrar películas del usuario con los movieId específicos
        peliculas_usuario = df_usuario[df_usuario['movieId'].isin(pelicula_ids.values())]

        # Calcular la distancia euclidiana entre el usuario enviado y el vecino más cercano
        distancias = np.linalg.norm(
            peliculas_vecino_mas_cercano[['rating']].values.reshape(1, -1) -
            peliculas_usuario[['rating']].values.reshape(-1, 1), axis=0
        )

        # Encontrar el índice de la distancia euclidiana más baja
        vecino_mas_cercano_index = np.argmin(distancias)

        vecino_mas_cercano_otra_instancia = peliculas_vecino_mas_cercano.iloc[vecino_mas_cercano_index].to_dict()

        # Imprimir las películas del vecino más cercano
        app.logger.info('Películas del vecino más cercano:')
        app.logger.info(peliculas_vecino_mas_cercano[peliculas_vecino_mas_cercano['movieId'].isin(pelicula_ids.values())])

        # Incluir la distancia en la respuesta
        distancia_del_vecino_mas_cercano = distancias[vecino_mas_cercano_index]

        # Preparar la respuesta
        respuesta = {
            'vecino_mas_cercano': vecino_mas_cercano_otra_instancia,
            'distancia_del_vecino_mas_cercano': distancia_del_vecino_mas_cercano,
            'usuario_recibido': user_data['usuario'],
        }

        return jsonify(respuesta)

    except Exception as e:
        app.logger.error('Error en la función procesar en la otra instancia: %s', str(e))
        return jsonify({'error': 'Error interno en la otra instancia'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Puerto diferente para la otra instancia
