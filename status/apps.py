from django.apps import AppConfig


class StatusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'status'

    def ready(self):
        import status.signals  # signals.py를 불러와 시그널 연결
