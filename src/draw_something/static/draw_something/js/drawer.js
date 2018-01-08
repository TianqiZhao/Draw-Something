var in_game = false;
var gamesock;
function loading () {
	$(".overlay").css({'display':'block','opacity':'0.8'});
	$(".showbox").stop(true).animate({'margin-top':'300px','opacity':'1'},200);
	console.log("loading.");
}

function loadingDone () {
    $(".showbox").remove();
    $(".overlay").css({'display':'none','opacity':'0'});
	console.log("loading done.");
}

function time_count() {
console.log("in time_count");
limit = new Date();
limit.setSeconds(limit.getSeconds() + 15.5);
$("#time-limit").countdown({until: limit,
                            onExpiry: function() {
                                //if time expires exit the room
                                var room_id = $("#mycanvas").attr("name");
                                window.location.href ="/draw-something/exit-room/" + room_id;
                            },
                            format: 'S',
                            compact: true,
                            description: ''});
}

function exit_room() {
     console.log("in exit");
     room_id = $("#mycanvas").attr("name");
     window.location.href ="/draw-something/exit-room/" + room_id;
}

function dialog (flag,points) {
     if (flag == "GUESS_CORRECT") {
        loadingDone();
        var dialog_content= "<div id='AjaxLoading' class='showbox'>" +
            "<div class='loadingWord'>Nice draw !</div> <br>" +
            "<div class='loadingWord'>Congraduations, you win " + points + " points!</div> <br>" +
	        "<div class='loadingWord'>Start a new game ? <span id='time-limit'></span> </div> <br>" +
	        "<div class='col-md-6 column'> <div class='col-md-6 column'></div><button type='submit' class='btn btn-success btn-lg' id='game-btn'>Yes</button></div>" +
	        "<div class='col-md-6 column'> <div class='col-md-2 column'></div><button type='submit' class='btn btn-warning btn-lg' id='home-btn'>No</button></div>" +
            "</div>" ;
    }
    if (flag == "TIME_RUNS_OUT") {
        loadingDone();
        var dialog_content= "<div id='AjaxLoading' class='showbox'>" +
            "<div class='loadingWord'>Sorry, you failed...</div> <br>" +
	        "<div class='loadingWord'>Start a new game ?&nbsp<span id='time-limit'></span> </div> <br>" +
	        "<div class='col-md-6 column'> <div class='col-md-6 column'></div><button type='submit' class='btn btn-success btn-lg' id='game-btn'>Yes</button></div>" +
	        "<div class='col-md-6 column'> <div class='col-md-2 column'></div><button type='submit' class='btn btn-warning btn-lg' id='home-btn'>No</button></div>" +
            "</div>" ;

    }
    if (flag == "GUESSER_EXIT") {
        loadingDone();
        var dialog_content= "<div id='AjaxLoading' class='showbox'>" +
            "<div class='column loadingWord'>Oh no! The other player abandoned you :(</div> <br>" +
	        "<div class='col-md-12 column'><div class='col-md-5 column'></div><button type='submit' class='btn btn-warning btn-lg' id='home-btn'>Go back to home</button></div>" +
            "</div>" ;
    }
     if (flag == "QUIT_GAME") {
        loadingDone();
        var dialog_content= "<div id='AjaxLoading' class='showbox'>" +
            "<div class='column loadingWord'>Are you sure you want to quit the game?</div> <br>" +
	        "<div class='col-md-6 column'> <div class='col-md-4 column'></div><button type='submit' class='btn btn-success btn-lg' id='quit-btn'>Yes</button></div>" +
	        "<div class='col-md-6 column'> <div class='col-md-2 column'></div><button type='submit' class='btn btn-warning btn-lg' id='continue-btn'>No</button></div>" +
            "</div>" ;
    }
    $(".overlay").parent().append(dialog_content);

    if (flag ==  "TIME_RUNS_OUT" || flag == "GUESS_CORRECT") {
        time_count();
    }
    $("#game-btn").click(function() {
        room_id = $("#mycanvas").attr("name");
        window.location.href ="/draw-something/guesser-page/" + room_id;
    });
    $("#home-btn").click(exit_room);
    $("#continue-btn").click(function() {
        loadingDone();
    });
    $("#quit-btn").click(function() {
        if (in_game) {
            var message = {
                exit_notify : "drawer exits normally",
            }
            gamesock.send(JSON.stringify(message));
        }
         window.location.href ="/draw-something/exit-room/" + room_id;
    });
    $(".overlay").css({'display':'block','opacity':'0.8'});
    $(".showbox").stop(true).animate({'margin-top':'300px','opacity':'1'},200);

}

function notification (type) {
    var note = 'Wrong guess, try again.';
    if (type == 'empty') {
        note = 'Enter a guess.';
    } else if (type == 'too long') {
        note = 'The Guess word is too long.';
    } else {
        note = "Welcome back.";
    }

    $.notify({
	      // options
	      icon: 'glyphicon glyphicon-edit',
	      message: note
          },{
	      // settings
	      delay: 100,
	      type: 'warning',
	      offset: {
		      x: 0,
		      y: 50
	      }
    });

}


$( document ).ready(function() {
    room_id = $("#mycanvas").attr("name");

    $("#nav-home-btn").click(function(event) {
        event.preventDefault();
        if (in_game) {
                dialog ("QUIT_GAME");
            }
        if (!in_game) {
            var message = {
                exit_notify : "drawer exits normally",
            }
            gamesock.send(JSON.stringify(message));
            window.location.href ="/draw-something/exit-room/" + room_id;
        }
    });

    var h = $(document).height();
	$(".overlay").css({"height": h });

    loading();

    var canvas = this.__canvas = new fabric.Canvas('mycanvas', {
        isDrawingMode: true
    });

    (function() {
        var $ = function(id){return document.getElementById(id)};
        fabric.Object.prototype.transparentCorners = false;

        var drawingOptionsEl = $('drawing-mode-options'),
            drawingColorEl = $('drawing-color'),
            drawingLineWidthEl = $('drawing-line-width'),
            clearEl = $('clear-canvas');

        clearEl.onclick = function() { canvas.clear() };

        if (fabric.PatternBrush) {
            var vLinePatternBrush = new fabric.PatternBrush(canvas);
            vLinePatternBrush.getPatternSrc = function() {
                var patternCanvas = fabric.document.createElement('canvas');
                patternCanvas.width = patternCanvas.height = 10;
                var ctx = patternCanvas.getContext('2d');

                ctx.strokeStyle = this.color;
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(0, 5);
                ctx.lineTo(10, 5);
                ctx.closePath();
                ctx.stroke();

                return patternCanvas;
            };

            var hLinePatternBrush = new fabric.PatternBrush(canvas);
            hLinePatternBrush.getPatternSrc = function() {

                var patternCanvas = fabric.document.createElement('canvas');
                patternCanvas.width = patternCanvas.height = 10;
                var ctx = patternCanvas.getContext('2d');

                ctx.strokeStyle = this.color;
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(5, 0);
                ctx.lineTo(5, 10);
                ctx.closePath();
                ctx.stroke();

                return patternCanvas;
            };

            var squarePatternBrush = new fabric.PatternBrush(canvas);
            squarePatternBrush.getPatternSrc = function() {

                var squareWidth = 10, squareDistance = 2;

                var patternCanvas = fabric.document.createElement('canvas');
                patternCanvas.width = patternCanvas.height = squareWidth + squareDistance;
                var ctx = patternCanvas.getContext('2d');

                ctx.fillStyle = this.color;
                ctx.fillRect(0, 0, squareWidth, squareWidth);

                return patternCanvas;
            };

            var diamondPatternBrush = new fabric.PatternBrush(canvas);
            diamondPatternBrush.getPatternSrc = function() {

                var squareWidth = 10, squareDistance = 5;
                var patternCanvas = fabric.document.createElement('canvas');
                var rect = new fabric.Rect({
                    width: squareWidth,
                    height: squareWidth,
                    angle: 45,
                    fill: this.color
                });

                var canvasWidth = rect.getBoundingRect().width;

                patternCanvas.width = patternCanvas.height = canvasWidth + squareDistance;
                rect.set({ left: canvasWidth / 2, top: canvasWidth / 2 });
                var ctx = patternCanvas.getContext('2d');
                rect.render(ctx);

                return patternCanvas;
            };

        }

        $('drawing-mode-selector').onchange = function() {

            if (this.value === 'hline') {
                canvas.freeDrawingBrush = vLinePatternBrush;
            }
            else if (this.value === 'vline') {
                canvas.freeDrawingBrush = hLinePatternBrush;
            }
            else if (this.value === 'square') {
                canvas.freeDrawingBrush = squarePatternBrush;
            }
            else if (this.value === 'diamond') {
                canvas.freeDrawingBrush = diamondPatternBrush;
            }
            else {
                canvas.freeDrawingBrush = new fabric[this.value + 'Brush'](canvas);
            }

            if (canvas.freeDrawingBrush) {
                canvas.freeDrawingBrush.color = drawingColorEl.value;
                canvas.freeDrawingBrush.width = parseInt(drawingLineWidthEl.value, 10) || 1;
            }
        };

        drawingColorEl.onchange = function() {
            canvas.freeDrawingBrush.color = this.value;
        };
        drawingLineWidthEl.onchange = function() {
            canvas.freeDrawingBrush.width = parseInt(this.value, 10) || 1;
            this.previousSibling.innerHTML = this.value;
        };

        if (canvas.freeDrawingBrush) {
            canvas.freeDrawingBrush.color = drawingColorEl.value;
            canvas.freeDrawingBrush.width = parseInt(drawingLineWidthEl.value, 10) || 1;
        }
    })();

    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    gamesock = new WebSocket(ws_scheme + '://' + window.location.host + "/game" + window.location.pathname);
    var interval_id=-1;
    console.log(gamesock);
    gamesock.onerror = function(event) {
        console.log("Websocket error, trying reconnecting...");
        gamesock = new WebSocket(ws_scheme + '://' + window.location.host + "/game" + window.location.pathname);
    }
    gamesock.onmessage = function(message) {
        var text = message.data;
        var data = JSON.parse(text);
        if (data.notify) {
            console.log("Notify is: "+data.notify);
            if (data.notify == "ready to start" || data.notify == "time remain from guesser") {
                guesser_username = data.guesser;
                console.log("ready, parterner is: ");
                console.log(guesser_username);
                var partner_content = "<div class='row partner'><img src='/draw-something/profile-image/" + guesser_username + "' class='img-circle img-thumbnail' width='60' style='float:right;'>" +
                    "<p class='name'> Your partner:</p><p>" + guesser_username + "</p></div>";
                console.log(partner_content);
                if ($(".partner").length <= 0) {
                    $(".timer").parent().prepend(partner_content);
                }

                // http://127.0.0.1:8000/draw-something/drawer-page/draw-something/profile-image/Arwen 500 (Internal Server Error)

                loadingDone();
                $("#keyword").html(data.keyword);
                in_game = true;

                shortly = new Date();
                var time = 30.5;
                if (data.level) {
                    if (data.level == 'm') {
                        time = 45.5;
                    } else if (data.level == 'h') {
                        time = 60.5;
                    }
                }

                if (data.notify == "time remain from guesser") {
                    console.log("Remaining time is:" + data.time_remain_guesser);
                    time = parseInt(data.time_remain_guesser) - 1;
                    canvas.loadFromJSON(data.canvas_content);
                    notification("back");
                }
                shortly.setSeconds(shortly.getSeconds() + time);
                $('#count-down').countdown({until: shortly,
                                            onExpiry: function() {
                                            // When time runs out, drawer(not guesser) sends server a message,
                                            // so server can delete the game object.
                                                if (gamesock.readyState == WebSocket.OPEN) {
                                                    var message = {
                                                        time_notify : "time runs out",
                                                    }
                                                    gamesock.send(JSON.stringify(message));
                                                }
                                            },
                                            format: 'S',
                                            compact: true,
                                            description: ''});
                console.log($("#count-down").children().html());

                interval_id = window.setInterval(function() {
                    var message = {
                        canvas_content: JSON.stringify(canvas),
                    }
                    gamesock.send(JSON.stringify(message));
                }, 100);
            }
            if (data.notify == "guess correctly") {
                $("#guess-result").html(data.answer);
                $('#count-down').countdown('pause');
                window.clearInterval(interval_id);
                in_game = false;
                var flag = "GUESS_CORRECT";
                var points = data.points;
                dialog(flag,points);
            }
            if (data.notify == "time runs out and game over") {
                window.clearInterval(interval_id);
                in_game = false;
                var flag = "TIME_RUNS_OUT";
                dialog(flag);
            }
            if (data.notify == "guesser exits normally") {
                $('#count-down').countdown('pause');
                console.log("Guesser exits!");
                window.clearInterval(interval_id);
                in_game = false;
                var flag = "GUESSER_EXIT";
                dialog(flag);
            }
            if (data.notify == "guesser reconnect") {
                console.log("Guesser reconnect");
                var time = $('#count-down').children().html();
                console.log("Sending remaining time:" + time);
                if (gamesock.readyState == WebSocket.OPEN) {
                    var message = {
                        time_remain : time,
                    }
                    gamesock.send(JSON.stringify(message));
                }
            }
        }
        if(data.guess) {
            console.log(data.guess);
            $("#guess-result").html(data.guess);
        }
    };
});
// vim:set spell spl=en fo=wan1croql tw=80 ts=2 sw=2 sts=2 sta et ai cin fenc=utf-8 ff=unix:

