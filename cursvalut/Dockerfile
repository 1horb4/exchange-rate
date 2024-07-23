FROM python:3

RUN pip install -r requirements.txt

WORKDIR code
COPY . /code/
ADD .env.docker /code/.env

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
