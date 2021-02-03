from django.shortcuts import render,redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from django.views import View
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.core import serializers
from django.db import connection
import json
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models.functions import TruncDay
from django.utils.timezone import localtime, now
from django.db.models import Max, Sum
from django.utils.formats import get_format
from django.forms.fields import DateField,DateTimeField
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import djqscsv
from django.db.models import Count
import collections
import decimal
import pytz
from django.db.models import Prefetch
from payments.models import PayIn
from products.models import Product
from users.models import User
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from bids.models import BidEntry,InvalidBid
from winners.models import Winner
from bids.models import Bid,BidEntry,UserBid,UssdDial,Survey
from messaging.models import OutgoingSMS
from django.views.decorators.csrf import csrf_exempt
from factory.helpers import Helpers
from messaging.tasks import send_unqiue_bidders_sms
helpers = Helpers()
import random
import string
from django.contrib.auth.mixins import UserPassesTestMixin,AccessMixin
from django.conf import settings

EXCLUDE_PHONES = ('',)
EXCLUDE_AMOUNTS = ('',)


def standardize_msisdn(msisdn):
	if msisdn.startswith('0'):
		return '254' + msisdn.lstrip('0').replace(' ','').strip()
	elif msisdn.startswith('+254'):
		return msisdn.lstrip('+').replace(' ','').strip()

	else:
		return msisdn.replace(' ','').strip()


def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return redirect('login')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'admin/change_password.html', {
		'form': form
	})

def make_utc(dt):
	if dt.is_naive():
		dt = timezone.make_aware(dt)
	return dt.astimezone(pytz.utc)


def parse_date(date_str):
	"""Parse date from string by DATE_INPUT_FORMATS of current language"""
	for item in get_format('DATE_INPUT_FORMATS'):
		try:
			return datetime.strptime(date_str, item)
		except (ValueError, TypeError):
			continue

	return None


def dictfetchall(cursor):
	"Return all rows from a cursor as a dict"
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]


def json_serial(obj):
	"""JSON serializer for objects not serializable by default json code"""
	if isinstance(obj, (datetime, date)):
		return obj.isoformat()
	elif isinstance(obj, decimal.Decimal):
		return float(obj)
	raise TypeError("Type %s not serializable" % type(obj))




class Dashboard(View):

	def post(self,request):
		pass

	def get(self,request):

		today = date.today()


		current_year = datetime.now().year

		current_month = datetime.now().month

		# graphs
		cursor = connection.cursor()

		bids_per_day_of_a_month = []
		monthly_bids_sum ={}
		cursor = connection.cursor()
		
		# mothly bids
		cursor.execute("""SELECT DATE(created_at) as date, count(id) as value
				FROM bids_bidentry
				WHERE EXTRACT(MONTH from created_at) = %s AND EXTRACT(YEAR from created_at)=%s
				GROUP BY DATE(created_at)""", [current_month, current_year])

		bids_results = dictfetchall(cursor)


		for result in bids_results:

			bids_per_day_of_a_month.append(result)

			monthly_bids_sum = json.dumps(
				bids_per_day_of_a_month, default=json_serial)

			cursor.close()
		

		#mothly deposists

		cursor = connection.cursor()

		monthly__deposits_datalist = []
		monthly_deposits_sum ={}



		cursor.execute("""SELECT DATE(created_at) as date,sum(transaction_amount) as value
				FROM payments_payin
				WHERE EXTRACT(MONTH from created_at) = %s AND EXTRACT(YEAR from created_at)=%s
				GROUP BY DATE(created_at)""", [current_month, current_year])

		monthly__deposits_results = dictfetchall(cursor)

		for result in monthly__deposits_results:

			monthly__deposits_datalist.append(result)

			monthly_deposits_sum = json.dumps(
				monthly__deposits_datalist, default=json_serial)

			cursor.close()

		#end monthly deposits

		

		# hours_count={}
		# hours_tickets_list=[]

		# cursor=connection.cursor()
		# today=date.today()
		# today_formated=today.strftime("%Y-%m-%d")
		# cursor.execute("""SELECT hour(created_at) as hour, count('id') as count
		# FROM `tickets_ticket`
		# WHERE game_id = "{}" AND DATE(created_at)="{}"
		# GROUP BY hour( created_at ) , day(created_at )""".format(game_id,today_formated))

		# hourly_tickets_results=dictfetchall(cursor)
		# for result in hourly_tickets_results:

		# 	hours_tickets_list.append(result)

		# hourly_tickets_data=json.dumps(hours_tickets_list)

		# cursor.close()

		#end hourly tickets


		data={
				'monthly_deposits_data': monthly_deposits_sum,
				'monthly_bids_data':monthly_bids_sum
				

			}

		return render(request,'admin_portal/dashboard.html',data)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)




def totals(request):
	cst = pytz.timezone('Africa/Nairobi')
	today = date.today()
	import datetime
	yesterday = date.today() - timezone.timedelta(hours=7)
	#utls

	# cst = pytz.timezone('Africa/Nairobi')
	# today = date.today()

	# current_year = today.year

	# current_month = today.month

	#end utils

	total_deposits = PayIn.get_total_deposits()

	#today deposists
	today_deposits = PayIn.objects.filter(created_at__gt=yesterday).aggregate(
		Sum('transaction_amount'))['transaction_amount__sum']

	# today bids
	today_bids = BidEntry.objects.filter(created_at__gt=yesterday).count()

	#total bids
	total_bids = BidEntry.objects.count()

	#today users
	today_users = User.objects.filter(date_created__gt=yesterday).count()



	data = {
		'total_deposits':total_deposits,
		'today_deposits':today_deposits,
		'total_bids':total_bids,
		'today_bids':today_bids,
		'today_users':today_users,
		


	}

	return JsonResponse(data)


class Winners(View):

	def get(self, request):
			
		fields = Winner.objects.values(
			'user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			'bid__code', 
			'bid__product__name',
			'bid__product__price',
			'winning_value',
			'created_at'
			)

		return render(request, 'admin_portal/winners.html', {'data': fields})

		# return render (request,'admin_portal/Users.html',{'data':all_Users})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(Winners, self).dispatch(request, *args, **kwargs)


def process_winners(request):
	includes = ['user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			'bid__code', 
			'bid__product__name',
			'bid__product__price',
			'winning_value',
			'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		Winner._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = Winner.objects.filter(Q(user__profile__first_name__icontains=global_search) |
											Q(user__profile__middle_name__icontains=global_search) |
											Q(user__profile__last_name__icontains=global_search) |
											Q(user__phone_number__icontains=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].values('user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			'bid__code', 
			'bid__product__name',
			'bid__product__price',
			'winning_value',
			'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Winner.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects = Winner.objects.all()

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by('-created_at')[start:start + length].values('user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			'bid__code', 
			'bid__product__name',
			'bid__product__price',
			'winning_value',
			'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Winner.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

class ExportWinnersCsv(View):

	def get(self, request):

		field_header_map = {'user__phone_number': 'Phone Number',
							'user__profile__first_name': 'First Name',
							'user__profile__middle_name': 'Middle Name',
							'user__profile__last_name': 'Last Name',
							'bid__code':'Bid Code',
							'bid__product__name':'Product Won',
							'bid__product__price':'Product RRP',
							'winning_value': "Winning Value",
							'created_at': 'Date Won'
						   }
		field_serializer_map = {'created_at': (lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = Winner.objects.values('user__phone_number', 'user__profile__first_name',
								'user__profile__middle_name', 'user__profile__last_name', 
								'bid_code', 'bid__product__name','bid__product__price','winning_value',
								'created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportWinnersCsv, self).dispatch(*args, **kwargs)


class Products(View):

	def get(self, request):

		fields = Product.objects.values('code',
				'name',
				'price',
				'description',
				'offered',
				'image',
				'created_at')

		return render(request, 'admin_portal/products.html', {'data': fields})

		# return render (request,'admin_portal/Users.html',{'data':all_Users})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(Products, self).dispatch(request, *args, **kwargs)


def process_products(request):
	includes = ['code',
				'name',
				'price',
				'description',
				'offered',
				'image',
				'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		Product._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = Product.objects.filter(
											Q(code__icontains=global_search) |
											
											Q(name__icontains=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].values('code',
				'name',
				'price',
				'description',
				'offered',
				'image',
				'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Product.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:



		all_objects = Product.objects.all()

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by(order_direction + column)[start:start + length].values('code',
				'name',
				'price',
				'description',
				'offered',
				'image',
				'created_at'):
			ret = [i[j] for j in columns]

			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Product.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

class ExportTicketsCsv(View):

	def get(self, request):

		field_header_map = {'user__phone_number': 'Phone Number',
							'user__profile__first_name': 'First Name',
							'user__profile__middle_name': 'Middle Name',
							'user__profile__last_name': 'Last Name',
							'lot__name': 'Lot',
							'game__name': 'Game',
							'number': 'Product Number',
							'created_at': 'Date Won'
						   }
		field_serializer_map = {'created_at': (lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = Product.objects.values('user__phone_number', 'user__profile__first_name',
				'user__profile__middle_name', 'user__profile__last_name','game__name',\
					'lot__name', 'number', 'created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportTicketsCsv, self).dispatch(*args, **kwargs)


class Players(View):

	def get(self, request):

		fields = User.objects.values('phone_number', 'profile__first_name','profile__middle_name','profile__last_name','date_created')
		all_users = User.objects.count()

		return render(request, 'admin_portal/players.html', {'data': fields,'all_users':all_users})

		# return render (request,'admin_portal/Users.html',{'data':all_Users})

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(Players, self).dispatch(request, *args, **kwargs)


def process_players(request):
	includes = ['phone_number', 'profile__first_name','profile__middle_name','profile__last_name','date_created', ]
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		User._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		

		all_objects = User.objects.filter(
											Q(phone_number__icontains=global_search) |
											Q(profile__first_name__icontains=global_search) |
											Q(profile__middle_name__icontains=global_search) |
											Q(profile__last_name__icontains=global_search)).all()

		columns = [i for i in includes]

		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].values('phone_number', 'profile__first_name','profile__middle_name','profile__last_name','date_created'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = User.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects = User.objects.all()
		# all_objects = User.objects.prefetch_related(Prefetch('playeraccounts_set')).all()

		columns = [i for i in includes]
		
		objects = []
		for i in all_objects.order_by('-date_created')[start:start + length].values('phone_number', 'profile__first_name','profile__middle_name','profile__last_name','date_created'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = User.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

class ExportPlayersCsv(View):

	def get(self, request):

		field_header_map = {
							'phone_number':'Phone Number',
							'profile__first_name':'First Name',
							'profile__last_name': 'Last Name',
							'date_created': 'Date Registered',
					  }
		field_serializer_map = {'date_created': (
			lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = User.objects.values('phone_number', 'profile__first_name','profile__last_name','date_created').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportPlayersCsv, self).dispatch(*args, **kwargs)

class IncomingPayments(View):
   


	def get(self, request):

		fields = PayIn.objects.values(
			'msisdn', 'first_name',  'last_name', 'transaction_id', 'transaction_amount', 'bill_reference_number',  'created_at')

		return render(request, 'admin_portal/payins.html', {'data': fields})

		# return render (request,'admin_portal/Playerss.html',{'data':all_Playerss})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(IncomingPayments, self).dispatch(request, *args, **kwargs)


def process_payins(request):
	includes = ['msisdn', 'first_name',  'last_name',
			 'transaction_id', 'transaction_amount', 'bill_reference_number',  'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		PayIn._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = PayIn.objects.filter(Q(transaction_id__icontains=global_search) |
										Q(transaction_amount__icontains=global_search) |
										Q(bill_reference_number__icontains=global_search) |
										Q(msisdn__icontains=global_search) |
										Q(first_name__icontains=global_search) |
										Q(first_name__icontains=global_search) |
										Q(last_name__icontains=global_search) |
										Q(middle_name__icontains=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].values():
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = PayIn.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=PayIn.objects.values(
			'msisdn', 'first_name',  'last_name', 'transaction_id', 'transaction_amount', 'bill_reference_number',  'created_at')

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by('-created_at')[start:start + length].values():
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = PayIn.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

class ExportPayInsCsv(View):

	def get(self, request):

		field_header_map = {'msisdn': 'Phone Number',
							'transaction_amount': 'Amount',
							'transaction_id':'Transaction ID',
							'bill_reference_number':'Bill Ref No.',
							'first_name':'First Name',
							'middle_name': 'Middle Name',
							'last_name':'Last Name',
							'created_at': 'Transaction Date',
							}
		field_serializer_map = {'created_at': (lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}


		qs = PayIn.objects.values('msisdn','transaction_amount','transaction_id','bill_reference_number',\
							   'first_name','last_name','created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportPayInsCsv, self).dispatch(*args, **kwargs)

#Payouts

class OutgoingPayments(View):

	def get(self, request):

		fields = Payout.objects.values(
			'user__profile__first_name', 'user__phone_number', 'user__profile__last_name', 'transaction_id', 'amount', 'created_at')

		return render(request, 'admin_portal/payouts.html', {'data': fields})

		# return render (request,'admin_portal/Playerss.html',{'data':all_Playerss})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(OutgoingPayments, self).dispatch(request, *args, **kwargs)


def process_payouts(request):
	includes = ['user__profile__first_name',\
				'user__profile__last_name', 'status', 'amount', 'user__phone_number','created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		Payout._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = Payout.objects.filter(Q(status__icontains=global_search) |
										Q(amount__icontains=global_search) |
										Q(user__phone_number__icontains=global_search) |
										Q(user__profile__first_name__icontains=global_search) |
										Q(user__profile__last_name__icontains=global_search) |
										Q(user__profile__middle_name__icontains=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].values('user__profile__first_name',\
				'user__profile__last_name', 'status', 'amount', 'user__phone_number','created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Payout.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=Payout.objects.values(
			'user__profile__first_name',\
				'user__profile__last_name', 'status', 'amount', 'user__phone_number','created_at')


		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by(order_direction + column)[start:start + length].values('user__profile__first_name',\
				'user__profile__last_name', 'status', 'amount', 'user__phone_number','created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Payout.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

class ExportPayOutsCsv(View):

	def get(self, request):

		field_header_map = {'user__phone_number': 'Phone Number',
							'amount': 'Amount',
							'transaction_id':'Transaction ID',
							'user__profile__first_name':'First Name',
							'user__profile__middle_name': 'Middle Name',
							'user__profile__last_name':'Last Name',
							'created_at': 'Transaction Date',
							}
		field_serializer_map = {'created_at': (lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}


		qs = Payout.objects.values('user__phone_number','amount','transaction_id',\
							   'user__profile__first_name', 'user__profile__middle_name','user__profile__last_name','created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportPayOutsCsv, self).dispatch(*args, **kwargs)


class Transactions(View):
	
	def get(self, request):

		fields = Transaction.objects.values(
			'user__profile__first_name',  'user__phone_number', 'transaction_id','transaction_type', 'amount', 'created_at')

		return render(request, 'admin_portal/transactions.html', {'data': fields})

		# return render (request,'admin_portal/Playerss.html',{'data':all_Playerss})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(Transactions, self).dispatch(request, *args, **kwargs)


def process_transactions(request):
	includes = ['user__profile__first_name',  'user__phone_number', 
	'transaction_id','transaction_type', 'amount', 'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		Transaction._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = Transaction.objects.filter(Q(user__phone_number__icontains=global_search) |
										Q(amount__icontains=global_search) |
										Q(transaction_id__icontains=global_search) |
										Q(transaction_type__icontains=global_search) |
										Q(user__profile__first_name__icontains=global_search) |
										Q(user__profile__last_name__icontains=global_search) |
										Q(user__profile__middle_name__icontains=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].values('user__profile__first_name', 
		'user__phone_number', 'transaction_id',
		'transaction_type', 'amount', 'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = PayIn.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=Transaction.objects.values(
			'user__profile__first_name',  'user__phone_number',
			 'transaction_id','transaction_type', 'amount', 'created_at')

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by(order_direction + column)[start:start + length].values('user__profile__first_name', 
		'user__phone_number', 'transaction_id',
		'transaction_type', 'amount', 'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Transaction.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

class ExportTransactionsCsv(View):

	def get(self, request):

		field_header_map = {'msisdn': 'Phone Number',
							'transaction_amount': 'Amount',
							'transaction_id':'Transaction ID',
							'bill_reference_number':'Bill Ref No.',
							'first_name':'First Name',
							'middle_name': 'Middle Name',
							'last_name':'Last Name',
							'created_at': 'Transaction Date',
							}
		field_serializer_map = {'created_at': (lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}


		qs = PayIn.objects.values('msisdn','transaction_amount','transaction_id','bill_reference_number',\
							   'first_name','last_name','created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportPayInsCsv, self).dispatch(*args, **kwargs)


class Bids(View):
	
	def get(self, request):
			
		fields = Bid.objects.values(
			'code',  'ref_no', 'product__name',
			'critical_mass', 'is_open',
			'is_critical_mass_passed', 
			'open_at','closes_at')

		return render(request, 'admin_portal/bids.html', {'data': fields})

		# return render (request,'admin_portal/Playerss.html',{'data':all_Playerss})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(Bids, self).dispatch(request, *args, **kwargs)


def process_bids(request):
	includes = ['code',  'ref_no', 'product__name',
			'critical_mass', 'is_open',
			'is_critical_mass_passed', 
			'open_at','closes_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		Bid._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = Bid.objects.filter(Q(code__icontains=global_search) |
										Q(duration=global_search) |
										Q(ref_no__icontains=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].values('code',  'ref_no', 'product__name',
			'critical_mass', 'is_open',
			'is_critical_mass_passed', 
			'open_at','closes_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Bid.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=Bid.objects.values(
			'code',  'ref_no', 'product__name',
			'critical_mass', 'is_open',
			'is_critical_mass_passed', 
			'open_at','closes_at')

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by('-created_at')[start:start + length].values('code',  'ref_no', 'product__name',
			'critical_mass', 'is_open',
			'is_critical_mass_passed', 
			'open_at','closes_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Bid.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

class ExportDrawsCsv(View):

	def get(self, request):

		field_header_map = {'msisdn': 'Phone Number',
							'transaction_amount': 'Amount',
							'transaction_id':'Transaction ID',
							'bill_reference_number':'Bill Ref No.',
							'first_name':'First Name',
							'middle_name': 'Middle Name',
							'last_name':'Last Name',
							'created_at': 'Transaction Date',
							}
		field_serializer_map = {'created_at': (lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}


		qs = PayIn.objects.values('msisdn','transaction_amount','transaction_id','bill_reference_number',\
							   'first_name','last_name','created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportPayInsCsv, self).dispatch(*args, **kwargs)



class AllBids(View):
	
	def get(self, request):
			
		fields = UserBid.objects.values(
			'bid_entry__user__phone_number','bid_entry__user__profile__first_name',
			'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
			'bid_entry__bid__code', 'amount',
			'source',
			'bid_entry__bid__product__price', 
			'created_at')

		return render(request, 'admin_portal/all-bids.html', {'data': fields})

		# return render (request,'admin_portal/Playerss.html',{'data':all_Playerss})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(AllBids, self).dispatch(request, *args, **kwargs)


def process_all_bids(request):
	includes = ['bid_entry__user__phone_number','bid_entry__user__profile__first_name',
				'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
				'bid_entry__bid__code', 'amount',
				'source',
				'bid_entry__bid__product__price', 
				'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		UserBid._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = UserBid.objects.filter(
				   Q(bid_entry__user__phone_number__icontains=global_search) |
				   Q(bid_entry__user__profile__first_name=global_search) |
				   Q(source__icontains = global_search) |
				   Q(bid_entry__user__profile__last_name=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].\
				values('bid_entry__user__phone_number','bid_entry__user__profile__first_name',
				'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
				'bid_entry__bid__code', 'amount',
				'source',
				'bid_entry__bid__product__price', 
				'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = UserBid.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=UserBid.objects.values(
				'bid_entry__user__phone_number','bid_entry__user__profile__first_name',
				'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
				'bid_entry__bid__code', 'amount',
				'source',
				'bid_entry__bid__product__price', 
				'created_at')

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by('-created_at')[start:start + length].\
			values('bid_entry__user__phone_number','bid_entry__user__profile__first_name',
				'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
				'bid_entry__bid__code', 'amount',
				'source',
				'bid_entry__bid__product__price', 
				'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = UserBid.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})



class ActiveBids(View):
	
	def get(self, request):
			
		fields = UserBid.objects.filter(bid_entry__bid__is_open=True).values(
			'bid_entry__user__phone_number','bid_entry__user__profile__first_name',
			'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
			'bid_entry__bid__code', 'amount',
			'source',
			'bid_entry__bid__product__price', 
			'created_at')

		return render(request, 'admin_portal/active-bids.html', {'data': fields})

		# return render (request,'admin_portal/Playerss.html',{'data':all_Playerss})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(ActiveBids, self).dispatch(request, *args, **kwargs)


def process_active_bids(request):
	includes = ['bid_entry__user__phone_number','bid_entry__user__profile__first_name',
				'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
				'bid_entry__bid__code', 'amount',
				'source',
				'bid_entry__bid__product__price', 
				'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		UserBid._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = UserBid.objects.filter(bid_entry__bid__is_open=True).\
			filter(Q(bid_entry__user__phone_number__icontains=global_search) |
				   Q(bid_entry__user__profile__first_name=global_search) |
				   Q(source__icontains = global_search) |
				   Q(bid_entry__user__profile__last_name=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.filter(bid_entry__bid__is_open=True).order_by(order_direction + column)[start:start + length].\
				values('bid_entry__user__phone_number','bid_entry__user__profile__first_name',
				'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
				'bid_entry__bid__code', 'amount',
				'source',
				'bid_entry__bid__product__price', 
				'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = UserBid.objects.filter(bid_entry__bid__is_open=True).count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=UserBid.objects.filter(bid_entry__bid__is_open=True).values(
				'bid_entry__user__phone_number','bid_entry__user__profile__first_name',
				'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
				'bid_entry__bid__code', 'amount',
				'source',
				'bid_entry__bid__product__price', 
				'created_at')

		columns = [i for i in includes]
		objects = []
		for i in all_objects.filter(bid_entry__bid__is_open=True).order_by('-created_at')[start:start + length].\
			values('bid_entry__user__phone_number','bid_entry__user__profile__first_name',
				'bid_entry__user__profile__last_name', 'bid_entry__bid__product__name',
				'bid_entry__bid__code', 'amount',
				'source',
				'bid_entry__bid__product__price', 
				'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = UserBid.objects.filter(bid_entry__bid__is_open=True).count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})




class UssdDials(View):
	
	def get(self, request):
			
		fields = UssdDial.objects.values(
			'phone_number',
			'no_of_dials',
			'last_dialed',
			'created_at')

		return render(request, 'admin_portal/ussd-dials.html', {'data': fields})

		# return render (request,'admin_portal/Playerss.html',{'data':all_Playerss})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(UssdDials, self).dispatch(request, *args, **kwargs)


def process_dials(request):
	includes = [
			'phone_number',
			'no_of_dials',
			'last_dialed',
			'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		UssdDial._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = UssdDial.objects.filter(
				   Q(phone_number__icontains=global_search) |
				   Q(no_of_dials=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].\
				values('phone_number',
					'no_of_dials',
					'last_dialed',
					'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = UssdDial.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=UssdDial.objects.values(
				'phone_number',
				'no_of_dials',
				'last_dialed',
				'created_at')

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by('-last_dialed')[start:start + length].\
			values('phone_number',
					'no_of_dials',
					'last_dialed',
					'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = UssdDial.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})


class ExportDialsCsv(View):

	def get(self, request):

		field_header_map = {
							'phone_number':'Phone Number',
							'no_of_dials':'Number of Dials',
							'last_dialed': 'Last Dial Time',
							'created_at': 'First Dial Time',
					  }
		field_serializer_map = {'created_at': (
			lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = UssdDial.objects.values('phone_number', 'no_of_dials','last_dialed','created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportDialsCsv, self).dispatch(*args, **kwargs)

class InvalidBids(View):

	def get(self, request):
			
		fields = InvalidBid.objects.filter(resolved=0).values(
			'id',
			'user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			# 'bid_value',
			'bill_ref_no',
			'notes',
			'created_at'
			)

		return render(request, 'admin_portal/invalid-bids.html', {'data': fields})

		# return render (request,'admin_portal/Users.html',{'data':all_Users})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(InvalidBids, self).dispatch(request, *args, **kwargs)


def process_invalid(request):
	includes = ['id','user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			# 'bid_value',
			'bill_ref_no',
			'notes',
			'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		InvalidBid._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = InvalidBid.objects.filter(resolved=0).filter(Q(user__profile__first_name__icontains=global_search) |
											Q(user__profile__middle_name__icontains=global_search) |
											Q(user__profile__last_name__icontains=global_search) |
											Q(user__phone_number__icontains=global_search)).all()

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].values('id','user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			# 'bid_value',
			'bill_ref_no',
			'notes',
			'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = InvalidBid.objects.filter(resolved=0).count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects = InvalidBid.objects.filter(resolved=0)

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by('-created_at')[start:start + length].values('id','user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			# 'bid_value',
			'bill_ref_no',
			'notes',
			'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = InvalidBid.objects.filter(resolved=0).count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

class ExportInvalidBidsCurrentCsv(View):

	def get(self, request):

		field_header_map = {

							'user__profile__first_name':'First Name',
							'user__profile__middle_name':'Middle Name',
							'user__profile__last_name': 'Last Name',
							'user__phone_number': 'Phone Number',
							# 'bid_value': 'Bid Value Entered',
							'bill_ref_no':'Bill Ref No.',
							'notes': 'Notes',
							'created_at': 'Bid Date',
					  }
		field_serializer_map = {'created_at': (
			lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = InvalidBid.objects.filter(resolved=0).values('user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			# 'bid_value',
			'bill_ref_no',
			'notes',
			'created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True,filename=f'Current Invalid Bids')

	def dispatch(self, *args, **kwargs):
		return super().dispatch(*args, **kwargs)


class ExportInvalidBidsArchivedCsv(View):

	def get(self, request):

		field_header_map = {
							'user__profile__first_name':'First Name',
							'user__profile__middle_name':'Middle Name',
							'user__profile__last_name': 'Last Name',
							'user__phone_number': 'Phone Number',
							# 'bid_value': 'Bid Value Entered',
							'bill_ref_no':'Bill Ref No.',
							'notes': 'Notes',
							'created_at': 'Bid Date',
					  }
		field_serializer_map = {'created_at': (
			lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = InvalidBid.objects.exclude(resolved=1).values('user__profile__first_name',
			'user__profile__middle_name',
			'user__profile__last_name',
			'user__phone_number', 
			# 'bid_value',
			'bill_ref_no',
			'notes',
			'created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True,filename=f'Archived Invalid Bids')

	def dispatch(self, *args, **kwargs):
		return super().dispatch(*args, **kwargs)


class OutBox(View):
	
	def get(self, request):
			
		fields = OutgoingSMS.objects.values(
			'phone_number',
			'text',
			'status',
			'identifier',
			'status_reason',
			'success',
			'created_at')

		return render(request, 'admin_portal/sms-outbox.html', {'data': fields})

		# return render (request,'admin_portal/Playerss.html',{'data':all_Playerss})
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(OutBox, self).dispatch(request, *args, **kwargs)


def process_outbox(request):
	includes = [
			'phone_number',
			'text',
			'status',
			'identifier',
			'status_reason',
			'success',
			'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		OutgoingSMS._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = OutgoingSMS.objects.filter(
				   Q(phone_number__icontains=global_search) |
				   Q(identifier__icontains=global_search) |
				   Q(status__icontains=global_search)).all()
		
				   

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].\
				values('phone_number',
					'text',
					'status',
					'identifier',
					'status_reason',
					'success',
					'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = OutgoingSMS.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=OutgoingSMS.objects.values(
				'phone_number',
				'text',
				'status',
				'identifier',
				'status_reason',
				'success',
				'created_at')

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by('-created_at')[start:start + length].\
			values('phone_number',
					'text',
					'status',
					'identifier',
					'status_reason',
					'success',
					'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = OutgoingSMS.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})


class ExportOutBoxCsv(View):

	def get(self, request):

		field_header_map = {
							'phone_number': 'Phone Number',
							'text':"Message",
							'status':'Status',
							'identifier':'Identifier',
							'status_reason':'Status Reason',
							'success':'Success',
							'created_at':'Date sent'
									}
		field_serializer_map = {'created_at': (
			lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = OutgoingSMS.objects.values('phone_number',
			'text',
			'status',
			'identifier',
			'status_reason',
			'success',
			'created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super(ExportOutBoxCsv, self).dispatch(*args, **kwargs)


class BidActions(UserPassesTestMixin,AccessMixin,View):
	raise_exception=True

	def test_func(self):
		return self.request.user.groups.filter(name=settings.BIDADMINS).exists()

	def generate_ref_no(self,sl=5):
		letters = string.ascii_uppercase
		return ''.join(random.choice(letters) for i in range(sl))

	def post(self,request):
		code = request.POST.get('code')
		create_similar = request.POST.get('create_similar')
		bid = helpers.get_bid_by_code(code)
		
		winner = helpers.get_min_unique_bid(bid)
		
		if not winner:
			winner = UserBid.objects.filter(bid_entry__bid=bid,bid_entry__bid__is_open=True).order_by('amount').first()
		data = {
			'firstname':winner.bid_entry.user.profile.first_name,
			'middlename':winner.bid_entry.user.profile.middle_name,
			'lastname':winner.bid_entry.user.profile.last_name,
			'phonenumber':winner.bid_entry.user.phone_number,
			'bidvalue':winner.amount
		}
		
		bid.is_open = False
		bid.save()
		helpers.create_winner(winner.bid_entry.user,bid,winner.amount)
		if create_similar:
			bid.pk = None
			bid.closes_at = timezone.now() + timedelta(days=5)
			bid.open_at = timezone.now()
			bid.created_at = timezone.now()
			bid.is_open = True
			bid.ref_no = self.generate_ref_no()
			bid.save()

		# send_unqiue_bidders_sms.delay(bid.id,winner.amount,winner.bid_entry.user.profile.first_name)
		return JsonResponse(data)

	def get(self,request):
		active_bids = helpers.get_active_bids()
		return render(request,'admin_portal/current_bids.html',{'active_bids':active_bids})

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

class Filters(View):

	def post(self,request):
		
		from_date = request.POST.get('from_date').strip()
		to_date = request.POST.get('to_date').strip()
		fld = DateTimeField()
		start_date=fld.to_python(from_date)
		end_date=fld.to_python(to_date)
		
		deposits_filter = PayIn.objects.filter(created_at__gt=start_date,created_at__lt=end_date)\
			.aggregate(Sum('transaction_amount')).get('transaction_amount__sum')
		
		f = PayIn.objects.filter(created_at__gt=start_date,created_at__lt=end_date)
		

		users_filter = User.objects.filter(date_created__gt=start_date,date_created__lt=end_date).count()
		bids_filter =BidEntry.objects.filter(created_at__gt=start_date,created_at__lt=end_date).count()
		data = {
			'deposits_filter':deposits_filter,
			'bids_filter':bids_filter,
			'users_filter':users_filter,
			
			


		}
		
		return JsonResponse(data)

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

class UniqueBids(UserPassesTestMixin,AccessMixin,View):
	raise_exception=True

	def test_func(self):
		return self.request.user.groups.filter(name=settings.BIDADMINS).exists()

	def get(self,request,bid_id):
		datalist = []
		unique_bids = UserBid.objects.filter(bid_entry__bid__id=bid_id).values('amount').annotate(amount_count=Count('amount')).filter(amount_count__lt=2).order_by('amount')[:500]
		for ub in unique_bids:
			data = {}
			amount = ub.get('amount')
			entry = UserBid.objects.filter(bid_entry__bid__id=bid_id).get(amount=amount)
			has_previous_win = helpers.has_previous_win(entry.bid_entry.user.id)
			data =dict(first_name=entry.bid_entry.user.profile.first_name,
					middle_name=entry.bid_entry.user.profile.middle_name,
					last_name=entry.bid_entry.user.profile.last_name,
					bid_code =entry.bid_entry.bid.code,
					product=entry.bid_entry.bid.product.name,
					amount=entry.amount,
					has_previous_win = has_previous_win
					)
			datalist.append(data)
		product = entry.bid_entry.bid.product.name
		bidcode = entry.bid_entry.bid.code
		return render(request,'admin_portal/unique-bids.html',{'data':datalist,'product':product,'bidcode':bidcode})
	def post(self,request):
		pass

		
		

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

class BidReport(UserPassesTestMixin,AccessMixin,View):
	raise_exception=True

	def test_func(self):
		return self.request.user.groups.filter(name=settings.BIDADMINS).exists()
	
	def get(self, request,bid_id):
		bid = Bid.objects.get(pk=bid_id)
		product_name = bid.product.name

		field_header_map = {
							'amount': 'BID VALUE',
							'bid_entry__bid__id':'BID ID',
							'bid_entry__bid__product__name':'PRODUCT',
							'bid_entry__bid__is_open':'OPEN',
							'bid_entry__user__id':'USER ID',
							'bid_entry__user__phone_number':'PHONE NUMBER',
							'bid_entry__user__profile__first_name':'FIRST NAME',
							'bid_entry__user__profile__last_name':'LAST NAME',
							'bid_entry__bid__closes_at':'END TIME'
									}
		field_serializer_map = {'bid_entry__bid__closes_at': (
			lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = UserBid.objects.filter(bid_entry__bid__id=bid_id).values('amount',
			'bid_entry__bid__id',
			'bid_entry__bid__product__name',
			'bid_entry__bid__is_open',
			'bid_entry__bid__closes_at',
			'bid_entry__user__id',
			'bid_entry__user__phone_number',
			'bid_entry__user__profile__first_name',
			'bid_entry__user__profile__last_name').order_by('amount')
		return djqscsv.render_to_csv_response(qs, filename=f'BIDS ON {product_name}-(Bid ID - {bid.id})',field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super().dispatch(*args, **kwargs)


class UssdSurvey(View):
	
	def get(self, request):
			
		fields = Survey.objects.values(
			'phone_number',
			'rate',
			'text',
			'created_at')

		return render(request, 'admin_portal/ussd-survey.html', {'data': fields})

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)


def process_ussd_survey(request):
	includes = [
			'phone_number',
			'rate',
			'text',
			'created_at']
	draw = request.GET['draw']
	start = int(request.GET['start'])
	length = int(request.GET['length'])
	order_column = int(request.GET['order[0][column]'])
	order_direction = '' if request.GET['order[0][dir]'] == 'desc' else '-'
	column = [i.name for n, i in enumerate(
		Survey._meta.get_fields()) if n == order_column][0]
	global_search = request.GET['search[value]']

	if global_search !='':

		print(global_search, 'search value')

		all_objects = Survey.objects.filter(
				phone_number__icontains=global_search)
				   
		
				   

		columns = [i for i in includes]
		objects = []

		for i in all_objects.order_by(order_direction + column)[start:start + length].\
				values('phone_number',
					'rate',
					'text',
					'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Survey.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})

	else:

		all_objects=Survey.objects.values(
				'phone_number',
				'rate',
				'text',
				'created_at')

		columns = [i for i in includes]
		objects = []
		for i in all_objects.order_by('-created_at')[start:start + length].\
			values('phone_number',
					'rate',
					'text',
					'created_at'):
			ret = [i[j] for j in columns]
			objects.append(ret)
		filtered_count = all_objects.count()
		total_count = Survey.objects.count()
		return JsonResponse({
					"sEcho": draw,
					"iTotalRecords": total_count,
					"iTotalDisplayRecords": filtered_count,
					"aaData": objects,

		})


class ExportUssdSurveyCsv(View):

	def get(self, request):

		field_header_map = {
							'phone_number': 'Phone Number',
							'rate': 'Rating (Out of 10)',
							'text':"Feedback",
							'created_at':'Recorded at'
									}
		field_serializer_map = {'created_at': (
			lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))}

		qs = Survey.objects.values('phone_number','rate',
			'text',
			'created_at').all()
		return djqscsv.render_to_csv_response(qs, field_header_map=field_header_map, field_serializer_map=field_serializer_map, append_datestamp=True)

	def dispatch(self, *args, **kwargs):
		return super().dispatch(*args, **kwargs)

class AddToBlackList(UserPassesTestMixin,AccessMixin,View):
	raise_exception=True
	data = {}

	def test_func(self):
		return self.request.user.groups.filter(name=settings.BIDADMINS).exists()

	
	def post(self,request):
		try:
			msisdn = request.POST.get('msisdn')
			notes = request.POST.get('notes')
			bid_id = request.POST.get('bid_id')
			if len(msisdn) < 10:
				self.data['icon']='error'
				self.data['title']='Error'
				self.data['status'] ='Invalid Phone Number'
				return JsonResponse(self.data)
			if not notes:
				self.data['icon']='error'
				self.data['title']='Error'
				self.data['status'] ='Reson cannot be empty'
				return JsonResponse(self.data)
			bid = helpers.get_bid_by_id(bid_id)
			msisdn = standardize_msisdn(msisdn)
			actor = request.user.get_full_name()
			obj,created = helpers.blacklist_user(msisdn,bid,notes,actor)
			if created:
				self.data['icon']='success'
				self.data['title']='Added'
				self.data['status'] = f'{msisdn} was blacklisted from submitting bids for {bid.product.name} - Bid ID: {bid.id}'
			elif not created:
				self.data['icon']='success'
				self.data['title']='Already added'
				self.data['status'] = f'{msisdn} was already Added to blacklist for {bid.product.name} - Bid ID: {bid.id}'

			else:
				self.data['icon']='error'
				self.data['title']='Error'
				self.data['status'] =  'Unknown error Occured.Please try again Later.'

			return JsonResponse(self.data)
		except:
			self.data['icon']='error'
			self.data['title']='Error'

			self.data['status'] =  'Unknown error Occured.Please try again Later.'

			return JsonResponse(self.data)

	
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

