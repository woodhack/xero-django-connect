"""xeroWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *

urlpatterns = [
    path('home', index, name='home'),
    path('login', login, name='login'),
    path('callback', oauth_callback, name='callback'),
    path('logout', logout, name='logout'),
    path('tenants', tenants, name='tenants'),
    path('refresh-token', refresh_token, name='refresh_token'),
    path('disconnect', disconnect, name='disconnect'),
    path('accounting-get-report-profit-and-loss', accounting_get_report_profit_and_loss, name='accounting_get_report_profit_and_loss'),
    path('accounting-get-report-balance-sheet', accounting_get_report_balance_sheet, name='accounting_get_report_balance_sheet'),
]
