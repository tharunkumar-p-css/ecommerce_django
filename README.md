# ecommerce-django

1. Create and activate venv
   python -m venv venv
   # mac/linux: source venv/bin/activate
   # windows: venv\Scripts\activate

2. Install deps
   pip install -r requirements.txt

3. Run project
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver

4. Open http://127.0.0.1:8000/

Notes:
- Upload product images in Django admin or place files in media/products/ when testing.
- DEBUG=True recommended while developing.