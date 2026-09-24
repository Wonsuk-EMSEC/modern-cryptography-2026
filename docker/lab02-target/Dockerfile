FROM modern-cryptography-2026:latest

WORKDIR /app
COPY instructor/lab02/targets/ /app/

ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080
CMD ["python3", "server.py"]
