from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='Index'),
	path('<str:page>/info', views.info, name='Info'),
	path('sms/', views.sms, name='Sms'),
	path('sms_check/', views.sms_check, name='SmsCheck'),
	path('reg_user/', views.reg_user, name='RegUser'),
	path('log_user/', views.log_user, name='LogUser'),
	path('logout_user/', views.logout_user, name='LogoutUser')
]
