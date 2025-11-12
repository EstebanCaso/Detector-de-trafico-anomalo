FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY backend/ /app/backend/

# Crear directorios
RUN mkdir -p logs data

# Exponer puerto
EXPOSE 5000

# Comando por defecto
CMD ["python", "backend/app.py"]
