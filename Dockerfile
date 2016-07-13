FROM python:2.7
WORKDIR /tj-dev
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt