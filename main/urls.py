from django.urls import path, re_path

from . import views

app_name = 'main'
urlpatterns = [
    path('home/<int:pk>/', views.deck, name='deck'),
    path('home/', views.home, name='home'),
    path('video/<int:pk>/', views.video, name='video'),
    path('card/<int:pk>/', views.card, name='card'),
    path('', views.index, name='index'),
    path('youtube_learning/', views.youtube_learning, name='youtube_learning'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path("addcard/", views.addcard, name="addcard"),
    path(r'review/<str:type>/<int:pk>/', views.review, name="review"),
    re_path(r'review/deck|video/[0-9]+/question_answer/$', views.question_answer, name="question_answer"),
]
