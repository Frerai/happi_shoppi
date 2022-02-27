from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    # Overriding the ready method, to tell Django to use any custom made functions defined.
    def ready(self) -> None:
        import store.signals.handlers
