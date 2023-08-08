FROM python:3.11.4-slim-bookworm

LABEL org.opencontainers.image.source https://github.com/Container-Driven-Development/Python-AWS-Exporter-Base

ENTRYPOINT ["/usr/local/bin/python"]

ADD requirements.txt /requirements.txt

CMD ["pip", "install", "--no-cache-dir", "-r", "/requirements.txt"]
