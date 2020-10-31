from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager
from datetime import datetime
import re
import hashlib
import glob
import os
import time as timec
import random
import requests
import json
from functools import wraps

def decor(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print('1')
        result = f(*args, **kwargs)
        print('2')
        return result
    return wrapper

# Конвертация объекта пагинатора в словарь
def paginatorParse(obj, page):
    arr = {
        'pages':obj.num_pages,
        'page':page,
        'has_prev':obj.page(page).has_previous(),
        'prev_num':obj.page(page).previous_page_number() if obj.page(page).has_previous() else 0,
        'has_next':obj.page(page).has_next(),
        'next_num':obj.page(page).next_page_number() if obj.page(page).has_next() else page
    }
    return arr

# Функция на замену пробелов на "-", в случае если придется генерировать урл с названием чего либо
def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)

# функция на замену значений типа транзакций, полученным по апи
def movementTranslate(m):
    arr = {'charge':'Пополнение','withdraw':'Вывод','payment':'Перевод'}
    return arr[m]

# Функция шифрования пароля в мд5
def hashpass(password):
    salt = '69hdaw@e21e2'
    new_pass = password + salt
    h = hashlib.md5(new_pass.encode())
    return h.hexdigest()

# Функция шифрования ссылки на csv файл транзакций
def hashcsv(user_id):
    salt = 'j12090d)()(@'
    link = str(user_id) + salt
    h = hashlib.md5(link.encode())
    return 'static/upload/csv/' + h.hexdigest() + '.csv'

# Функция шифрования файла фото профиля
def hashprofile(user_id):
    salt = 'pp12oj321jp)('
    link = str(user_id) + salt
    h = hashlib.md5(link.encode())
    return h.hexdigest()

# Функция на слияние двух списков в нужный мне формат (не используется)
def mergeTwoListsAsDict(list1, list2):
    dict1 = {k: {'name': v} for k, v in enumerate(list1)}
    dict2 = {k: {'id': v} for k, v in enumerate(list2)}
    return {k: {**v, **dict2[k]} for k, v in dict1.items()}

# Функция конвертации таймстампа в дату
def timeToDate(time):
    timestamp = datetime.fromtimestamp(time)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

# Функция ковертации даты в таймстамп
def dateToTime(time):
    return timec.mktime(datetime.strptime(time, "%Y-%m-%d").timetuple())

# Класс для работы с апи
class API():
    url = 'https://apis-dev.maxwallet.ru/' # Урл апи
    api_key = '????????' # Апи ключ
    headers = {"Content-Type" : "application/json", "X-API-KEY" : api_key} # Заголовки

    # Конструктор, в который передаю название метода для исполнения
    def __init__(self, method, body):
        self.method = method
        self.url = self.url + self.method
        self.body = body


    # Метод для гет запроса
    def get(self):
        #response = requests.get(self.url, headers=self.headers, params=self.body)
        #return response.json()
        return ''

    # Метод для пост запроса
    def post(self):
        #response = requests.post(self.url, headers=self.headers, json=self.body)
        #return response.json()
        return ''

# Класс пользователей
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(_('phone number'), max_length=120, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    email = models.CharField(max_length=120, blank=True, null=True)
    identity = models.TextField(blank=True, null=True)
    confirmation = models.IntegerField(default=0)
    roots = models.IntegerField(default=1)
    secret_id = models.TextField(blank=True, null=True)
    secret_key = models.TextField(blank=True, null=True)
    self_employed_approve = models.IntegerField(blank=True, null=True)
    rate = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    def __str__(self):
        return self.phone

# Класс кошельков юзера
class Wallets(models.Model):
    wallet_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.CharField(max_length=255, default=0)
    status = models.IntegerField()
    user_id = models.IntegerField()
    comment = models.CharField(max_length=192, blank=True, null=True)
    secret_id = models.CharField(max_length=255, blank=True, null=True)
    deleted = models.IntegerField(default=1)

    def __init__(self, *args, **kwargs):
        super(Wallets, self).__init__(*args, **kwargs)

# Класс транзакций юзера
class Transactions(models.Model):
    wallet_sender_id = models.IntegerField(blank=True, null=True)
    wallet_reciever_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()
    movement_type = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    commission = models.CharField(max_length=255)
    time = models.IntegerField(default=timec.time())
    secret_t = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(default=1)
    card = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    link = models.IntegerField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Transactions, self).__init__(*args, **kwargs)

# Класс для работы с смс
class Sms_approve(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    code = models.IntegerField()
    action = models.CharField(max_length=255, blank=True, null=True)
    time = models.IntegerField(default=timec.time())
    status = models.IntegerField(default=0)
    phone = models.CharField(max_length=255)
    api_url = 'https://api.smsgold.ru' # Урл апи смс сервиса
    method_getToken = '????????????' # Токен
    method_send = '/sms/v1/message/sendOne' # Метод для отправки смс

    def __init__(self, *args, **kwargs):
        super(Sms_approve, self).__init__(*args, **kwargs)
        self.generate_code()

    # Сгенерировать код
    def generate_code(self):
        self.code = 1111
        #self.code = random.randint(1000,9999)

    # Обновить время отправления смс, при повторной отправке
    def update_time(self):
        self.time = timec.time()

    # Метод для отправки смс
    def send_sms(self):
        """
        headers = {"Content-Type" : "application/json", "charset" : "utf-8", "X-SDK" : "python | 0.0.1"}
        url = self.api_url + self.method_getToken
        response = requests.get(url, headers=headers)
        response = response.json()
        accessToken = response['accessToken']
        
        body = {
            'channel' : 'sms',
            'sms_text' : self.code,
            'viber_text' : '',
            'sms_sender' : 'SmsGold',
            'viber_sender' : '',
            'phone' : self.phone
        }

        headers['Authorization'] = 'Bearer ' + accessToken
        url = self.api_url + self.method_send

        response = requests.post(url, headers=headers, json=body)
        response = response.json()
        """
        return ''