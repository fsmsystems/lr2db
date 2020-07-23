# Dockerfile - this is a comment. Delete me if you want.
FROM python:3.6.1-alpine
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
