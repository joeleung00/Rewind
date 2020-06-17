from django import forms
from django.forms import ModelForm
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import Card, Youtube, Deck

class SigninForm(forms.Form):
    username = forms.CharField(max_length=50,
                            label="",
                            widget = forms.TextInput(attrs={'placeholder': 'Username',
                                                            'class': 'textbox'}))
    password = forms.CharField(max_length=50,
                            label="",
                            widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                            'class': 'textbox'}))

class SearchForm(forms.Form):
    search_bar = forms.URLField(label = "", widget = forms.TextInput(attrs={'placeholder': "www.youbute.com"}))

    def clean_search_bar(self):
        url = self.cleaned_data['search_bar']
        val = URLValidator()
        try:
            val(url)
        except:
            msg = "Webpage does not exist"
            self.add_error(field='search_bar', error=msg)
        return url


class CardForm(forms.Form):
    deck = forms.MultipleChoiceField()

    front_text = forms.CharField(max_length=500,
                                label='',
                                widget = forms.Textarea
    )
    back_text = forms.CharField(max_length=500,
                                label='',
                                widget = forms.Textarea
    )
    youtube_timestamp = forms.TimeField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs);
        if user:
            deck_list = user.deck_set.all()
            options = ( (deck.id, deck.deck_name) for deck in deck_list )
            self.fields['deck'].choices = options
class YoutubeForm(ModelForm):
    class Meta:
        model = Youtube
        fields = '__all__'

class DeckForm(forms.Form):
    deck_name = forms.CharField(max_length=30)


class AnswerForm(forms.Form):
    #options = (("<1m", "<1m"), ("<10m", "<10m"), ("3d", "3d"))
    answer = forms.CharField(max_length=10)
    question_id = forms.IntegerField()
