This is the server part of the resource, which allows you to receive data about tenders using the API located on the Prozorro resource.

Install requirements:
```shell
pip install requirements.txt
```
Run migrations:
```shell
python manage.py migrate
```
Run server:
```shell
python manage.py runserver
```

Or you can use docker's commands:

Build:
```shell
docker compose build
```
Run:
```shell
docker compose up
```