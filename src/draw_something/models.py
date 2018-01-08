# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models import Max
from django.template.loader import render_to_string

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30,
                                  validators=[RegexValidator(regex='^[A-Za-z]+$',
                                                             message="First name can only contain characters.")])
    last_name = models.CharField(max_length=30,
                                 validators=[RegexValidator(regex='^[A-Za-z]+$',
                                                            message="Last name can only contain characters.")])
    # NO_ROOM = 'nr'
    # NO_GAME = 'ng'
    # IN_GAME = 'ig'
    # STATE_CHOICES = (
    #     (NO_ROOM, 'No-room'),
    #     (NO_GAME, 'No-game'),
    #     (IN_GAME, 'In-game'),
    # )
    # state = models.CharField(max_length=2,
    #                          choices=STATE_CHOICES,
    #                          default=NO_ROOM)
    points = models.IntegerField(default=0, blank=True)
    profile_image = models.ImageField(upload_to="user_profile_images", blank=True, default='user_profile_images/default.jpg')

    def __unicode__(self):
        return "%s: %s %s" % (self.user.username, self.user.first_name, self.user.last_name)
    def __str__(self):
        return self.__unicode__()


class Game(models.Model):
    keyword = models.CharField(max_length=20)
    drawer = models.ForeignKey(Player,null=True, on_delete=models.SET_NULL,
                                  related_name='drawer')
    guesser = models.ForeignKey(Player,null=True, on_delete=models.SET_NULL,
                                   related_name='guesser')

    current_content = models.TextField(null=True)
    start = models.BooleanField(default=False)



class Room(models.Model):
    room_name = models.SlugField(unique=True,max_length=15)
    players = models.ManyToManyField(Player, related_name='players')
    game = models.ForeignKey(Game, null=True, on_delete=models.SET_NULL)
    create_time = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)

    LEVEL_CHOICES = (
        ('e','Easy'),
        ('m','Medium'),
        ('h','Hard'),
    )
    level = models.CharField(max_length=1,
                             choices=LEVEL_CHOICES,
                             default='e')

    def __unicode__(self):
        return self.room_name

    # Returns all recent additions to the home page.
    @staticmethod
    def get_changes(timestamp="1970-01-01T00:00+00:00"):
        #t = datetime.datetime.fromtimestamp(timestamp / 1000.0)
        return Room.objects.filter(create_time__gt=timestamp).distinct().order_by('create_time')

    @staticmethod
    def get_max_time():
        return Room.objects.all().aggregate(Max('last_changed'))['last_changed__max'] or "1970-01-01T00:00+00:00"

    @property
    def html(self):
        return render_to_string("draw_something/room.html",
                                {"room": self}).replace("\n", "");






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




