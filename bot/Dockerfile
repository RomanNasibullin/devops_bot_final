FROM python:3.10-alpine

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

CMD ["python", "bot.py"]
