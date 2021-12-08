FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

RUN mkdir -p /var/app
WORKDIR /var/app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY analyze.py .
COPY app.py .
COPY client_secret.json .
COPY create_data.py .
COPY datapipe.py .
COPY gmail_client.py .
COPY logger.py .
COPY mongo_client.py .
COPY preprocessor.py .
COPY static static
COPY task_mgr.py .
COPY topic_model.py .
COPY utils.py .
COPY webapp/build webapp/build

ENV MONGO_CONN_STRING "mongodb://mongodb:27017"
ENV MAX_EMAILS 5000
EXPOSE 8080
CMD ["python3", "app.py"]

