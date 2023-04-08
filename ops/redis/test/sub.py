import redis
import time

HOST = '192.168.0.100'
PORT = 6379
CHANNEL = 'test'
password = "123456a@"
db="db0"

if __name__ == '__main__':
    r = redis.Redis(host=HOST, port=PORT, password=password)
    pub = r.pubsub()
    pub.subscribe(CHANNEL)

    while True:
        data = pub.get_message()
        if data:
            message = data['data']
            if message and message != 1:
                print("Message: {}".format(message))

        time.sleep(1)
