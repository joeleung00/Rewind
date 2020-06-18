from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone
NEW = "N"
REVIEW = "R"
LEARNING = "L"
FINISHED = "F"

class Deck(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	deck_name = models.CharField(max_length=30)

	def get_due_new_num(self):
		card_list = self.card_set.all()
		(review, learning, new) = Card.card_list_state_count(card_list)
		return review + learning, new


	def get_youtube_videos(self):
		card_list = self.card_set.all()
		youtube_id_set = set()
		for card in card_list:
			youtube_id_set.add(card.youtube.id)

		youtube_list = Youtube.objects.filter(pk__in=list(youtube_id_set))

		videos = []
		for youtube in youtube_list:
			card_list_by_youtube = youtube.card_set.all()
			(review, learning, new) = Card.card_list_state_count(card_list_by_youtube)
			videos.append([youtube, review + learning, new])
		return videos


	def __str__(self):
		return self.deck_name

class Youtube(models.Model):
	deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
	youtube_link = models.URLField()
	youtube_title = models.CharField(max_length=150)

	def __str__(self):
		return self.youtube_title

class Card(models.Model):
	STATE = [(NEW, "NEW"), (REVIEW, "REVIEW"), (LEARNING, "LEARNING"), (FINISHED, "FINISHED")]

	deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
	youtube = models.ForeignKey(Youtube, on_delete=models.CASCADE, null=True)
	front_text = models.TextField(max_length=500)
	back_text = models.TextField(max_length=500)
	front_img = models.ImageField(blank=True)
	back_img = models.ImageField(blank=True)
	state = models.CharField(max_length=20, choices=STATE, default=NEW)
	finished_count = models.PositiveSmallIntegerField()
	youtube_timestamp = models.TimeField()
	due_time = models.DateTimeField()


	def review_card_id_list(card_list):
		## dont keep card which is finished
		id_list = []
		for card in card_list:
			if card.state != "F":
				id_list.append(str(card.id))
		return ",".join(id_list)

	def get_card_list_by_id_list(id_list):
		if id_list == '':
			return None
		id_list = id_list.split(',')
		id_list = list(map(lambda x: int(x), id_list))
		return Card.objects.filter(pk__in=id_list)

	def earliest_card(card_list):
		min_card = card_list[0]
		for card in card_list:
			if card.due_time < min_card.due_time:
				min_card = card
		return min_card

	def get_youtube_link_with_timestamp(url, timestamp):
		minutes = timestamp.hour * 60 + timestamp.minute
		sec = timestamp.second
		suffix = "&t={}m{}s".format(minutes, sec)
		return url + suffix


	def card_list_state_count(card_list):
		count = [0, 0, 0] # REWVIEW, LEARNING, NEW
		for card in card_list:
			if card.state == NEW:
				count[2] += 1
			elif card.state == LEARNING:
				count[1] += 1
			elif card.state == REVIEW:
				count[0] += 1
		return count

	def remove_value_from_id_list(id, id_list):
		id_list = id_list.split(",")
		if str(id) in id_list:
			id_list.remove(str(id))
		return ",".join(id_list)

	def modify_cards(answer, question_id, id_list):
		card = Card.objects.get(pk=question_id)
		if answer == "<1m":
			card.due_time = timezone.now() + timedelta(minutes=1)
			card.state = "L"
		elif answer == "<10m":
			card.due_time = timezone.now() + timedelta(minutes=10)
			card.state = "L"
		elif answer == "3d":
			card.due_time = timezone.now() + timedelta(days=3)
			card.state = "F"
			id_list = Card.remove_value_from_id_list(question_id, id_list)
		card.save()
		return id_list
