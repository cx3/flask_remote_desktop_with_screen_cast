#! Python38
import os
import sys
from functools import wraps
from time import sleep

# third party imports
import pyautogui
from PIL import ImageDraw
from flask import Flask, request, send_from_directory, render_template


# let's code!


app = Flask(__name__)
pg = {'methods': ['POST', 'GET']}


config = {
    'admin_login': 'a',
    'admin_pass': 'a',
    'spectators': {'user1': 'pass1', 'user2': 'pass2'},
    'spectators_allowed': True,
    'spectators_allowed_without_password': False,

    'host': '0.0.0.0',
    'port': 80,
    'debug': True,

    'logged_users': {}
}


def is_admin(client_ip: str) -> bool:
    for user, ip in config['logged_users'].items():
        if client_ip == ip:
            if user == config['admin_login']:
                return True
    return False


def is_spectator(client_ip: str) -> bool:
    for user, ip in config['logged_users'].items():
        if client_ip == ip:
            if user in config['spectators'].keys():
                return True
    return False


def is_logged(client_ip: str) -> bool:
    return client_ip in config['logged_users'].values()


def js_redirect(link: str) -> str:
    link = link if link[0] == '/' else '/' + link
    return f"<script>window.location='{link}';</script>"


@app.route('/', **pg)
def main_route():
    return js_redirect('/rdp')


@app.route('/ip', **pg)
def get_ip_route():
    return request.remote_addr


@app.route('/login', **pg)
def login():

    if request.method == 'GET':
        if is_admin(request.remote_addr):
            return js_redirect('/rdp')
        if is_spectator(request.remote_addr):
            return js_redirect('/cast')
        return render_template('login.html')

    if request.method == 'POST':
        args = dict(request.form)

        if 'user' in args and 'pass' in args:
            if args['user'] in config['logged_users']:
                return 'This login is busy'
            if args['user'] == config['admin_login'] and args['pass'] == config['admin_pass']:
                config['logged_users'][args['user']] = request.remote_addr
                if 'next' in args:
                    return js_redirect(args['next'])
                return js_redirect('/rdp')
            if config['spectators_allowed']:
                for user, passwd in config['spectators'].items():
                    if args['user'] == user and passwd == args['pass']:
                        config['logged_users'][args['user']] = request.remote_addr
                        return js_redirect('/cast')
            else:
                return 'Spectators are disabled by admin'
        return 'Pass both valid user name and password. One user cannot login twice'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_logged(get_ip_route()):
            return f(*args, **kwargs)
        return js_redirect('/login?next=/rdp')
    return decorated_function


@app.route('/screenshot', methods=['GET'])
def get_screenshot_route():
    if is_logged(request.remote_addr):
        shot = pyautogui.screenshot()
        draw = ImageDraw.Draw(shot)
        x, y = pyautogui.position()
        try:
            draw.ellipse((x-10, y-10, x + 10, y + 10), fill='green', outline='red')
        except (ValueError, Exception):
            pass
        shot.save('screenshots/last.jpg')
        return send_from_directory('screenshots', 'last.jpg', mimetype="image/jpg")
    return ''


@app.route('/mouse', **pg)
def move_mouse_route():
    if is_admin(request.remote_addr):
        args = dict(request.args)
        try:
            x = ''.join(_ for _ in args['x'] if _.isdigit())  # anti-XSS
            y = ''.join(_ for _ in args['y'] if _.isdigit())  # refactor it, wrong way ;>
            pyautogui.moveTo(int(x), int(y))
            return 'OK'
        except (ValueError, Exception):
            pass
    return js_redirect('/login?next=/rdp')


@app.route('/rdp', **pg)
@app.route('/remote_desktop', **pg)
def remote_desktop_route():

    if request.method == 'GET':
        if is_admin(request.remote_addr):
            return render_template('remote_desktop.html')
        if is_logged(request.remote_addr):
            return render_template('spectator.html')

        return js_redirect('/login?next=/rdp')

    if request.method == 'POST':

        if is_admin(request.remote_addr):
            args = dict(request.args)
            try:
                x = ''.join(_ for _ in args['x'] if _.isdigit())  # anti-XSS
                y = ''.join(_ for _ in args['y'] if _.isdigit())
                x, y = int(x), int(y)
                pyautogui.moveTo(x, y)
                pyautogui.click(x, y)
                sleep(0.1)
                pyautogui.screenshot().save('screenshots/last.jpg')
            except (ValueError, Exception):
                return 'x or y value error'
            return "OK " + str(args)
        else:
            return js_redirect('/login?next=/rdp')
    return ''


@app.route('/cast', methods=['GET'])
def screen_cast_route():
    if is_admin(request.remote_addr):
        return render_template('remote_desktop.html')

    if config['spectators_allowed']:
        if is_spectator(request.remote_addr) or config['spectators_allowed_without_password']:
            return render_template('spectator.html')
        return js_redirect('/login?next=/cast')
    return 'Spectators are not allowed by admin'


@app.route('/download', methods=['GET'])
def download():
    # for instance:
    return send_from_directory("d:\\proj\\py", 'flask_remote_desktop.zip')


if __name__ == '__main__':
    app.run(host=config['host'], port=config['port'], debug=config['debug'])
