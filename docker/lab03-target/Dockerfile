FROM modern-cryptography-2026:latest

WORKDIR /app
COPY instructor/lab03/targets/ /app/
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080
HEALTHCHECK --interval=2s --timeout=2s --retries=10 CMD python3 -c "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=1).status == 200"
CMD ["python3", "server.py"]
