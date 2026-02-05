FROM python:3

RUN pip install Flask

WORKDIR /app

COPY main.py .

RUN mkdir -p /app/data

ENV DATABASE_PATH=/app/data/ecommerce.db

EXPOSE 5000

CMD ["python", "main.py"]
