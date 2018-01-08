from channels import Group, channel_layers
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
from django.db import transaction
import logging, random
from .models import *
from django.shortcuts import get_object_or_404
import json
from draw_something.forms import *

log = logging.getLogger(__name__)

# Connected to websocket.connect
@transaction.atomic
@channel_session_user_from_http
def guesser_connect(message,room_id):
    room = get_object_or_404(Room, id=room_id)
    player = get_object_or_404(Player, user=message.user)
    #room.players.add(player)
    if len(room.players.filter(user = message.user)) == 0:
        room.players.add(player)

    Group('game-' + room_id, channel_layer=message.channel_layer).add(message.reply_channel)
    message.channel_session['room'] = room.id
    message.reply_channel.send({"accept": True})

    if room.game:
        if room.game.guesser and room.game.guesser.user != message.user:
            Group("game-%s" % message.channel_session['room']).send({
                "text": json.dumps({"notify": "Guesser exists", "username": message.user.username}),
            })
        else:
            room.game.guesser = player
            room.game.save()
            room.save()
    else:
        if room.level == 'm':
            word_library = open("draw_something/static/draw_something/wordLibrary_medium.txt", "r")
        elif room.level == 'h':
            word_library = open("draw_something/static/draw_something/wordLibrary_hard.txt", "r")
        else:
            word_library = open("draw_something/static/draw_something/wordLibrary.txt", "r")
        lines = word_library.read().split(',')
        word_library.close()
        word = random.choice(lines).strip()
        game = Game.objects.create(keyword=word, guesser=player)
        game.save()
        room.game = game
        room.save()
        Group("game-%s" % message.channel_session['room']).send({
            "text": '{"notify":"Guesser connected"}',
        })

    if room.game.drawer and room.game.guesser:
        if not room.game.start:
            Group("game-%s" % message.channel_session['room']).send({
                "text": json.dumps({"notify":"ready to start",
                                    "keyword":room.game.keyword,
                                    "drawer":room.game.drawer.user.username,
                                    "guesser":room.game.guesser.user.username,
                                    "level":room.level}),
            })
            room.game.start = True
            room.game.save()
            room.save()
        else:
            Group("game-%s" % message.channel_session['room']).send({
                "text": json.dumps(
                    {"notify": "guesser reconnect"}),
            })


# Connected to websocket.connect
@transaction.atomic
@channel_session_user_from_http
def drawer_connect(message,room_id):
    room = get_object_or_404(Room, id=room_id)
    player = get_object_or_404(Player, user=message.user)
    #room.players.add(player)
    if len(room.players.filter(user=message.user)) == 0:
        room.players.add(player)

    Group('game-' + room_id, channel_layer=message.channel_layer).add(message.reply_channel)
    message.channel_session['room'] = room.id
    message.reply_channel.send({"accept": True})

    if room.game:
        if room.game.drawer and room.game.drawer.user != message.user:
            Group("game-%s" % message.channel_session['room']).send({
                "text": json.dumps({"notify": "Drawer exists", "username": message.user.username}),
            })
        else:
            room.game.drawer = player
            room.game.save()
            room.save()
    else:
        if room.level == 'm':
            word_library = open("draw_something/static/draw_something/wordLibrary_medium.txt", "r")
        elif room.level == 'h':
            word_library = open("draw_something/static/draw_something/wordLibrary_hard.txt", "r")
        else:
            word_library = open("draw_something/static/draw_something/wordLibrary.txt", "r")
        lines = word_library.read().split(',')
        word_library.close()
        word = random.choice(lines).strip()
        game = Game.objects.create(keyword=word, drawer=player)
        game.save()
        room.game = game
        room.save()
        Group("game-%s" % message.channel_session['room']).send({
            "text": '{"notify":"Drawer connected"}',
        })

    if room.game.drawer and room.game.guesser:
        if not room.game.start:
            Group("game-%s" % message.channel_session['room']).send({
                "text": json.dumps({"notify":"ready to start",
                                    "keyword":room.game.keyword,
                                    "drawer":room.game.drawer.user.username,
                                    "guesser":room.game.guesser.user.username,
                                    "level":room.level}),
            })
            room.game.start = True
            room.game.save()
            room.save()
        else:
            Group("game-%s" % message.channel_session['room']).send({
                "text": json.dumps(
                    {"notify": "drawer reconnect"}),
            })



@transaction.atomic
@channel_session_user
def drawer_canvas(message, room_id):
    room = get_object_or_404(Room, id=room_id)
    data = json.loads(message.content['text'])
    if set(data.keys()) == set([u'time_notify']):
        if room.game:
            room.game.delete()
            Group("game-%s" % message.channel_session['room']).send({
                "text": '{"notify":"time runs out and game over"}',
            })
            return
    if set(data.keys()) == set([u'exit_notify']):
        Group("game-%s" % message.channel_session['room']).send({
            "text": '{"notify":"drawer exits normally"}',
        })
        return
    if set(data.keys()) == set([u'time_remain']):
        if room.game:
            Group("game-%s" % message.channel_session['room']).send({
                "text": json.dumps(
                        {"notify":"time remain from drawer","time_remain_drawer": data['time_remain'],"drawer":room.game.drawer.user.username, "guesser":room.game.guesser.user.username}),
            })
        return
    Group("game-%s" % message.channel_session['room']).send({
        "text": message.content['text'],
    })
    return


@transaction.atomic
@channel_session_user
def guesser_keyword(message,room_id):
    room = get_object_or_404(Room, id=room_id)
    answer = room.game.keyword
    data = json.loads(message['text'])
    if set(data.keys()) == set([u'time_notify']):
        # need to judge if the game exists
        if room.game:
            room.game.delete()
        Group("game-%s" % message.channel_session['room']).send({
            "text": '{"notify":"time runs out and game over"}',
        })
        return
    if set(data.keys()) == set([u'exit_notify']):
        Group("game-%s" % message.channel_session['room']).send({
            "text": '{"notify":"guesser exits normally"}',
        })
        return
    if set(data.keys()) == set([u'time_remain', u'canvas_content']):
        if room.game:
            Group("game-%s" % message.channel_session['room']).send({
                "text": json.dumps(
                        {"notify":"time remain from guesser", "time_remain_guesser":data['time_remain'], "canvas_content":data['canvas_content'],
                        "keyword":room.game.keyword, "drawer":room.game.drawer.user.username, "guesser":room.game.guesser.user.username}),
            })
        return
    form = GuessForm({'guess_word': data["guess"]})
    if not form.is_valid():
        return
    if (data["guess"]):
        if data["guess"].lower() == answer.lower():
            if room.level == 'm':
                Group("game-%s" % message.channel_session['room']).send({
                    "text": json.dumps({"notify": "guess correctly", "points": '4',
                                        "answer": data["guess"]}),
                })
                point = 4
            elif room.level == 'h':
                Group("game-%s" % message.channel_session['room']).send({
                    "text": json.dumps({"notify": "guess correctly", "points": '5',
                                        "answer": data["guess"]}),
                })
                point = 5
            else:
                Group("game-%s" % message.channel_session['room']).send({
                    "text": json.dumps({"notify": "guess correctly", "points": '3',
                                        "answer": data["guess"]}),
                })
                point = 3
            for player in room.players.all():
                player.points = player.points + point
                player.save()
            if room.game:
                room.game.delete()
        else:
            Group("game-%s" % message.channel_session['room']).send({
                "text": message['text'],
             })

# Connected to websocket.disconnect
@transaction.atomic
@channel_session_user
def ws_disconnect(message):
    room_id = message.channel_session['room']
    room = get_object_or_404(Room, id=room_id)
    player = get_object_or_404(Player, user=message.user)
    if len(room.players.filter(user=message.user)) == 1:
        room.players.remove(player)

    if room.game:
        if len(room.players.all()) == 0:
            room.game.delete()

    Group("game-%s" % message.channel_session['room']).discard(message.reply_channel)