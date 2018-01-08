Yingwen Zhang's contribution: 50%

	1. Guesser page: when “guess” button is clicked, render the guesser page, create the websocket connection to server
	2. Canvas synchronization: display synchronized canvas on guesser’s page
	3. Submit guess: send guesser’s answer to server
	4. Show guess result: show the result of guesser’s answer(correct, incorrect, empty)
	5. End game: end the game if guess correctly or  time out.
	6. Search room: User can search the room by room name, player in the room and level of the room.
	7. Score player: If game succeeds, score the player based on the level.
	8. Validate the player number in one room: At most two players can in one room.
	9. Player quit game alert: If player want to quit the game during the game, alert and confirm the quit.
	10. restore game after a player disconnects by accident
	11. Display rank page


Tianqi Zhao's contribution: 50%

	1. Home page: list all the rooms
    2. “Draw” button is clicked: display drawer’s page, open a WebSocket, create a new game
    3. Canvas implementation: draw on canvas, send canvas content to guesser per 0.1 second
    4. Message receiving: display wrong guess, end game due to time running out, end game due to correct guess
    5. Timer implementation: jquery.countdown.js
    6. User register and login
    7. Edit profile and change password
    8. Player can create room: room name, level(easy, medium, hard)
    9. Role assignment: first to join the room is drawer, second is guesser
    10. Use different word library for rooms of different difficulty level
    11. restore game after a player disconnects by accident



