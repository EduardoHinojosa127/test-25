import pandas as pd

# Lee el archivo CSV
data = pd.read_csv('ratings.csv')

# Limita a 100,000 datos
data_limitada = data.head(100000)

# Filtra por userID 3.0
data_filtrada = data_limitada[data_limitada['userId'] == 3.0]

# Imprime el DataFrame resultante
print(data_filtrada)
