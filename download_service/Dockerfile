FROM python:3.11-alpine

WORKDIR /app


RUN apk add --no-cache ffmpeg
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install -U yt-dlp

COPY app .
CMD ["python", "main.py"]