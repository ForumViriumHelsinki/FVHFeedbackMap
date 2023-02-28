# FVH Feedback Map
App for collecting and processing feedback related to geospatial points.

## REST V2

This is the new version of the REST API.
It is currently in development and is not yet ready for production use.

Original REST API is still available at `/rest/` and this version is mapped to `/rest/v2/`.

### TODO REST V2

- [x] Update all Python packages to latest versions
- [x] Add .pre-commit-config.yaml
- [x] Add ruff
- [x] Change database backend to PostGIS
- [x] Add GeometryField to MapDataPoint model
- [x] Add pagination
- [x] Add filtering
  - [x] Add filtering by `created_at`
  - [x] Add filtering by `updated_at`
  - [x] Add filtering by `bbox`
  - [x] Add filtering by `point` (distance)
- [x] Add ordering
  - [x] Add ordering by `created_at`
  - [x] Add ordering by `updated_at`
- [ ] Add swagger for v2
- [ ] Add tests for v2

## Installation

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
