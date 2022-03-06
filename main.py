import socketio
import os
from subprocess import call
import threading
import signal
import sys
import configparser
import time


config = configparser.RawConfigParser()
config.read('server.properties')

sio = socketio.Client()
auth_token = ''


def get_token():
    f = open("token", "r")
    return f.read()


@sio.event
def volume(data):
    print('set volume: ', data)
    call(["amixer", "-D", "pulse", "sset", "Master", "{}%".format(data)])


def startKiro(data):
    print('start kiro: '+data)
    os.system('chromium-browser --kiosk www.kiro.com')


@sio.event
def performanceOS(data):
    print('get performace of os')
    cpu_usage = str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())
    cpu_temp = res = os.popen('vcgencmd measure_temp').readline().replace("temp=", "").replace("'C\n", "")
    sio.emit("osPerformance", {'cpu_usage': cpu_usage, 'cpu_temp': cpu_temp})


@sio.event
def connect():
    print("I'm connected!")
    sio.emit("join-agent", {'token': auth_token})


@sio.event
def agentConnect(data):
    print("Agent connect!")


@sio.event
def connect_error(data):
    print("The connection failed!")


@sio.event
def disconnect():
    print("I'm disconnected!")


def agent_socket():
    sio.connect('http://localhost:5000', wait_timeout=10)


def signal_handler(signal, frame):
    print("goodbye agent!")
    sys.exit(0)


def agent():
    prot = config.get('Server', 'server.prot')
    address = config.get('Server', 'server.addr')
    port = config.get('Server', 'server.port')
    sio.connect('{}://{}:{}'.format(prot, address, port), wait_timeout=10)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    auth_token = get_token()
    t = threading.Thread(target=agent)
    t.start()
    t.join()

