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
```

### run the server
```sh
$ python manage.py runserver
```
### Save and restore your data
For icons:
save all your icons
```sh
$ python manage.py dumpdata group.Icon --output seed/icon.json
```
Load icons
```sh
$ python manage.py loaddata seed/icon.json
```