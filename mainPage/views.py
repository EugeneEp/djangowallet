from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from . models import hashpass, mergeTwoListsAsDict, Sms_approve, API, decor, CustomUser
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
import time
import re
import json
from django.http import HttpResponse

def index(request):
	return render(request, 'mainPage/index.html')\

def info(request, page):
	return render(request, 'mainPage/'+page+'.html')

@csrf_exempt
def sms(request):
	if request.method == 'POST':
		timelimit = int(time.time())
		phone = request.POST['phone']
		sms_type = request.POST['type'] 

		phone = re.sub("\D", "", phone)

		if len(str(phone)) < 11:
			return HttpResponse(json.dumps({'error':'Телефон введен не верно'}))

		re_sms = Sms_approve.objects.filter(phone=phone).filter(action=sms_type).first()

		# Было ли отправлено смс по этому номеру, на конкретное действие
		if re_sms:
			if (timelimit - re_sms.time) < 60:
				return HttpResponse(json.dumps({'error':'Повторное смс будет доступно через 60 секунд'}))
			elif re_sms.action == 'reg' and re_sms.status == 1:
				return HttpResponse(json.dumps({'error':'Такой пользователь уже зарегистрирован'})) # Если код уже использован и подтвержден
			else:
				re_sms.generate_code()
				re_sms.update_time()
				re_sms.status = 0
				# Отправить повторное смс по апи
				#send = re_sms.send_sms()
				re_sms.save()
		else:
			if request.user.is_authenticated:
				sms = Sms_approve(user_id=user.id, action=sms_type, phone=phone)
			else:
				sms = Sms_approve(action=sms_type, phone=phone)

			# Отправить смс по апи
			#send = sms.send_sms()
			sms.save()

	else:
		return HttpResponse(json.dumps({'error':'Request method error'}))

	return HttpResponse(json.dumps({'success':'Успех'}))

@csrf_exempt
def sms_check(request):
	if request.method == 'POST':
		phone = request.POST['phone']
		phone = re.sub("\D", "", phone)
		sms_type = request.POST['type'] 
		code = request.POST['code']
		timelimit = int(time.time())

		sms = Sms_approve.objects.filter(phone=phone).filter(action=sms_type).filter(status=0).filter(code=code).first()

		if sms:
			if (timelimit - sms.time) > (60 * 60):
				return HttpResponse(json.dumps({'error':'Проверочный код истек, отправьте повторное смс'}))
			sms.status = 1
			sms.save()
		else:
			return HttpResponse(json.dumps({'error':'Код смс введен не верно'}))

	else:
		return HttpResponse(json.dumps({'error':'Request method error'}))

	return HttpResponse(json.dumps({'success':'Успех'}))

@csrf_exempt
def reg_user(request):
	if request.method == 'POST':
		phone = request.POST['phone']
		phone = re.sub("\D", "", phone)
		password = request.POST['password']
		confirm = request.POST['confirm']

		user = CustomUser.objects.filter(phone=phone).first()
		sms = Sms_approve.objects.filter(phone=phone).filter(action='reg').first()
		if sms:
			if sms.status == 0:
				return HttpResponse(json.dumps({'error':'Вы не подтвердили смс'}))
			if user and sms.status == 1:
				return HttpResponse(json.dumps({'error':'Такой пользователь уже зарегистрирован'}))
		else:
			return HttpResponse(json.dumps({'error':'Вы не отправили смс'}))

		if phone == '' or password == '' or confirm == '':
			return HttpResponse(json.dumps({'error':'Не все поля заполнены'}))
		if confirm != password:
			return HttpResponse(json.dumps({'error':'Пароли не совпадают'}))
		user = CustomUser.objects.create_user(phone=phone, password=password)

		# Добавить юзера в банк по апи
		#add_user = user.add_user()
		#if add_user['ok'] != True:
		#	return json.dumps({'error':'Не получилось добавить в систему'})

		user.save()

	return HttpResponse(json.dumps({'success':'Успех'}))

@csrf_exempt
def log_user(request):
	if request.method == 'POST':
		phone = request.POST['phone']
		phone = re.sub("\D", "", phone)
		password = request.POST['password']
		if phone == '' or password == '':
			return HttpResponse(json.dumps({'error':'Не все поля заполнены'}))
		user = authenticate(request, phone=phone, password=password)
		if user:
			if user.roots == 0:
				return HttpResponse(json.dumps({'error':'Вы не прошли подтверждение'}))
			login(request, user)
			return HttpResponse(json.dumps({'test':'User exist'}))
		else:
			return HttpResponse(json.dumps({'error':'Телефон и пароль не совпадают'}))
	else:
		return HttpResponse(json.dumps({'error':'Request method error'}))

@login_required(login_url='/')
def logout_user(request):
	logout(request)
	return redirect('/')