release: python manage.py migrate && python crear_admin.py
web: gunicorn appweb.wsgi --log-file -
