import g4f
from g4f.client import Client
import requests
import time
import json

client = Client()
AUTHOR_TAG = 'evgenykarachinsky'
AUTHOR_PASSWORD = 'karach'
last_post_responded = 2909


def ask_gpt(prompt):
    response = client.chat.completions.create(
        model=g4f.models.gpt_4,
        provider=g4f.Provider.Liaobots,
        max_tokens=1000000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def add_post(text, title='Мое мнение', html=''):
    if not text:
        print('Text is empty!')
        return
    
    requests.post('https://coffeetox.ru/addpostapi', json={
        'author_tag': AUTHOR_TAG,
        'author_password': AUTHOR_PASSWORD,
        'text': text,
        'title': title,
        'html': html
    }, verify=False)

def generate_prompt(current_number):
    text_author, text = get_contents_of_post(current_number)

    prompt = f'''Ты -- Евгений Яковлевич Карачинский, видный активист и политический деятель резко либеральных взглядов. Тебе пишет {text_author}. Содержание его письма следующее:
    {text}
    Напиши ему свои мысли по тому поводу, по которому он пишет
    Напиши до 150 слов, будто ты пишешь в Твиттер. 
    Помни, что тебе необходимо вовлечь каким-либо образом свои политические взгляды в твой ответ'''

    print(prompt)

    return prompt

def get_new_last_post():
    l = requests.get('https://coffeetox.ru/getmaxpostid', verify=False).content

    print(type(l))
    print(l)
    new_last_post = json.loads(l).get('id')

    return new_last_post

def get_contents_of_post(current_number):
    l = requests.get('https://coffeetox.ru/getfeed?start=' + str(current_number) + '&count=1&author_id=', verify=False).content

    print(l)

    text_author = json.loads(l)[0].get('author_name')
    text = json.loads(l)[0].get('text')

    return text_author, text

def scan(last_post_responded):
    for i in range(last_post_responded, get_new_last_post() + 1):
        text, text = get_contents_of_post(i)
        ex = text.split('://')
        if ex[0] == 'https':
            continue
        elif text == '':
            continue
        else:
            create_post(generate_prompt(i))
    last_post_responded = get_new_last_post()
    return last_post_responded

def create_post(prompt):
    try:
        print('Выражаю мнение...')
        response = ask_gpt(prompt)
        add_post(response.replace('**', ''))
        time.sleep(15)
        print('Выразил свое мнение!')
    except Exception as e:
        print('Error:', e)
    
last_post_responded = scan(last_post_responded)
