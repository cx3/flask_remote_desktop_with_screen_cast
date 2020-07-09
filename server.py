#! Python38
import os
import sys
from functools import wraps
from time import sleep

# third party imports
import pyautogui
from flask import Flask, request, send_from_directory, render_template

# let's code!


app = Flask(__name__)
pg = {'methods': ['POST', 'GET']}


config = {
    'admin_login': 'admin',
    'admin_pass': 'admin',
    'spectators': {'user1': 'pass1', 'user2': 'pass2'},
    'spectators_allowed': True,

    'host': '0.0.0.0',
    'port': 80,
    'debug': True,

    'logged_users': {}
}


def is_admin(client_ip: str):
    for user, ip in config['logged_users'].items():
        if client_ip == ip:
            if user == config['admin_login']:
                return True
    return False


def is_spectator(client_ip: str):
    for user, ip in config['logged_users'].items():
        if client_ip == ip:
            if user in config['spectators'].keys():
                return True
    return False


def js_redirect(link: str) -> str:
    link = link if link[0] == '/' else link = '/' + link
    return f"<script>window.location='{link}';</script>"


@app.route('/', **pg)
def main_route():
    return js_redirect('/rdp')


"""
if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200
else:
    return jsonify({'ip': request.environ['HTTP_X_FORWARDED_FOR']}), 200 """


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
        return 'Pass both valid user name and password. User cannot login twice'


@app.route('/screenshot', methods=['GET'])
def get_screenshot_route():
    if is_admin(request.remote_addr) or is_spectator(request.remote_addr):
        pyautogui.screenshot().save('screenshots/last.jpg')
        return send_from_directory('screenshots', 'last.jpg', mimetype="image/jpg")
    return ''


@app.route('/rdp', **pg)
@app.route('/remote_desktop', **pg)
def remote_desktop_route():

    if request.remote_addr not in config['logged_users'].values():
        return render_template('login.html', next='/rdp')

    if request.method == 'GET':
        return render_template('remote_desktop.html')
    if request.method == 'POST':
        args = dict(request.args)
        print("ARGS RECEIVED:", args)

        try:
            x = ''.join(_ for _ in args['x'] if _.isdigit())  # ints only due to xss. 
            y = ''.join(_ for _ in args['y'] if _.isdigit())  # it should be in little bit other way :) 
            x, y = int(x), int(y)
            pyautogui.moveTo(x, y)
            pyautogui.click(x, y)
            sleep(0.1)
            pyautogui.screenshot().save('screenshots/last.jpg')
        except (ValueError, Exception):
            return 'x or y value error'

        return "OK " + str(args)
    return ''


@app.route('/cast', methods=['GET'])
def screen_cast_route():
    if config['spectators_allowed']:
        if request.remote_addr in config['logged_users'].values():
            return render_template('spectator.html')
        else:
            return "<script>window.location='/login?next=/cast';</script>"
    return 'Spectators are not allowed by admin'


if __name__ == '__main__':
    app.run(host=config['host'], port=config['port'], debug=config['debug'])
