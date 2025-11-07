#configures app and its metadata
from django.apps import AppConfig

#registers app with Django (ref in settings.py)
class CinemaConfig(AppConfig):
    #this is the metadata for the app
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cinema'
    #can add more app-specific configurations here
