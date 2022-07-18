# Django xero Intergration:
Integrating xero with Django  https://github.com/xeroAPI/xero-python 

# Create xero app:
Create a free xero developer account or sign in at https://developer.xero.com/app/manage/ \
Create an xero app\
Get your Client-ID & Client-Secret\

# Create Virtual Environment:
python3 -m venv env\
source bin/activate\
pip install -r requirements.txt\
python manage.py runserver\
python manage.py migrate\


# Connection:
http://localhost:8000/login\
Login to your xero account and authorise your app\
You will be redirected back to your app\
Select what report you would like to access\
Your data will be fetched in the terminal\

# Upcoming features
Display data in templates\
Refresh tokens\