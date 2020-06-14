from django.db import models
from django.contrib.auth.models import User

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
	youtube_link = models.URLField()
	youtube_title = models.CharField(max_length=150)

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
				



