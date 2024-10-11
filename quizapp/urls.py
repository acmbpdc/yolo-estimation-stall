from django.contrib import admin
from django.urls import path
from quizapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('welcome/', views.welcome_view, name='welcome'),
    path('question1/', views.question_one_view, name='question_one'),
    path('question2/', views.question_two_view, name='question_two'),
]
