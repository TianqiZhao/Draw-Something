from django import forms

from django.contrib.auth.models import User
from draw_something.models import *
from django.core.validators import RegexValidator
from hashlib import sha256
from draw_something.models import *

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30,
                                 validators = [RegexValidator(regex='^[A-Za-z]+$', message="First name can only contain characters.")])
    last_name = forms.CharField(max_length=30,
                                 validators = [RegexValidator(regex='^[A-Za-z]+$', message="Last name can only contain characters.")])
    email = forms.CharField(max_length=100)
    password = forms.CharField(max_length=200,
                               label='Password',
                               widget=forms.PasswordInput())
    confirm = forms.CharField(max_length=200,
                              label='Confirm password',
                              widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        username = cleaned_data.get('username')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        return cleaned_data


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude  = {'players', 'create_time', 'game',}


class SearchForm(forms.Form):
    search_param = forms.CharField(max_length=50)
    search_content = forms.CharField(max_length=50)

    # validate that parameter can only be player, level or room name
    def clean_search_param(self):
        search_param = self.cleaned_data.get('search_param')
        if search_param == 'Player' or search_param == 'Level' or search_param == 'Room name':
            return search_param
        else:
            raise forms.ValidationError('Select the search parameter. It can only be Player, Level or Room name.')

    def clean_search_content(self):
        search_param = self.cleaned_data.get('search_param')
        search_content = self.cleaned_data.get('search_content')
        # if parameter is level, validate that content can only be easy, medium or hard
        if search_content == '/':
            raise forms.ValidationError('Please enter search content.')
        if search_param == 'Level':
            if search_content.lower() == 'easy' or search_content.lower() == 'medium' or search_content.lower() == 'hard':
                return search_content
            else:
                raise forms.ValidationError('Level only allows easy, medium or hard.')
        else:
            return search_content



class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        exclude = ('user','points',)
        widgets = {'profile_image' : forms.FileInput(),}
                    # 'short_bio' : forms.Textarea(attrs={'rows':5})}

class GuessForm(forms.Form):
    guess_word = forms.CharField(max_length=30)

