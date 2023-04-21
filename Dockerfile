FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 443

HEALTHCHECK CMD curl --fail http://localhost:443/ping || exit 1

CMD ["python", "main.py"]

ENTRYPOINT ["python", "main.py"]