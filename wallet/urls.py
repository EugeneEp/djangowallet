from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='walletIndex'),
	path('charge/', views.charge, name='walletCharge'),
	path('donate/', views.donate, name='walletDonate'),
	path('moneybank/', views.moneybank, name='walletMoneybank'),
	path('partner/', views.partner, name='walletPartner'),
	path('transfer/', views.transfer, name='walletTransfer'),
	path('profile/', views.profile, name='walletProfile'),
	path('csv/', views.csv_transactions, name='walletCSV'),
	path('picture/', views.profile_picture, name='walletPicture')
]