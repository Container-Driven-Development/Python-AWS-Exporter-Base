FROM python:3.11.4-slim-bookworm

LABEL org.opencontainers.image.source https://github.com/Container-Driven-Development/Python-AWS-Exporter-Base
LABEL org.opencontainers.image.description "Base image for Python scripts exporting AWS resources using boto library to Prometheus"

ENTRYPOINT ["/usr/local/bin/python"]

ADD requirements.txt /requirements.txt

CMD ["pip", "install", "--no-cache-dir", "-r", "/requirements.txt"]
