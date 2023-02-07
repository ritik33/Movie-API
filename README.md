# Movie API

## Tech Stack

- Python
- Django
- Django Rest Framework

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

```
SECRET_KEY
EMAIL_BACKEND
EMAIL_HOST
EMAIL_USE_TLS
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
```

## Run Locally

Clone the project

```bash
git clone https://github.com/ritik33/Movie-API.git
```

Create a virtual environment

```bash
pip install virtualenv

virtualenv venv
```

Activate the virtual environment

```bash
venv\scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Apply migrations

```
python manage.py makemigrations

python manage.py migrate
```

Start the server

```bash
python manage.py runserver
```

> ⚠ Development server will start [here](http://127.0.0.1:8000/)
## Running Tests

To run tests, run the following command

```bash
python manage.py test
```


## Screenshots

![](https://user-images.githubusercontent.com/54118809/216813994-ce891b60-1870-4a40-b30a-dd5d5bab2acd.png)
![](https://user-images.githubusercontent.com/54118809/216814461-2f437405-afcd-4dfb-ab3a-7a250d00e48a.png)
