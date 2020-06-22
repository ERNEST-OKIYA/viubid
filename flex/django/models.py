from django.db import models
from flex.datastructures.enum import Enum, StrEnum



class StrEnumField(models.CharField):
	"""EnumField object."""
	description = "A %(enum)s member"

	def __init__(self, *args, enum=None, **kwargs):
		if enum is None or not issubclass(enum, StrEnum):
			raise TypeError('StrEnumField enum must be a subclass of StrEnum. %s given.' % (type(enum),))

		kwargs.setdefault('max_length', max(64, *(len(m) for m in enum)))
		kwargs['choices'] = enum.choices()
		super(StrEnumField, self).__init__(*args, **kwargs)
		self.enum = enum

	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		kwargs['enum'] = self.enum
		return name, path, args, kwargs

	def to_python(self, value):
		return value if value is None or isinstance(value, self.enum) else self.enum(value)

	def from_db_value(self, value, expression, connection, context=None):
		return value if value is None else self.enum(value)

	def get_prep_value(self, value):
		return value if value is None else self.to_python(value).value

