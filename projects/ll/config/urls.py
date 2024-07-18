"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# config/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from todo import views

router = DefaultRouter()
router.register(r'todo-items', views.TodoItemViewSet)
router.register(r'todo-item-dates', views.TodoItemDateViewSet)
router.register(r'user-todo', views.UserProvidedTodoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),  # Django admin 페이지
    path('calendar/<str:item_name>/', views.CalendarReadAPIView.as_view(), name='calendar-read'),
    path('calendar/cnt/all', views.CalendarCountAPIView.as_view(), name='calendar-count'),
]

