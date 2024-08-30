FROM python:3.10

WORKDIR /app


COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY ./potato_pyserver ./potato_pyserver

EXPOSE 8000

CMD ["fastapi", "run", "./potato_pyserver/main.py", "--host", "0.0.0.0", "--port", "8000"]
