FROM python:3.11-alpine

WORKDIR /app


RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app .

CMD ["python", "main.py"]