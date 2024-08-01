from django.apps import AppConfig

class SignalConfig(AppConfig):
    name = 'todo'
    def ready(self):
        import todo.signals  # 신호 처리기 모듈을 가져옵니다.

# class TodoConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'todo'

