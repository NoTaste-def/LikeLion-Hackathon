# Generated by Django 5.0.7 on 2024-07-23 15:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TodoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('water_8_cups', '물 8컵 마시기'), ('breakfast', '아침 식사하기'), ('salad', '샐러드 먹기'), ('nuts', '견과류 먹기'), ('fish', '생선 먹기'), ('vegetable_juice', '야채주스 마시기'), ('fermented_food', '발효식품 먹기'), ('protein', '단백질 먹기'), ('cardio', '유산소 운동하기'), ('strength_training', '근력 운동하기'), ('stretching', '스트레칭하기'), ('meditation', '명상하기'), ('therapeutic_bath', '목욕하기'), ('massage', '마사지 받기'), ('sleep_7_hours', '7시간 이상 잠자기')], max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_email', models.EmailField(max_length=64, unique=True)),
                ('nickname', models.CharField(max_length=64)),
                ('level', models.IntegerField(default=1)),
                ('badges', models.CharField(blank=True, max_length=64, null=True)),
                ('title', models.CharField(blank=True, max_length=64, null=True)),
                ('login_at', models.DateField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='custom_user_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_set', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '사용자 id',
                'verbose_name_plural': '사용자',
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='UserProvidedTodo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_todo', models.JSONField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TodoItemDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dates', to='todo.todoitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'item', 'date')},
            },
        ),
    ]