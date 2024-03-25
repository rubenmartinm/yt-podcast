# Usa la imagen oficial de Python 3.9 basada en Alpine Linux
FROM python:3.9-alpine

# Instala ffmpeg y otras dependencias
RUN apk update && apk add --no-cache ffmpeg \
    && rm -rf /var/cache/apk/*

# Establece el directorio de trabajo en /app
WORKDIR /app

# Establece un directorio de caché dentro de /app y asigna permisos de escritura
RUN mkdir -p cache && chmod 777 cache

# Establece la variable de entorno XDG_CACHE_HOME para apuntar al directorio de caché creado
ENV XDG_CACHE_HOME /app/cache

# Copia los archivos de requerimientos y luego instala las dependencias de Python
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Limpia los archivos temporales de la instalación de Python
RUN rm -rf /root/.cache

# Copia el código fuente al contenedor
COPY . .

# Comando predeterminado a ejecutar cuando se inicie el contenedor
CMD ["python", "main.py"]

