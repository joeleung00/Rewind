from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import SigninForm
from .models import Card, Deck, Youtube
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def index(request):
	return render(request, 'main/index.html', {})


def signin(request):
	if request.method == 'POST':
		form = SigninForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user:
				login(request, user)
				return redirect(reverse('main:home'))
			else:
				form.add_error(field=None, error="invalid password or username")
	else:
		form = SigninForm()
	return render(request, 'main/signin.html', {"form": form})


def signup(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)

		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect(reverse('main:home'))

	else:
		form = UserCreationForm()
	return render(request, 'main/signup.html', {"form": form})




@login_required(login_url="/signin/", redirect_field_name="home")
def home(request):
	user = request.user
	deck_list = user.deck_set.all()
	print(user)
	print(deck_list)
	due_new_list = []
	for deck in deck_list:
		due_new_list.append(deck.get_due_new_num())
	print(due_new_list)
	
	zip_list = zip(deck_list, due_new_list)

	context = {'context': zip_list}
	return render(request, 'main/home.html', context)


@login_required(login_url="/signin/")
def deck(request, pk):
	mydeck = Deck.objects.get(pk=pk)
	youtube_videos = mydeck.get_youtube_videos()

	return render(request, 'main/deck.html', {'context': youtube_videos})

@login_required(login_url="/signin/")
def video(request, pk):
	card_list = Youtube.objects.get(pk=pk).card_set.all()

	return render(request, 'main/video.html', {'card_list': card_list})


@login_required(login_url="/signin/")
def card(request, pk):
	card = Card.objects.get(pk=pk)
	return render(request, 'main/card.html', {'card': card})



@login_required(login_url="/signin/")
def addcard(request):
	return render(request, 'main/addcard.html', {})

def signout(request):
	logout(request)
	return redirect(reverse('main:index'))