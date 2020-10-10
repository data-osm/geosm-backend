### Create the virtual env and install requirements
```sh
$ python3 -m venv dataosmenv
$ source dataosmenv/bin/activate
$ python -m pip install --upgrade pip
$ pip install -r requirements.txt
```
#### Migrate the databse 
```sh
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```