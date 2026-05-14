FROM python:3.13-alpine
WORKDIR /backend

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host=0.0.0.0", "--port=8000", "--workers=3"]
