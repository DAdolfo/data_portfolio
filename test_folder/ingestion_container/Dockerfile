FROM python:3.11-slim-bookworm

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    openjdk-17-jdk-headless \
    bash \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Variables de entorno
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-arm64"
ENV SPARK_HOME="/opt/spark"
ENV PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

# Instalar Spark
RUN mkdir -p ${SPARK_HOME} \
    && wget -qO- https://dlcdn.apache.org/spark/spark-4.0.1/spark-4.0.1-bin-hadoop3.tgz \
       | tar xz -C ${SPARK_HOME} --strip-components=1

# Copiar código
WORKDIR /app
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r pipeline_requirements.txt

#CMD ["echo", "hello world"]