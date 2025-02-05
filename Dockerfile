FROM python:3.8
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y sqlite3 libsqlite3-dev
RUN apt-get install -y python3-pip

# Create directories and set permissions
RUN mkdir -p /db && chmod 777 /db
RUN mkdir -p /home/api
WORKDIR /home/api

# Copy application code
COPY requirements.txt .
COPY app/ ./app/
COPY main.py .

RUN pip3 install -r requirements.txt

EXPOSE 3000
