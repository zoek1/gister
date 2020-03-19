# Gister

**DEMO**: 
[Video demo](https://www.dropbox.com/s/350qhtkitbnb3o6/2020-03-19%2001-33-05.flv?dl=0) |
[Project demo](https://gister.gordian.dev)


Fusion between Gist and Pastebin with a Hipster touch. 

Pastebin ❤️ Gist = Gister

![Gister Logo](dashboard/static/favicon/android-icon-144x144.png)

## Setup

Requires docker-compose installed before start.

1. Create virtual enviroment and install dependencies
```shell
$ python3 -m venv --prompt gister  .env
$ pip install -r requirements.txt
```
2. Create the DB
```shell
$ docker-compose up -d
```
3. Run migrations and start the server
```shell
$ python manage.py migrate
$ python manage.py runserver
```

## Flow 

### Create gist
![](/screenshot/create_gist.png)

### Get a gist
All files are stored and downloaded from the skynet, no server is needed to access the files.
![](/screenshot/details.png)

### View all gists
![](/screenshot/all.png)

## LICENSE
See [LICENSE](/LICENSE)
