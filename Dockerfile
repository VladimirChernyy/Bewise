FROM python:3.10

RUN mkdir /bewise_app
WORKDIR /bewise_app

COPY requirements.txt .

RUN pip install  --upgrade pip --no-cache-dir --upgrade -r requirements.txt

COPY . .

WORKDIR app

CMD gunicorn --worker-class uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app

