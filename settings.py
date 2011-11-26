import os
SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = (
    ('Your Name', 'your_email@example.com'),
)
EMAIL_FROM = 'no-reply@barboske.ru'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='localhost'
EMAIL_PORT=1025
MANAGERS = ADMINS
TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru_RU'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATICFILES_DIRS = (
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
SECRET_KEY = 'v4^zlka6u$fl=le%f%(tc*!2-5l75v+jl_cqy-0gboqq%ap-ca'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
ROOT_URLCONF = 'BarboskeRu.urls'
TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'taggit',
    'mptt',
    'pytils',
    'sorl.thumbnail',
    'endless_pagination',
    'shop',
    'staticpages',
)
THUMBNAIL_UPSCALE=False
THUMBNAIL_FORMAT='PNG'
THUMBNAIL_DEBUG=DEBUG
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'shop.context_processors.common_pieces',
)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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
AUTOSLUG_SLUGIFY_FUNCTION = 'pytils.translit.slugify'
try:
    from local_settings import *
except ImportError:
    pass
