from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('home/<int:pk>/', views.deck, name='deck'),
    path('home/', views.home, name='home'),
    path('video/<int:pk>/', views.video, name='video'),
    path('card/<int:pk>/', views.card, name='card'),
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path("addcard/", views.addcard, name="addcard"),
]
