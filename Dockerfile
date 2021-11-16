FROM python:3.9-slim

ENV LISTEN_PROTOCOL='tcp'
ENV RESOLVER_IP='1.1.1.1'
ENV RESOLVER_PORT=853
ENV SSL_CA_CERTS='/etc/ssl/certs/ca-certificates.crt'
ENV PYTHONPATH="${PYTHONPATH}:/app/util/"

ADD dot-relay /app/dot-relay

ENTRYPOINT ["python3", "/app/dot-relay/main.py"]