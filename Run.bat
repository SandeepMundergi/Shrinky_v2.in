doskey st = python manage.py runserver 
doskey deploy = python manage.py runserver 192.168.11.222:8000
doskey migration = python manage.py makemigrations 
doskey migrate = python manage.py migrate 
doskey reset = python manage.py migrate --run-syncdb
doskey create = python manage.py createsuperuser