# Usa una imagen base de Python
FROM python:3.8-slim-buster

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido actual al contenedor en /app
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5000
EXPOSE 5000

# Define la variable de entorno FLASK_APP
ENV FLASK_APP=app.py

# Ejecuta la aplicación cuando el contenedor se inicia
CMD ["python", "app.py"]