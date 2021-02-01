Python 3.8 + Flask + PyAutoGUI + PIL (Python Imaging Library)

Flask web server with very simple login system for one admin who control mouse on the server via browser.
App allows screen casting for logged spectators, spectators without loggin, disable spectators.

Routes info:

/
main route. Lists all possible routes served by Flask's app

/login
Allows users to log in

/logout
You know

/cast
Route for spectators who watch how admin works on the server

/rdp
Route for admin to control machine

/logout_all
Route for admin to logout all users (with himself)

/mouse?x=[position]&y=[position]
/mouse?x=[position]&y=[position]&buttons=[button_number]
Places mouse on the screen on the machine. Admin required


/keyboard?keys=[some keys here]
/keyboard?special=[special key]
/keyboard?specials=[special keys]
Gets pressed keys from client's browser and puts them on the screen of the server. Admin required


By now works fine only under LAN. While working under solution with external serves for functionality like TeamViewer or other RDP systems
