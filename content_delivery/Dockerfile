FROM python:3.10

WORKDIR /opt/content_delivery

ENV PYTHONPATH /opt/content_delivery/src
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

COPY . .

ENTRYPOINT [ "bash", "entrypoint.sh" ]