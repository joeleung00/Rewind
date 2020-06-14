from django import forms


class SigninForm(forms.Form):
    username = forms.CharField(max_length=50,
                            label="",
                            widget = forms.TextInput(attrs={'placeholder': 'Username',
                                                            'class': 'textbox'}))
    password = forms.CharField(max_length=50,
                            label="",
                            widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                            'class': 'textbox'}))
