import requests

def get(name):
    c = requests.get('https://tikolu.net/edit/.text/' + name).text
    return c

def post(name, content):
    values = {
        'content': content,
        'timestamp': '0',
        'ignoreconflict': True,
    }
    c = requests.post('https://tikolu.net/edit/' + name, json = values)
    return c
