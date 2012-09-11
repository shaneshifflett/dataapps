import os
from os import environ

env = lambda e, d: environ[e] if environ.has_key(e) else d# Django settings for bc_data_apps project.

PROJECT_ROOT = os.path.dirname(__file__)

DEBUG = not bool(env('DATAAPP_SITE_PROD', ''))
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Shane Shifflett', 'sshifflett@cironline.org'),
)

def map_path(directory_name):
    return os.path.join(os.path.dirname(__file__), directory_name).replace('\\', '/')

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME':'citizen',
        'USER':'root',
        'PASSWORD':'',
        'HOST':'localhost',
    },
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

MEDIA_ROOT          = map_path('public')
STATIC_ROOT         = map_path('public/static')
MEDIA_URL = SSL_MEDIA_URL = '/public/'
STATIC_URL = SSL_STATIC_URL = '%sstatic/' % MEDIA_URL

#DEPRECATED in Django 1.4; remove this when we update
ADMIN_MEDIA_PREFIX  = '%sadmin/' % STATIC_URL

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'j6%u&amp;*(3*hcf+5z!#)2-=cg^t5#^+t0*n2vp^nhb2=+^6no)19'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'bc_data_apps.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bc_data_apps.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    map_path('templates'),
    map_path('dataapps_templates'), 
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'bc_data_apps.apps.locations',
    'bc_data_apps.apps.schools',
    'bc_data_apps.apps.generics',
    'bc_data_apps.dataapps.bike_accidents',
    #'bc_data_apps.dataapps.immunizations',
    #'bc_data_apps.dataapps.census2010',
    #'bc_data_apps.dataapps.rankedvotes',
    #'bc_data_apps.dataapps.rankedchoice',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
