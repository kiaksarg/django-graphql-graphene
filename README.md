# django-graphql-graphene
**Django + GraphQL example with graphene based on @saleor project**

## Install the dependencies:
```
python -m venv zagros-venv
zagros-venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Database Migration (PostgreSQL):
`Check or change the database name, user and password in settings.py file.`

1. Create database
2. Create database user
3. Make changes in settings.py file
4. Run migrate command:
```
python manage.py migrate
```

## Create superuser:
```
python manage.py createsuperuser
```

## Then execute:
```
python manage.py runserver
```

### Default url:
`http://127.0.0.1:8000`

### GraphQL Playground:
`http://127.0.0.1:8000/graphql/`
