# FVH Feedback Map
App for collecting and processing feedback related to geospatial points.

## Installation

### Using docker-compose (preferred way)

* Requires that docker is installed on the host system

In project root:

* ```sh configure_dev.sh``` or ```sh configure_prod.sh``` to ensure the correct configurations are in use for the 
  intended environment
* For prod setup, ```cp .env.prod.sample .env.prod``` and fill in the correct settings for your prod env
* ```docker-compose up -d``` should then launch the needed docker containers for the env
* To get started with development, ```docker exec -it fvhfeedbackmap-web-1 python manage.py createsuperuser``` should
  allow creation of a super user for the Django backend
* Navigating to http://localhost:8000/admin/feedback_map/tag/ should then allow logging in as the super user and
  creating tags (i.e. feedback categories)
* Once some tags have been created & published, they should show up in the react UI at http://127.0.0.1:3000/

### Installing natively

**Prerequisites**:
* Python 3.10+ with pip
* Node.js 13.3 with ./node_modules/.bin in the PATH
* Postgres with a db available as configured in django_server/feedback_map_config/settings.py

In project root:

```
sudo pip install pipenv
cd django_server
pipenv install
pipenv shell
python manage.py migrate
python manage.py createsuperuser
<Configure user to your satisfaction>
python manage.py runserver
<Verify that you can login at 127.0.0.1:8000/admin/ >
```

In react_ui:

```
npm install yarn
yarn install
yarn start
<Verify that you can login to React UI at 127.0.0.1:3000 using your superuser or courier user credentials>
```
