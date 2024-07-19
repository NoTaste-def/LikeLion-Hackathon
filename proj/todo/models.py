from django.db import models

class TodoItem(models.Model):
    # 고정된 항목을 정의합니다.
    ITEM_CHOICES = [
        ('water_8_cups', '물 8컵 마시기'),
        ('breakfast', '아침 식사하기'),
        ('salad', '샐러드 먹기'),
        ('nuts', '견과류 먹기'),
        ('fish', '생선 먹기'),
        ('vegetable_juice', '야채주스 마시기'),
        ('fermented_food', '발효식품 먹기'),
        ('protein', '단백질 먹기'),
        ('cardio', '유산소 운동하기'),
        ('strength_training', '근력 운동하기'),
        ('stretching', '스트레칭하기'),
        ('meditation', '명상하기'),
        ('therapeutic_bath', '목욕하기'),
        ('massage', '마사지 받기'),
        ('sleep_7_hours', '7시간 이상 잠자기'),
    ]

    # 각 항목의 이름
    name = models.CharField(max_length=255, choices=ITEM_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class TodoItemDate(models.Model):
    # TodoItem과 연결된 날짜 기록
    item = models.ForeignKey(TodoItem, related_name='dates', on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('item', 'date')

class UserProvidedTodo(models.Model):
    # 유저 완성되면 유저 외래키 기반으로 관리.
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_todo = models.TextField()  # models.ListField 대신 models.TextField 사용

    def __str__(self):
        return self.user_todo

    def get_user_todo_list(self):
        return self.user_todo.split(',')  # 쉼표를 기준으로 문자열을 리스트로 분할하여 반환
