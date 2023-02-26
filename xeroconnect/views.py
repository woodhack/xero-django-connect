import traceback
import datetime
import json
import dateutil
from django.http import JsonResponse
from decimal import Decimal

from dateutil import tz
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.sessions.models import Session

from functools import wraps
from django.http import HttpResponseRedirect

from authlib.integrations.django_client import OAuth

# configure xero-python sdk client
from xero_python.accounting import AccountingApi, Account, Accounts, AccountType, Allocation, Allocations, BatchPayment, BatchPayments, BankTransaction, BankTransactions, BankTransfer, BankTransfers, Contact, Contacts, ContactGroup, ContactGroups, ContactPerson, CreditNote, CreditNotes, Currency, Currencies, CurrencyCode, Employee, Employees, ExpenseClaim, ExpenseClaims, HistoryRecord, HistoryRecords, Invoice, Invoices, Item, Items, LineAmountTypes, LineItem, Payment, Payments, PaymentService, PaymentServices, Phone, Purchase, Receipt, Receipts, TaxComponent, TaxRate, TaxRates, TaxType, TrackingCategory, TrackingCategories, TrackingOption, TrackingOptions, User, Users
from xero_python.assets import AssetApi, Asset, AssetStatus, AssetStatusQueryParam, AssetType, BookDepreciationSetting
from xero_python.project import ProjectApi, Amount, ChargeType, Projects, ProjectCreateOrUpdate, ProjectPatch, ProjectStatus, ProjectUsers, Task, TaskCreateOrUpdate, TimeEntryCreateOrUpdate
from xero_python.payrollau import PayrollAuApi, Employees, Employee, EmployeeStatus,State, HomeAddress
from xero_python.payrolluk import PayrollUkApi, Employees, Employee, Address, Employment
from xero_python.payrollnz import PayrollNzApi, Employees, Employee, Address, Employment, EmployeeLeaveSetup
from xero_python.file import FilesApi
from xero_python.finance import FinanceApi
from xero_python.api_client import ApiClient, serialize
from xero_python.api_client.configuration import Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.exceptions import AccountingBadRequestException, PayrollUkBadRequestException
from xero_python.identity import IdentityApi
from xero_python.utils import getvalue

from .utils import jsonify, serialize_model

# Configure oauth using authlib
oauth = OAuth()
xero = oauth.register(
    name="xero",
    version="2",
    client_id="",  # Enter your client ID
    client_secret="", # Enter your client secret
    endpoint_url="https://api.xero.com/",
    authorize_url="https://login.xero.com/identity/connect/authorize",
    access_token_url="https://identity.xero.com/connect/token",
    refresh_token_url="https://identity.xero.com/connect/token",
    # scope="offline_access openid profile email",
    scope="offline_access openid profile email accounting.transactions "
    "accounting.reports.read accounting.journals.read accounting.settings "
    "accounting.contacts accounting.attachments assets projects",
    server_metadata_url="https://identity.xero.com/.well-known/openid-configuration",
)


# configure xero-python sdk client
api_client = ApiClient(
    Configuration(
        debug=True,
        oauth2_token=OAuth2Token(
            client_id="", # Enter your client ID
            client_secret=""  # Enter your client secret
        ),
    ),
    pool_threads=1,
)

# Token details stored below, cosider changing to session etc. 
token_details = {'token': None,
                 'modified': True}


@api_client.oauth2_token_getter
def obtain_xero_oauth2_token():
    return token_details["token"]


@api_client.oauth2_token_saver
def store_xero_oauth2_token(token):
    token_details["token"] = token
    token_details['modified'] = True

def xero_token_required(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        xero_token = obtain_xero_oauth2_token()
        if not xero_token:
            return redirect("login")

        return function(*args, **kwargs)

    return decorator

@xero_token_required
def index(request):
    try:
        xero_access = dict(obtain_xero_oauth2_token() or {})
        return render(request, template_name='code.html')
        api_client.refresh_oauth2_token()
        return get_invoices(request)
    except Exception as e:
        print(e)
        return redirect("login")

def login(request):
    if not obtain_xero_oauth2_token():
        response = xero.authorize_redirect(request, redirect_uri="http://localhost:8000/callback")
        return response
    return redirect("home")


def oauth_callback(request):
    try:
        response = xero.authorize_access_token(request)
    except Exception as e:
        print(e)
        raise
    # todo validate state value
    if response is None or response.get("access_token") is None:
        return "Access denied: response=%s" % response
    store_xero_oauth2_token(response)
    return redirect ("home")

def logout(request):
    store_xero_oauth2_token(None)
    return redirect("login")

def get_connection_id():
    identity_api = IdentityApi(api_client)
    for connection in identity_api.get_connections():
        if connection.tenant_type == "ORGANISATION":
            return connection.id

@xero_token_required
def tenants(request):
    identity_api = IdentityApi(api_client)
    accounting_api = AccountingApi(api_client)
    asset_api = AssetApi(api_client)

    available_tenants = []
    for connection in identity_api.get_connections():
        tenant = serialize(connection)
        if connection.tenant_type == "ORGANISATION":
            organisations = accounting_api.get_organisations(
                xero_tenant_id=connection.tenant_id
            )
            tenant["organisations"] = serialize(organisations)

        available_tenants.append(tenant)

    return render(request, template_name=
        'output.html'
    )

@xero_token_required
def get_xero_tenant_id():
    token = obtain_xero_oauth2_token()
    if not token:
        return None

    identity_api = IdentityApi(api_client)
    for connection in identity_api.get_connections():
        if connection.tenant_type == "ORGANISATION":
            return connection.tenant_id

def disconnect(request):
    connection_id = get_connection_id()
    identity_api = IdentityApi(api_client)
    identity_api.delete_connection(
        id=connection_id
    )

    return redirect("home")

@xero_token_required
def refresh_token(request):
    xero_token = obtain_xero_oauth2_token()
    new_token = api_client.refresh_oauth2_token()
    return render(request, template_name=
        "output.html")
    """,
        code=jsonify({"Old Token": xero_token, "New token": new_token}),
        sub_title="token refreshed",
        )"""

# Accounting API's    
# Get Profit and Loss
@xero_token_required
def accounting_get_report_profit_and_loss(request):
    api_instance = AccountingApi(api_client)
    xero_tenant_id = get_xero_tenant_id()
    from_date = dateutil.parser.parse("2021-10-31")
    to_date = dateutil.parser.parse("2022-05-31")
    periods = '1'
    timeframe = 'MONTH'
    tracking_category_id = ''
    tracking_category_id_2 = ''
    tracking_option_id = ''
    tracking_option_id_2 = ''
    standard_layout = 'True'
    payments_only = 'False'
    
    try:
        api_response = api_instance.get_report_profit_and_loss(xero_tenant_id, from_date, to_date, periods, timeframe, tracking_category_id, tracking_category_id_2, tracking_option_id, tracking_option_id_2, standard_layout, payments_only)
        print(api_response)
        return render(request, template_name="code.html")
    except AccountingBadRequestException as e:
        print("Exception when calling AccountingApi->getReportProfitAndLoss: %s\n" % e)

# Get Balance Sheet
def accounting_get_report_balance_sheet(request):
    api_instance = AccountingApi(api_client)
    xero_tenant_id = get_xero_tenant_id()
    date = dateutil.parser.parse("2022-05-01")
    periods = '1'
    timeframe = 'MONTH'
    tracking_option_id_1 = ''
    tracking_option_id_2 = ''
    standard_layout = 'True'
    payments_only = 'False'
    
    try:
        api_response = api_instance.get_report_balance_sheet(xero_tenant_id, date, periods, timeframe, tracking_option_id_1, tracking_option_id_2, standard_layout, payments_only)
        print(api_response)
        return render(request, template_name="code.html")
    except AccountingBadRequestException as e:
        print("Exception when calling AccountingApi->getReportBalanceSheet: %s\n" % e)

"""
# Get contacts
def accounting_get_contacts():
    api_instance = AccountingApi(api_client)
    xero_tenant_id = 'YOUR_XERO_TENANT_ID'
    if_modified_since = dateutil.parser.parse("2020-02-06T12:17:43.202-08:00")
    where = 'ContactStatus=="ACTIVE"'
    order = 'Name ASC'
    ids = ["00000000-0000-0000-0000-000000000000"]
    include_archived = 'True'
    summary_only = 'True'
    search_term = 'searchTerm=Joe Bloggs'
    
    try:
        api_response = api_instance.get_contacts(xero_tenant_id, if_modified_since, where, order, ids, page, include_archived, summary_only, search_term)
        print(api_response)
    except AccountingBadRequestException as e:
        print("Exception when calling AccountingApi->getContacts: %s\n" % e)
"""
