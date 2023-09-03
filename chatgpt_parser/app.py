import openai
import os
from dotenv import load_dotenv
import requests
import time
from chatgpt_parser.models import TextsParsingSet, Text
from django.db.models import Avg
from django.db.models import F
from celery import shared_task
from django.contrib.auth.models import User
import zipfile
from io import BytesIO

load_dotenv()
openai.api_key = os.getenv("OPENAI_API")
TEXTRU_KEY = os.getenv("TEXTRU_KEY")
TEXTRU_URL = "http://api.text.ru/post"


def get_text_from_chat(task, temperature):
    result = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': task}
        ],
        temperature=float(temperature)
    )
    print('Сгенерили текст на тему:', task)
    return result['choices'][0]['message']['content']


def raise_uniqueness(text, rewriting_task):
    task = (f'{rewriting_task}\n{text}')
    result = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': task}
        ],
        temperature=0
    )

    return result['choices'][0]['message']['content']


def get_text_uniqueness(text):
    headers = {
        "Content-Type": "application/json"
    }
    text_data = {
        "text": text,
        "userkey": TEXTRU_KEY
    }
    response = requests.post(TEXTRU_URL, json=text_data, headers=headers)
    uid = response.json()['text_uid']
    attempts = 0
    uid_data = {
        "uid": uid,
        "userkey": TEXTRU_KEY
    }
    while attempts < 10:
        if attempts < 5:
            time.sleep(20)
        time.sleep(60)
        response = requests.post(TEXTRU_URL, json=uid_data, headers=headers)
        if 'text_unique' in response.json():
            return float(response.json()["text_unique"])
        attempts += 1


def generate_text(task, temperature, rewriting_task, required_uniqueness):
    try:
        text = get_text_from_chat(task, temperature)
        print('получили текст')
        text_uniqueness = get_text_uniqueness(text)
        print('получили уникальность')
        attempts_to_uniqueness = 0
        while text_uniqueness < float(required_uniqueness) and attempts_to_uniqueness <= 3:
            text = raise_uniqueness(text, rewriting_task)
            print('переписали текст')
            text_uniqueness = get_text_uniqueness(text)
            print('пересчитали уникальность')
            attempts_to_uniqueness += 1
        return {
            'text': text,
            'attempts_to_uniqueness': attempts_to_uniqueness,
            'text_uniqueness': text_uniqueness
        }
    except:
        return


def generate_text_set_zip(text_set):
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'a', zipfile.ZIP_DEFLATED, False) as zipf:
        texts = text_set.texts.all()
        for text in texts:
            text_content = (f"уникальность: {text.uniqueness}\n\n"
                            f"{text.header}\n"
                            f"{text.text}")
            header = text.header.replace('\r', '')

            zipf.writestr(f"{header}.txt", text_content)
        failed_texts = text_set.failed_texts
        low_uniqueness_texts = text_set.low_uniqueness_texts
        print('failed_texts', failed_texts)
        if failed_texts:
            zipf.writestr("не получились.txt", failed_texts)
        print('low_uniqueness_texts', low_uniqueness_texts)
        if low_uniqueness_texts:
            zipf.writestr("тексты с низкой уникальностью.txt", low_uniqueness_texts)

    buffer.seek(0)
    return buffer


@shared_task()
def generate_texts(author,
                   set_name,
                   temperature,
                   task_strings,
                   rewriting_task,
                   required_uniqueness):
    task_list = [task for task in task_strings.split('\n') if "||" in task]
    new_set = TextsParsingSet.objects.create(
        total_amount=len(task_list),
        author=User.objects.get(pk=author),
        set_name=set_name,
        temperature=float(temperature)
    )
    for task in task_list:
        chat_request, header = task.split('||')
        text_data = generate_text(chat_request,
                                  temperature,
                                  rewriting_task,
                                  required_uniqueness)

        if not text_data:
            new_set.failed_texts += task + '\n'
            new_set.save()
            continue
        new_text = Text.objects.create(
            header=header,
            text=text_data['text'],
            attempts_to_uniqueness=text_data['attempts_to_uniqueness'],
            uniqueness=text_data['text_uniqueness'],
            chat_request=chat_request,
            parsing_set=new_set
        )

        if text_data['text_uniqueness'] < float(required_uniqueness):
            new_set.low_uniqueness_texts += (task
                                             + '||'
                                             + str(text_data['text_uniqueness'])
                                             + '\n')
            new_set.save()

        new_set.parsed_amount = F('parsed_amount') + 1
        new_set.save(update_fields=['parsed_amount'])
        new_set.refresh_from_db()

    uniqueness_data = (
        Text.objects.filter(parsing_set=new_set).aggregate(
            average_attempts=Avg('attempts_to_uniqueness'),
            uniqueness=Avg('uniqueness')
        ))

    new_set.average_attempts_to_uniqueness = uniqueness_data['average_attempts'] or 0
    new_set.average_uniqueness = uniqueness_data['uniqueness'] or 0
    new_set.is_complete = True
    new_set.save()
    print('закончили работу')
