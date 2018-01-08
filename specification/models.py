# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    NO_ROOM = 'nr'
    NO_GAME = 'ng'
    IN_GAME = 'ig'
    STATE_CHOICES = (
        (NO_ROOM, 'No-room'),
        (NO_GAME, 'No-game'),
        (IN_GAME, 'In-game'),
    )
    state = models.CharField(max_length=2,
                             choices=STATE_CHOICES,
                             default=NO_ROOM)
    points = models.IntegerField(default=0, blank=True)



class Room(models.Model):
    room_name = models.SlugField(unique=True)
    owner = models.OneToOneField(Player,on_delete=models.CASCADE)
    player = models.OneToOneField(Player,related_name='room',null=True)
    game = models.OneToOneField(Game, null=True)



class Game(models.Model):
    keyword = models.CharField(max_length=20)
    drawer = models.OneToOneField(Player,on_delete=models.CASCADE)
    guesser = models.OneToOneField(Player, on_delete=models.CASCADE)
    current_content = models.TextField(null=True)


class DrawerMessage(models.Model):
    room = models.ForeignKey(Room, related_name='messages')

    canvas_content = models.TextField(null=True)
    guess_content = models.CharField(max_length=30,null=True)

    # When a palyer enters a room, a message that contains
    # his/her user info will be broadcast to all players.
    connect_user = models.OneToOneField(User, null=True)

    # When the owner of the room clicks "Start Game" button
    # a message that contains a start_flag will be broadcast
    # to all players.
    start_flag = models.CharField(max_length=1,null=True)




