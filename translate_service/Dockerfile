FROM python:3.11-alpine

WORKDIR /app


RUN apk add --no-cache \
    nodejs \
    npm

RUN npm install -g vot-cli

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app .

CMD ["python", "main.py"]