from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # OLD (Error): name = 'core'
    # NEW (Correct):
    name = 'apps.core'