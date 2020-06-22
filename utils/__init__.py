
# class ConstType(type):

# 	def __new__(mcls, name, bases, dct):
# 		members = dct
# 		dct = dict(__members__=dct)

# 		dct['__members__']
# 		super_new = super(ConstType, mcls).__new__

# 		if not any((b for b in bases if isinstance(b, UssdScreenType))):
# 			return super_new(mcls, name, bases, dct)

# 		return cls
