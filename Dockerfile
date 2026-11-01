FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Textos latinos de D., C., CTh. e I. (BIA) para enlazar las citas; si falla la descarga, la web sigue sin esos enlaces
RUN python romanos.py || true
ENV PORT=8000
EXPOSE 8000
CMD ["python", "server.py"]
