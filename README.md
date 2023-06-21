# All_Messages
Service that aggregates your messages in one place


# Online version
updating....

# About

This is service, that aggregates messages from your favourite messengers and social networks

How does it works

Technical side: link to presentation

1. You registrate on All_Messages
2. Setup your personal data
3. Setup connection to API 
4. Add or export contacts
5. Enjoy Messaging different messengers and social networks in one place

Technology stack is:
  - Python3
  - Nginx
  - uWSGI
  - ASGI
  - asyncio
  - threading
  - Django
    - Channels
  - Vue.js
  - PostgreSQL
  - Smarty templates
  - Telethon

# How to deploy

Deploy by docker-compose 
```
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear 
```

Deploy by yourself

1. Clone the repository
```
git clone https://github.com/GCTMLP/all_messages.git
```
```
cd all_messages
```

2. Install requirements
```
poetry update
```

3. Create database named "all_messages"
```
sudo -u postgres psql
CREATE DATABASE all_messages;
CREATE USER myprojectuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE all_messages TO myprojectuser;
```

4. Write your postgresql configuration at "config/settings.py"
examlpe:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'all_messages',
        'USER': 'myprojectuser',
        'PASSWORD': 'password',
        'HOST': 'yourhost' (ex: localhost),
        'PORT': 'yourport',
    }
}
```

5. Apply migrations
```
python3 manage.py makemigration
python3 manage.py migrate
```

6. Add your server name at "config/settings.py"
example
```
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
```

7. Set up nginx
example configuration at "/etc/nginx/sites-enabled/all_messages"
```

server {

    listen 443 ssl;
    ssl_certificate /etc/ssl/yourcrt.crt;
    ssl_certificate_key /etc/ssl/yourkey.key;
    server_name yourservername;

    location / {
       uwsgi_pass unix:///run/uwsgi/app/all_messages/socket;
       include uwsgi_params;
       uwsgi_read_timeout 300s;
       client_max_body_size 32m;
    }

    location /static/ {
        alias /all_message_project/all_message/static/;
    }
    
    location /media/ {
        alias /all_message_project/all_message/media/;
    }

}
```

8. Import styles from ```https://github.com/GCTMLP/html_styles``` and add them to all_messages/static/assets
