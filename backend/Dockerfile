FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r app/requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
