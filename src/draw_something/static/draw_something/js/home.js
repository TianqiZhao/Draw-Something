function populateList() {
    $.get("/draw-something/get-changes").done(function(data) {
        var list = $("#room_list");
        list.data('max-time', data['max-time']);
        list.html('')

        //getUpdates();
        for (var i = 0; i < data.rooms.length; i++) {
            var room = data.rooms[i];
            var new_room = $(room.html);
            new_room.data("room-id", room.id);
            list.prepend(new_room);
        }
    }).fail(function(xhr, status, errorThrown) {
        alert( "Sorry, there was a problem!" );
        console.log( "Error: " + errorThrown );
        console.log( "Status: " + status );
        console.dir( xhr );
    });
}

function getUpdates() {
    var list = $("#room_list")
    var max_time = list.data("max-time")
    $.get("/draw-something/get-changes/"+ max_time)
      .done(function(data) {
          list.data('max-time', data['max-time']);
          for (var i = 0; i < data.rooms.length; i++) {
              var room = data.rooms[i];
              var new_room = $(room.html);
              new_room.data("room-id", room.id);
              list.prepend(new_room);
          }
      });
}

function search(){
    var search_bar = $("#search_bar");
    var param = $("#search_param");
    var select = $('#search_concept').text();
    var content = $("#search_content").val();
    console.log(select + ": "+ content);
    window.location.replace("/draw-something/search/"+ select + "=" + content);
}

function notification () {
    var note = '<strong>The room is full, try another room.</strong>'
    $.notify({
	      // options
	      message: note
          },{
	      // settings
	      delay: 100,
	      type: 'info',
	      offset: {
		      x: 500,
		      y: 50
	      }
    });

}

$( document ).ready(function() {  // Runs when the document is ready
    populateList();

    window.setInterval(getUpdates, 5000);

    $( "body" ).on( "click", ".join-btn", function( event ) {
        var elem = $( this );
        var id = elem.attr('name');
//        $.post('/draw-something/join-room/'+id);
        window.location.href = '/draw-something/join-room/'+id;
    });
    var room_full = $("#room_full").val();
    console.log("room full: " + room_full);
    if (room_full == "True") {
        notification();
        window.setTimeout(function() {
            window.location.href = '/draw-something/home/';
        },3000);
    }

    // using jQuery
    // https://docs.djangoproject.com/en/1.10/ref/csrf/
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
    }

    $('.search-panel .dropdown-menu').find('a').click(function(e) {
		e.preventDefault();
		var param = $(this).text();
		$('.search-panel span#search_concept').text(param);
		if (param == 'Player') {
		    $('#search_content').attr('placeholder','Search: enter player name here...');
		} else if (param == 'Level') {
		    $('#search_content').attr('placeholder','Search: choose from easy/medium/hard...');
		} else if (param == 'Room name') {
		    $('#search_content').attr('placeholder','Search: enter room name here...');
		}

	});
    $(".search-option li a")[2].click();


    $('.create-level-panel .dropdown-menu').find('a').click(function(e) {
		e.preventDefault();
		var param = $(this).text();
		if (param == 'Easy') {
		    $('.create-level-panel .level-btn').attr('class','btn btn-info dropdown-toggle level-btn');
		} else if (param == 'Medium') {
		    $('.create-level-panel .level-btn').attr('class','btn btn-warning dropdown-toggle level-btn');
		} else if (param == 'Hard') {
		    $('.create-level-panel .level-btn').attr('class','btn btn-danger dropdown-toggle level-btn');
		}
		$('.create-level-panel span#level-concept').text(param);
	});

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $("#search-btn").click(search);

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#create_room_form').on('submit', function(event) {
        var contentField = $("#room_name_field");
        event.preventDefault(); // Prevent form from being submitted

        var form = new FormData();
        form.append('room_name',$("#room_name_field").val());

        if ($("#level-concept").html() == 'Easy') {
            form.append('level','e');
        } else if ($("#level-concept").html() == 'Medium') {
            form.append('level','m');
        } else if ($("#level-concept").html() == 'Hard') {
            form.append('level','h');
        } else {
            form.append('level',$("#level-concept").html());
        }

        $.ajax({
            url: "/draw-something/add-room",
            method: "POST",
            dataType: 'json',
            data: form,
            processData: false,
            contentType: false,
        }).always(function(data) {
            $(".post-error").remove();
            getUpdates();
            contentField.val("");
        }).done(function(data) {
            console.log(data);
            if ("room_name" in data) {
                var errorMessage = document.createElement('p');
                errorMessage.innerHTML = data.room_name[0].message;
                console.log(data.room_name[0].message);
                $(errorMessage).css({"margin-left":"20px","color": "#212121","font-size": "20px"});
                $(errorMessage).attr("class", "post-error");
                contentField.parent().append(errorMessage);
            }
            if ("level" in data) {
                var errorMessage = document.createElement('p');
                errorMessage.innerHTML = data.level[0].message;
                console.log(data.level[0].message);
                $(errorMessage).css({"margin-left":"20px","color": "#212121","font-size": "20px"});
                $(errorMessage).attr("class", "post-error");
                contentField.parent().append(errorMessage);
            }
        });
    });

});