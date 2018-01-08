var in_game = false;
var gamesock;
function loading () {
    $(".overlay").css({'display':'block','opacity':'0.8'});
    $(".showbox").stop(true).animate({'margin-top':'300px','opacity':'1'},200);
}

function loadingDone () {
    $(".showbox").remove();
    $(".overlay").css({'display':'none','opacity':'0'});
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
            "<div class='loadingWord'>Smart guess !</div> <br>" +
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
    if (flag == "DRAWER_EXIT") {
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
        var room_id = $("#mycanvas").attr("name");
        window.location.href ="/draw-something/drawer-page/" + room_id;
    });
    $("#home-btn").click(function() {
        console.log("in exit");
        var room_id = $("#mycanvas").attr("name");
        window.location.href ="/draw-something/exit-room/" + room_id;
    });
    $("#continue-btn").click(function() {
        loadingDone();
    });
    $("#quit-btn").click(function() {
        if (in_game) {
            var message = {
                exit_notify : "guesser exits normally",
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
    } else if (type =="back") {
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
                exit_notify : "guesser exits normally",
            }
            gamesock.send(JSON.stringify(message));
            window.location.href ="/draw-something/exit-room/" + room_id;
        }
    });

    var h = $(document).height();
	$(".overlay").css({"height": h });

    loading();

    var canvas = this.__canvas = new fabric.Canvas('mycanvas', {
        isDrawingMode: false
    });

    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    gamesock = new WebSocket(ws_scheme + '://' + window.location.host + "/game" + window.location.pathname);
    console.log(gamesock);
    gamesock.onerror = function(event) {
        console.log("Websocket error, trying reconnecting...");
        gamesock = new WebSocket(ws_scheme + '://' + window.location.host + "/game" + window.location.pathname);
    }

    gamesock.onmessage = function(message) {
        var text = message.data;
        var data = JSON.parse(text);
        if (data.notify) {
            console.log(data.notify);
            if (data.notify == "ready to start" || data.notify == "time remain from drawer") {
                drawer_username = data.drawer;
                console.log("ready, parterner is: ");
                console.log(drawer_username);
                var partner_content = "<div class='row partner'><img src='/draw-something/profile-image/" + drawer_username + "' class='img-circle img-thumbnail' width='60' style='float:right;'>" +
                    "<p class='name'> Your partner:</p><p>" + drawer_username + "</p></div>";
                if ($(".partner").length <= 0) {
                    $(".timer").parent().prepend(partner_content);
                }


                loadingDone();
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
                if (data.notify == "time remain from drawer") {
                    console.log("Remaining time is:" + data.time_remain_drawer);
                    time = parseInt(data.time_remain_drawer) - 1;
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
                console.log($("#count-down"));
            }
            if (data.notify == "guess correctly") {
                $('#count-down').countdown('pause');
                in_game = false;
                var flag = "GUESS_CORRECT";
                var points = data.points;
                dialog(flag,points);
            }
            if (data.notify == "time runs out and game over") {
                in_game = false;
                var flag = "TIME_RUNS_OUT";
                dialog(flag);
            }
            if (data.notify == "drawer exits normally") {
                $('#count-down').countdown('pause');
                console.log("Drawer exits!");
                in_game = false;
                var flag = "DRAWER_EXIT";
                dialog(flag);
            }
            if (data.notify == "drawer reconnect") {
                console.log("Drawer reconnect");
                var time = $('#count-down').children().html();
                console.log("Sending remaining time:" + time);
                if (gamesock.readyState == WebSocket.OPEN) {
                    var message = {
                        time_remain : time,
                        canvas_content: JSON.stringify(canvas),
                    }
                    gamesock.send(JSON.stringify(message));
                }
            }
        }
        if (data.guess) {
            notification('wrong');
        }
        if (data.canvas_content){
            canvas.loadFromJSON(data.canvas_content);
        }
    };

    $("#guess_form").on("click", "button", function() {
        var guess_answer = $('#guess').val();
        if (guess_answer == '') {
            notification('empty');
        } else if (guess_answer.length > 30) {
            notification('too long');
        } else {
            var message = {
                guess: guess_answer,
            }
            gamesock.send(JSON.stringify(message));
            $("#guess").val('').focus();
        }

    });

});