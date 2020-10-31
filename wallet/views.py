from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from mainPage.models import CustomUser, Transactions, dateToTime, timeToDate, movementTranslate, paginatorParse, hashcsv
import json
from django.http import HttpResponse
from django.core.paginator import Paginator
import csv
import time as timec
import glob
from django.core.files.storage import FileSystemStorage

@login_required(login_url='/')
@csrf_exempt
def index(request):
	page = request.GET.get('page', '')
	page = int(page) if page and page.isdigit() else 1

	date_from = request.GET.get('from', '')
	date_end = request.GET.get('to', '')
	filters = []

	sql = 'SELECT * FROM "mainPage_transactions" WHERE user_id = '+str(request.user.id)

	if date_from and date_from != "":
		sql += ' AND time > ' + str(dateToTime(date_from))
	if date_end and date_end != "":
		sql += ' AND time < ' + str(dateToTime(date_end))

	sql += ' ORDER BY id DESC'

	transactions = []
	t = Transactions.objects.raw(sql)

	for i in t:
		i.time = timeToDate(i.time)
		i.movement_type = movementTranslate(i.movement_type)
		transactions.append(i)


	p = paginatorParse(Paginator(transactions, 8), page)

	context = {
		't' : transactions[page:8],
		'p' : p
	}

	return render(request, 'wallet/index.html', context)

@login_required(login_url='/')
@csrf_exempt
def profile(request):
	if request.method == 'GET':
		identity = {'fullname': '', 'passport': '', 'passportIssuedAt': ''}
		if request.user.identity:
			identity.update(json.loads(request.user.identity))

		context = {
			'identity' : identity
		}
		return render(request, 'wallet/profile.html', context)
	if request.method == 'POST':

		fullname = request.POST['fullname']
		passport = request.POST['passport']
		passportIssuedAt = request.POST['passportIssuedAt']

		if fullname == '' and passport == '' and passportIssuedAt == '':
			return HttpResponse(json.dumps({'error':'Не все поля заполнены'}))
		
		fullnameArr = fullname.split()
		passport = passport.replace(' ', '')

		if len(fullnameArr) < 3:
			return HttpResponse(json.dumps({'error':'ФИО введено не корректно'}))

		identity = {
			'fullname': fullname,
			'lastName': fullnameArr[0],
			'firstName': fullnameArr[1],
			'secondName': fullnameArr[2],
			'passport': passport,
			'passportIssuedAt':passportIssuedAt
		}

		identity = json.dumps(identity)

		user_query = CustomUser.objects.filter(id=request.user.id).first()
		user_query.identity = identity

		user_query.save()

		return HttpResponse(json.dumps({'success':'Данные успешно отправлены'}))

@login_required(login_url='/')
@csrf_exempt
def charge(request):
	if request.method == 'GET':
		return render(request, 'wallet/charge.html')
	if request.method == 'POST':
		return HttpResponse(json.dumps({'error':'Метод еще не готов'}))

@login_required(login_url='/')
@csrf_exempt
def donate(request):
	if request.method == 'GET':
		return render(request, 'wallet/donate.html')
	if request.method == 'POST':
		return HttpResponse(json.dumps({'error':'Метод еще не готов'}))

@login_required(login_url='/')
@csrf_exempt
def moneybank(request):
	if request.method == 'GET':
		return render(request, 'wallet/moneybank.html')
	if request.method == 'POST':
		return HttpResponse(json.dumps({'error':'Метод еще не готов'}))

@login_required(login_url='/')
@csrf_exempt
def partner(request):
	if request.method == 'GET':
		return render(request, 'wallet/partner.html')

@login_required(login_url='/')
@csrf_exempt
def transfer(request):
	if request.method == 'GET':
		return render(request, 'wallet/transfer.html')
	if request.method == 'POST':
		return HttpResponse(json.dumps({'error':'Метод еще не готов'}))

@login_required(login_url='/')
@csrf_exempt
def csv_transactions(request):
	if request.method == 'POST':
		try:

			mylist = [['Дата', 'Тип транзакции', 'Статус', 'Сумма']]

			date_from = request.POST['from']
			date_end = request.POST['to']
			filters = []

			sql = 'SELECT * FROM "mainPage_transactions" WHERE user_id = '+str(request.user.id)

			if date_from and date_from != "":
				sql += ' AND time > ' + str(dateToTime(date_from))
			if date_end and date_end != "":
				sql += ' AND time < ' + str(dateToTime(date_end))

			sql += ' ORDER BY id DESC'

			t = Transactions.objects.raw(sql)
			for i in t:
				i.time = str(timeToDate(i.time))
				i.movement_type = str(movementTranslate(i.movement_type))
				mylist.append([i.time, i.movement_type, i.status, i.amount])
						
			link = hashcsv(request.user.id)

			with open('wallet/'+link, 'w', newline='', encoding='cp1251') as myfile:
				wr = csv.writer(myfile, delimiter=";")
				for x in mylist:
					wr.writerow(x)

			return HttpResponse(json.dumps({'link': '/' + link + '?t=' + str(timec.time())}))

		except Exception as e:
			print(str(e))
			return HttpResponse(json.dumps({'error':'Что-то пошло не так'}))
	else:
		return HttpResponse(json.dumps({'error':'Метод не найден'}))

@login_required(login_url='/')
@csrf_exempt
def profile_picture(request):
	if request.method == 'POST':
		if request.FILES['img']:
			for x in glob.glob('wallet/static/upload/profile/' + str(request.user.id) + '.png'):
				os.unlink(x)
			f = request.FILES['img']
			ext = f.name.split('.')[1]
			filename = 'wallet/static/upload/profile/' + str(request.user.id) + '.png'
			try:
				fs = FileSystemStorage()
				fs.save(filename, f)
			except Exception as e:
				print(str(e))
				return HttpResponse(json.dumps({'error':'Что-то пошло не так'}))
				
			return HttpResponse(json.dumps({'success':'Успех'}))
		else:
			return HttpResponse(json.dumps({'error':'Файл не найден'}))
	else:
		return HttpResponse(json.dumps({'error':'Метод не найден'}))