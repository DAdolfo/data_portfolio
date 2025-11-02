FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    openjdk-17-jdk-headless \
    bash \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-arm64"
ENV SPARK_HOME="/opt/spark"
ENV SPARK_LOCAL_HOSTNAME="localhost"
ENV PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

RUN mkdir -p ${SPARK_HOME} \
    && wget -qO- https://dlcdn.apache.org/spark/spark-4.0.1/spark-4.0.1-bin-hadoop3.tgz \
       | tar xz -C ${SPARK_HOME} --strip-components=1

RUN wget -P ${SPARK_HOME}/jars/ \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r pipeline_requirements.txt

CMD ["python3", "ingestion_pipeline.py"]