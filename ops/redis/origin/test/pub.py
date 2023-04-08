import redis
import time

HOST = "192.168.20.197" #'192.168.20.131'
PORT = "31549" #'6379'
CHANNEL = 'test'
password = "123456a@"

if __name__ == '__main__':
    r = redis.Redis(host=HOST, port=PORT, password=password)
    pub = r.publish(
        channel=CHANNEL,
        message='HelloWorld!'
    )

