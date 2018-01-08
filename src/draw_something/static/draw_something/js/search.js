function search(){
    var search_bar = $("#search_bar");
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
     $("#search-btn").click(search);
     setTimeout(function() { $("#search_error").remove();}, 3000)
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

    $( "body" ).on( "click", ".join-btn", function( event ) {
        var elem = $( this );
        var id = elem.attr('name');
        window.location.href = '/draw-something/join-room/'+id;
    });

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

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});