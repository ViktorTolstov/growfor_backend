import os

from flask import Flask
from flask_wtf.csrf import CsrfProtect, CSRFError
from flask_sslify import SSLify
from flask_cors import CORS
from app.router import routers, csrf_exempt
from app.models import config_init, config

app = Flask(__name__)
csrf = CsrfProtect(app)
sslify = SSLify(app)
CORS(app)

routers(app)
csrf_exempt(csrf)


def shutdown_server():
    import subprocess
    import signal

    print('\033[31m Server shutting down...')
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        if b'flask' in line or b'python' in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)


path = os.environ.get('CONFIG_PATH') if os.environ.get(
    'CONFIG_PATH') != None else "configure.ini"

config_init(path)
try:
    #   Flask application configuration

    app.config.update(dict(
        SECRET_KEY=str(config['FLASK_APP']['SECRET_KEY']),
        WTF_CSRF_SECRET_KEY=str(config['FLASK_APP']['WTF_CSRF_SECRET_KEY'])
    ))
    print(f"\n\033[32m Сервер запустился с конфигом:\n\033[32m {path}\n")
except KeyError:
    print(f"\033[31m Файл {path} не найден или неверный")
    shutdown_server()


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'message': 'Не верный токен'}), 401, {'ContentType': 'application/json'}
