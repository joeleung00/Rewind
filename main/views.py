from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import SigninForm,  SearchForm, CardForm, YoutubeForm, DeckForm, AnswerForm
from .models import Card, Deck, Youtube
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse,  HttpResponseNotFound
import re
from datetime import datetime
from django.urls import resolve

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
	if request.method == 'POST':
		form = DeckForm(request.POST)
		if form.is_valid():
			deck_name = form.cleaned_data['deck_name']
			new_deck = Deck(deck_name = deck_name, user=user)
			new_deck.save()

	deck_list = user.deck_set.all()
	due_new_list = []
	for deck in deck_list:
		due_new_list.append(deck.get_due_new_num())
	zip_list = zip(deck_list, due_new_list)
	form = DeckForm()
	context = {'context': zip_list, "form": form}
	return render(request, 'main/home.html', context)


@login_required(login_url="/signin/")
def deck(request, pk):
	mydeck = Deck.objects.get(pk=pk)
	youtube_videos = mydeck.get_youtube_videos()

	return render(request, 'main/deck.html', {'context': youtube_videos, 'pk':pk})

@login_required(login_url="/signin/")
def video(request, pk):
	card_list = Youtube.objects.get(pk=pk).card_set.all()

	return render(request, 'main/video.html', {'card_list': card_list, 'pk':pk})


@login_required(login_url="/signin/")
def card(request, pk):
	card = Card.objects.get(pk=pk)
	return render(request, 'main/card.html', {'card': card})



@login_required(login_url="/signin/")
def addcard(request):
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			url = form.cleaned_data["search_bar"]
			request.session['youtube_link'] = url
			return redirect(reverse('main:youtube_learning'))
	else:
		form = SearchForm()

	return render(request, 'main/addcard.html', {'form': form})


def get_embed_link(url):
	result = re.search("&list=", url)
	if result != None:
		pos = result.start()
		chopped_url = url[0:pos]
	else:
		chopped_url = url
	return re.sub("watch\?v=", "embed/", chopped_url), chopped_url

def init_card(card_form, youtube):
	value_dict = {'state': "N", 'finished_count': 0, 'due_time': datetime.now(), 'youtube': youtube}
	for key, value in card_form.cleaned_data.items():
		value_dict[key] = value
	value_dict['deck'] = Deck.objects.get(pk=value_dict['deck'][0])
	return Card(**value_dict)


@login_required(login_url="/signin/")
def youtube_learning(request):
	url = request.session.get("youtube_link")
	embed_link, url = get_embed_link(url)
	if request.method == "POST":
		card_form = CardForm(request.POST, user=request.user)
		youtube_form = YoutubeForm(request.POST)
		if youtube_form.is_valid():
			if card_form.is_valid():
				youtube = youtube_form.save()
				card = init_card(card_form, youtube)
				card.save()
				return JsonResponse({'success': True});
			else:
				## card_form error
				return JsonResponse({'success': False})
		else:
			#youtube_form error
			return JsonResponse({'success': False})
	else:
		youtube_form = YoutubeForm(initial={'youtube_link': url})
		card_form = CardForm(user=request.user)

	return render(request, 'main/youtube_learning.html', {'youtube_form': youtube_form, 'card_form': card_form, "embed_link": embed_link})


@login_required(login_url="/signin/")
def review(request, type, pk):
	if type == "deck":
		deck = Deck.objects.get(pk=pk)
		card_list = deck.card_set.all()
		path = deck.deck_name
		back_path = "/home/" + str(pk) + "/"
	elif type == "video":
		youtube = Youtube.objects.get(pk=pk)
		card_list = youtube.card_set.all()
		deck = card_list[0].deck
		path = deck.deck_name + "/" + youtube.youtube_title
		back_path = "/video/" + str(pk) + "/"
	else:
		return HttpResponseNotFound('<h1>Page not found</h1>')

	(review_num, learning_num, new_num) = Card.card_list_state_count(card_list)
	context = {'review_num': review_num, 'learning_num': learning_num, 'new_num': new_num, 'path': path, 'back_path': back_path}
	request.session['review_card_list'] = Card.review_card_id_list(card_list)
	print(request.session['review_card_list'])
	if review_num == 0 and learning_num == 0 and new_num == 0:
		context["congra_msg"] = "Congratulations! You have finished all cards."
	return render(request, 'main/review.html', context)



@login_required(login_url="/signin/")
def question_answer(request):

	if request.method == "POST":
		## change the review_card_list
		form = AnswerForm(request.POST)
		if form.is_valid():
			answer = form.cleaned_data['answer']
			question_id = form.cleaned_data['question_id']
			request.session['review_card_list'] = Card.modify_cards(answer, question_id, request.session['review_card_list'])
	###prepare next question
	current_url = request.get_full_path()
	back_url = re.sub("question_answer/", "", current_url)
	if "review_card_list" in request.session:
		card_list = Card.get_card_list_by_id_list(request.session['review_card_list'])
		if card_list != None:
			card = Card.earliest_card(card_list)
			answers = (("<1m", "again"), ("<10m", "good"), ("3d", "easy"))
			youtube_link = Card.get_youtube_link_with_timestamp(card.youtube.youtube_link, card.youtube_timestamp)
			form = AnswerForm(initial={'question_id': card.id})
			context = {'card': card, 'back_url':back_url, 'answers': answers, "youtube_link":youtube_link, 'form': form}
			return render(request, 'main/question_answer.html', context)

	return redirect(back_url)


def signout(request):
	logout(request)
	return redirect(reverse('main:index'))
