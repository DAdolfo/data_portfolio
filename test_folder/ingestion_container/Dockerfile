FROM python:3.11.4

WORKDIR /usr/src/app

COPY pipeline_requirements.txt ./

RUN pip install --no-cache-dir -r pipeline_requirements.txt

COPY ingestion_pipeline.py ./

CMD ["python3", "ingestion_pipeline.py"]