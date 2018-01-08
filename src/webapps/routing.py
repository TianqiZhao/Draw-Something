from channels.routing import route
from draw_something.consumers import *
channel_routing = [
    route("websocket.connect", guesser_connect, path=r"^/game/draw-something/guesser-page/(?P<room_id>[\w\W]+)$"),
    route("websocket.connect", drawer_connect, path=r"^/game/draw-something/drawer-page/(?P<room_id>[\w\W]+)$"),
    route("websocket.receive", drawer_canvas, path=r"^/game/draw-something/drawer-page/(?P<room_id>[\w\W]+)$"),

    route("websocket.disconnect", ws_disconnect),
    route("websocket.receive", guesser_keyword, path=r"^/game/draw-something/guesser-page/(?P<room_id>[\w\W]+)$"),
]
