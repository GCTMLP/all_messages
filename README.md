# All_Messages
Service that aggregates your messages in one place


# Online version
updating....

# About

This is service, that aggregates messages from your favourite messengers and social networks

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

3. Create database named "hasker"
```
sudo -u postgres psql
CREATE DATABASE all_messages;
CREATE USER myprojectuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE all_messages TO myprojectuser;
```

4. Write your mysql configuration at "config/settings.py"
examlpe:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
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
example configuration at "/etc/nginx/sites-enabled/hasker"
```
updating....
```

8. Import styles from ```https://github.com/GCTMLP/html_styles``` and add them to all_messages/static/assets
