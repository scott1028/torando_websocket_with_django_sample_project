# coding: utf-8
# 只需要 Django Model 的 settings.py 配置表

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': './db.sqlite3',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# # Make this unique, and don't share it with anybody.
SECRET_KEY = 'c94coq2ly9*y*j@-l!a)eeubf)17i0yy)=lrkm-h#da@!v96ot'

INSTALLED_APPS = (
    'queue_inline',
    'store'
)
