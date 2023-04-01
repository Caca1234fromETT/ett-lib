import requests

def get(name):
    c = requests.get('https://tikolu.net/edit/.text/' + name).text
    return c

def post(name, content):
    values = {
        'content': content,
        'timestamp': None,
        'ignoreconflict': True,
    }
    c = requests.post('https://tikolu.net/edit/' + name, json = values)
    return c

import threading

def start_thread(func, name=None, args = [], kwargs = []):
    threading.Thread(target=func, name=name, args=args, kwargs = kwargs).start()

def post_async(name, content):
    start_thread(post, kwargs={"name": name, "content": content})
