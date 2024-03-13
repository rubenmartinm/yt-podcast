# Usa la imagen oficial de Python 3.9 basada en Alpine Linux
FROM python:3.9-alpine

# Instala ffmpeg y otras dependencias
RUN apk update && apk add --no-cache ffmpeg \
    && rm -rf /var/cache/apk/*

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requerimientos y luego instala las dependencias de Python
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Limpia los archivos temporales de la instalación de Python
RUN rm -rf /root/.cache

# Copia el código fuente al contenedor
COPY . .

# Comando predeterminado a ejecutar cuando se inicie el contenedor
CMD ["python", "main.py"]

