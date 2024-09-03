FROM python:3.10

WORKDIR /app


COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY ./potato_pyserver ./potato_pyserver

EXPOSE 443

CMD ["uvicorn", "potato_pyserver.main:app", "--host", "0.0.0.0", "--port", "443", "--ssl-keyfile", "/run/secrets/keyfile", "--ssl-certfile", "/run/secrets/certfile"]
