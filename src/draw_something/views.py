# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from draw_something.models import *
from draw_something.forms import *
import json
from django.db import transaction
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from mimetypes import guess_type
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import Count, F



# Create your views here.
def log_in(request):
    if request.method == 'GET' and request.user.username:
        return redirect(reverse('home'))
    return login(request, template_name='draw_something/login.html')


def log_out(request):
    logout(request)
    return redirect(reverse('login'))


@transaction.atomic
def register(request):
    context = {}

    if request.method == 'GET':
        if request.user.username:
            return redirect(reverse('home'))
        context['register_form'] = RegisterForm()
        return render(request, 'draw_something/registration.html', context)

    form = RegisterForm(request.POST)
    context['register_form'] = form

    if not form.is_valid():
        return render(request, 'draw_something/registration.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'],
                                        is_active=False)
    new_user.set_password(form.cleaned_data['password'])
    new_user.save()
    player = Player(user=new_user, points=0, first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'])
    player.save()

    token = default_token_generator.make_token(new_user)
    email_body = """
    Welcome to Draw Something! Please click the link below to verify your email address and complete the registration of your account:

    http://%s%s
    """ % (request.get_host(),
           reverse('confirm-register', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="drawsomething.team317@gmail.com",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'draw_something/registration_email_send.html', context)


@transaction.atomic
def confirm_register(request, username, token):
    context = {}
    try:
        user_to_activate = User.objects.get(username=username)
    except ObjectDoesNotExist:
        context['user_error'] = 'Can not find user'
        return render(request, 'draw_something/registration_error.html', context)

    match = default_token_generator.check_token(user_to_activate, token)
    if match:
        user_to_activate.is_active = True
        user_to_activate.save()
        return redirect(reverse('home'))
    else:
        context['token_error'] = 'Token is invalid'
        return render(request, 'draw_something/registration_error.html', context)


@login_required
def home(request):
    context = {}
    context['user'] = request.user

    Player.objects.annotate(rank=Count('points'))
    yourself = get_object_or_404(Player,user=request.user)
    yourself.rank = Player.objects.filter(points__gt=yourself.points).count() + 1
    context['yourself'] = yourself
    context['room_full_message'] = False
    return render(request, 'draw_something/home.html', context)


@transaction.atomic
@login_required
def join_room(request,room_id):

    room = get_object_or_404(Room, id=room_id)
    num = room.players.all().count()
    player = get_object_or_404(Player, user = request.user)

    context = {}
    context['user'] = request.user
    Player.objects.annotate(rank=Count('points'))
    player.rank = Player.objects.filter(points__gt=player.points).count() + 1
    context['yourself'] = player
    context['room_full_message'] = True

    if num < 2:
        room.players.add(player)
        if num == 0: #if first palyer enters the room render drawer page
            return redirect(reverse('drawer', kwargs={'room_id': room_id}))
        if num == 1:
            if room.game: #if game have been created
                if room.game.drawer and room.game.guesser:
                    # when during a game, one player disconnects by accident, and the third player tries to join room
                    if room.game.drawer != player and room.game.guesser != player:
                        room.players.remove(player)
                        return render(request, 'draw_something/home.html', context)
                    # when during a game, drawer disconnects by accident and then tries to come back
                    if room.game.drawer == player:
                        return redirect(reverse('drawer',kwargs={'room_id': room_id}))
                    # when during a game, guesser disconnects by accident and then tries to come back
                    if room.game.guesser == player:
                        return redirect(reverse('guesser', kwargs={'room_id': room_id}))
                if not room.game.guesser: # if the game doesn't have guesser
                    if room.game.drawer != player:
                        return redirect(reverse('guesser', kwargs={'room_id': room_id}))
                    else: #user cannot play with himself
                        return redirect(reverse('home'))
                if not room.game.drawer: # if the game doesn't have drawer
                    if room.game.guesser != player:
                        return redirect(reverse('drawer', kwargs={'room_id': room_id}))
                    else: #user cannot play with himself
                        return redirect(reverse('home'))
            else: # when drawer is in room, but the game hasn't been created
                return redirect(reverse('guesser', kwargs={'room_id': room_id}))
    else: # if room is already full, redirect to home with 'room_full_message' True
        return render(request, 'draw_something/home.html', context)


@transaction.atomic
@login_required
def exit_room(request,room_id):
    context = {}
    room = get_object_or_404(Room, id=room_id)
    player = get_object_or_404(Player, user = request.user)
    if len(room.players.filter(user = request.user)) == 1:
        room.players.remove(player)
        # if during a game, one player exits the room normally, then game is deleted
        if room.game:
            if room.game.drawer == player or room.game.guesser == player:
                room.game.delete()
    return redirect(reverse('home'))


@transaction.atomic
@login_required
def drawer_page(request, room_id):
    context = {}
    context['room_id'] = room_id
    context['user'] = request.user

    room = get_object_or_404(Room, id=room_id)
    player = get_object_or_404(Player, user=request.user)
    if len(room.players.filter(user = request.user)) == 1:
        if room.game:
            if room.game.drawer:
                # if room already has another player as drawer, redirect to guesser page
                if room.game.drawer != Player.objects.get(user=request.user):
                    return redirect(reverse('guesser',kwargs={'room_id': room_id}))
                else:
                    return render(request, 'draw_something/drawer.html', context)
            else: # if the game doesn't have drawer, render drawer page
                return render(request, 'draw_something/drawer.html', context)
        return render(request, 'draw_something/drawer.html', context)
    else:  # a player try to reconnect to game using an url
        if room.game and room.game.drawer == player:
            room.players.add(player)
            return render(request, 'draw_something/drawer.html', context)
        # when a player is not in the room, and room doesn't have a game, then a player cannot get to the drawer page by url
        return redirect(reverse('home'))


@transaction.atomic
@login_required
def guesser_page(request, room_id):
    context = {}
    context['room_id'] = room_id
    context['user'] = request.user

    room = get_object_or_404(Room, id=room_id)
    player = get_object_or_404(Player, user=request.user)

    if len(room.players.filter(user=request.user)) == 1:
        if room.game:
            if room.game.guesser:
                # if room already has another player as guesser, redirect to drawer page
                if room.game.guesser != Player.objects.get(user=request.user):
                    return redirect(reverse('drawer', kwargs={'room_id': room_id}))
                else:
                    return render(request, 'draw_something/guesser.html', context)
            else: # if the game doesn't have guesser, render guesser page
                return render(request, 'draw_something/guesser.html', context)
        return render(request, 'draw_something/guesser.html', context)
    else: # a player try to reconnect to game using an url
        if room.game and room.game.guesser == player:
            room.players.add(player)
            return render(request, 'draw_something/guesser.html', context)
        # when a player is not in the room, and room doesn't have a game, then a player cannot get to the guesser page by url
        return redirect(reverse('home'))


@login_required
def profile_image(request,username):
    player = get_object_or_404(Player, user=User.objects.filter(username=username))
    if not player.profile_image:
        return HttpResponse("/draw_something/images/default.jpg")
    content_type = guess_type(player.profile_image.name)
    return HttpResponse(player.profile_image, content_type=content_type)


@login_required
@transaction.atomic
def get_changes(request, time="1970-01-01T00:00+00:00"):
    max_time = Room.get_max_time()
    try:
        rooms = Room.get_changes(time)
    except ValidationError:
        rooms = Room.get_changes("1970-01-01T00:00+00:00")

    context = {"max_time": max_time, "rooms": rooms}
    return render(request, 'draw_something/rooms.json', context, content_type='application/json')


@transaction.atomic
@login_required
def add_room(request):
    rooms = Room.objects.all().order_by('-create_time')

    messages = []

    if request.method == 'GET':
        context = {'rooms': rooms, 'messages': messages, 'user': request.user}
        context['room_form'] = RoomForm()
        return render(request, 'draw_something/home.html', context)

    new_room = Room()
    form = RoomForm(request.POST, instance = new_room)

    if not form.is_valid():
        messages.append("Form contained invalid data")
        return HttpResponse(form.errors.as_json(), content_type='application/json')

    form.save()
    messages.append('Added a new room.')
    return HttpResponse("")

@transaction.atomic
@login_required
def search(request,param,content):
    if request.method == 'GET':
        form = SearchForm({'search_param':param, 'search_content':content})
        context = {}
        message = "Sorry... No matched result has been found."
        context['user'] = request.user
        if not form.is_valid():
            rooms = Room.objects.all().order_by('-create_time')
            context['rooms'] = rooms
            context['form'] = form
            return render(request, "draw_something/search_result.html", context)

        param = form.cleaned_data['search_param']
        content = form.cleaned_data['search_content']
        #search by player
        if param == 'Player':
            player = Player.objects.filter(user=User.objects.filter(username=content))
            if player:
                room = Room.objects.filter(players__exact = player)
                if room:
                    context['rooms'] = room
                else: context["message"] = "Sorry... The player is not in any room."
            else:
                message = "Sorry... The player doesn't exist."
                context["message"] = message
        #search by level
        elif param == 'Level':
            if content.lower() == 'easy':
                room = Room.objects.filter(level='e')
            elif content.lower() == 'medium':
                room = Room.objects.filter(level='m')
            elif content.lower() == 'hard':
                room = Room.objects.filter(level='h')
            else:
                room = Room.objects.filter(level=content)

            if room:
                context['rooms'] = room
            else:
                context["message"] = message
        #serch by room name
        else:
            room = Room.objects.filter(room_name__contains = content)
            if room:
                context['rooms'] = room
            else:
                context["message"] = message
        return render(request,"draw_something/search_result.html",context)
    else:
        return redirect(reverse('home'))


@transaction.atomic
@login_required
def profile(request):
    context = {}
    player_to_edit = get_object_or_404(Player, user=request.user)
    if request.method == 'GET':
        context['player_form'] = PlayerForm(instance=player_to_edit)
        context['password_change_form'] = PasswordChangeForm(request.user)
        context['user'] = request.user
        return render(request, 'draw_something/profile.html', context)

    form = PlayerForm(request.POST, request.FILES, instance=player_to_edit)

    if not form.is_valid():
        context['player_form'] = form
        context['user'] = request.user
        return render(request, 'draw_something/profile.html', context)
    form.save()
    return redirect(reverse('home'))


@transaction.atomic
@login_required
def change_password(request):
    context = {}
    if request.method == 'GET':
        return redirect(reverse('edit-profile'))

    player_to_edit = get_object_or_404(Player, user=request.user)
    context['player_form'] = PlayerForm(instance=player_to_edit)

    form = PasswordChangeForm(request.user, request.POST)
    context['password_change_form'] = form
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # Important!
        messages.success(request, 'Your password was successfully updated!')
        return redirect(reverse('edit-profile'))
    else:
        context['password_change_form'] = form
        return render(request, 'draw_something/profile.html', context)


@transaction.atomic
@login_required
def get_ranks(request):
    Player.objects.annotate(rank=Count('points'))
    players = Player.objects.order_by('-points')[:50]
    for player in players:
        player.rank = Player.objects.filter(points__gt=player.points).count() + 1
    yourself = Player.objects.get(user=request.user)
    yourself.rank = Player.objects.filter(points__gt=yourself.points).count() + 1
    context = {"players": players, "yourself": yourself}
    return render(request, 'draw_something/rank.html', context)

