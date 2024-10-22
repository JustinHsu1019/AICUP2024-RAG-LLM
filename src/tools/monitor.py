import subprocess
import time

import requests


def check_service():
    url = 'http://xxxx/api/'
    try:
        response = requests.get(url)
        if response.status_code != 200:
            restart_service()
    except requests.RequestException:
        restart_service()


def restart_service():
    print('Service is down. Restarting service...')
    subprocess.run(['nohup', 'python3', 'src/flask_app.py', '&'])


if __name__ == '__main__':
    while True:
        check_service()
        time.sleep(600)
