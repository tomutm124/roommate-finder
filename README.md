# ust-roomies
A Django web application for students at HKUST to find roommates with similar lifestyle and routines. This application is a personal project and is not affiliated with HKUST.

< screenshots here >


## Running in Prod
1. Create roomies/secrets.py with DJANGO_SECRET_KEY and SEND_GRID_API_KEY
2. Go to roomies/settings.py to:
   1. update DEBUG to False
   2. set CSRF_COOKIE_SECURE to True (uncomment the line near the bottom)
   3. set SESSION_COOKIE_SECURE to True (uncomment the line near the bottom)
3. Consider disabling the route to admin page
4. Consider setting up a more prod-ready database and config the connection in roomies/settings.py
5. Host static files elsewhere to reduce server load
  
