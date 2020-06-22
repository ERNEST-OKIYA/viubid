import re

from .backends import ussd_session_backend
from .settings import ussd_settings
from .utils import ArgumentVector


class UssdMiddleware(object):

	default_request_data = dict(
		service_code=None,
		phone_number=None,
		session_id=None,
		initial_code=None,
		ussd_string=None,
		request_input=None
	)

	def __init__(self, get_response):
		self.get_response = get_response

	@property
	def backend(self):
		return ussd_session_backend

	def is_ussd_request(self, request):
		for endpoint in ussd_settings.URLS:
			if re.search(endpoint['path'], request.path) is not None:
				self.validate_request(request, endpoint)
				request.ussd_conf = endpoint
				return True
		return False

	def validate_request(self, request, conf):
		if request.method not in conf['methods']:
			raise ValueError(
				'Http Method %s not allowed for USSD endpoint %s.'\
				% (request.method, request.path)
			)

	def validate_request_data(self, data, request):
		for k in ('service_code', ('ussd_string', 'request_input'), 'phone_number', 'session_id'):
			if isinstance(k, (tuple, list)):
				ok = any((True for x in k if data.get(x) is not None))
			else:
				ok = data.get(k) is not None
			if not ok:
				raise ValueError('Query param %s required in USSD requests.' % (k,))

	# def extract_request_data(self, req):
	# 	raise NotImplementedError

	def prepare_request_data(self, req):
		req.ussd_data = dict(self.default_request_data)
		req.ussd_data.update(self.extract_request_data(req))
		self.validate_request_data(req.ussd_data, req)

	def open_session(self, req):
		session = self.backend.open_session(req)
		req.ussd_session = session

	def close_session(self, req, response):
		if hasattr(req, 'ussd_session'):
			self.backend.close_session(req.ussd_session, req, response)

	def prepare_request(self, request):
		service_code = request.ussd_data['service_code']
		base_code = request.ussd_data.get('initial_code')
		argstr = request.ussd_data['ussd_string']
		args = request.ussd_data['request_input']

		request.service_code = service_code

		if args is None:

			argv = ArgumentVector(service_code, argstr, base_code)

			session = request.ussd_session
			xargv = session.argv
			request.args = argv - xargv if xargv else []

			#TODO:- argv might not be needed in the request object. DONE.
			session.argv = argv
		else:
			request.args = ArgumentVector(args)

	def setup_request(self, request):
		self.prepare_request_data(request)
		self.open_session(request)
		self.prepare_request(request)

	def teardown_request(self, request, response):
		self.close_session(request, response)

	def __call__(self, req, *args, **kwargs):
		is_ussd_request = self.is_ussd_request(req)

		res = is_ussd_request and self.setup_request(req) or self.get_response(req, *args, **kwargs)
		res = is_ussd_request and self.teardown_request(req, res) or res
		return res


