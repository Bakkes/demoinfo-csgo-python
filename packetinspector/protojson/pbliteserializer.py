"""
Protocol Buffer 2 Serializer which serializes messages into PB-Lite
("JsPbLite") format.

PB-Lite format is an array where each index corresponds to the associated tag
number. For example, a message like so:

	message Foo {
		optional int bar = 1;
		optional int baz = 2;
		optional int bop = 4;
	}

would be represented as such:

	[None, (bar data), (baz data), (nothing), (bop data)]

Note that since the array index is used to represent the tag number, sparsely
populated messages with tag numbers that are not continuous (and/or are very
large) will have many (empty) spots and thus, are inefficient.
"""

import sys

from protojson.error import PbDecodeError

from google.protobuf.descriptor import FieldDescriptor

_postImportVars = vars().keys()


TYPE_BOOL = FieldDescriptor.TYPE_BOOL
TYPE_MESSAGE = FieldDescriptor.TYPE_MESSAGE
TYPE_GROUP = FieldDescriptor.TYPE_GROUP
TYPE_ENUM = FieldDescriptor.TYPE_ENUM
LABEL_REPEATED = FieldDescriptor.LABEL_REPEATED

MESSAGE_OR_GROUP = (TYPE_MESSAGE, TYPE_GROUP)


def _convertToBool(obj):
	if obj not in (0, 1):
		raise PbDecodeError("Expected a value == "
			"to 0 or 1, but found a %r" % (type(obj),))
	return (obj == 1)


def _ensureValidEnum(field, obj):
	# Protocol Buffers' Python module (as of 2010-07-18) allows setting
	# an enum field to an invalid value.  This can lead to all sorts of
	# terrible bugs.  Here we dig into the field and check if the value is
	# allowed.  I filed a bug to get this fixed in protobuf:
	# https://code.google.com/p/protobuf/issues/detail?id=206
	if obj not in field.enum_type.values_by_number:
		raise PbDecodeError("Expected a valid value for "
			"%r, but didn't get one." % (field,))


def _getIterator(obj):
	"""
	Returns C{obj.__iter__()} or raises a L{PbDecodeError}.
	"""
	try:
		return obj.__iter__()
	except (TypeError, AttributeError):
		raise PbDecodeError("Expected an iterable object but "
			"found a %r" % (type(obj),))


class PbLiteSerializer(object):
	"""
	A port of Closure Library's goog.proto2.PbLiteSerializer, but without
	the laziness.
	"""
	__slots__ = ('fillerValue',)

	def __init__(self, fillerValue=None):
		"""
		C{fillerValue} is the object to use for unpopulated indices.  The
		default is C{None}.
		"""
		self.fillerValue = fillerValue


	def _getSerializedValue(self, field, value):
		"""
		Returns the serialized form of the given value for the given field
		if the field is a Message or Group and returns the value unchanged
		otherwise (except serialize BOOLs as ints).
		"""
		if field.type == TYPE_BOOL:
			# Booleans are serialized in numeric form.
			return value and 1 or 0
		elif field.type in MESSAGE_OR_GROUP:
			return self.serialize(value)
		else:
			return value


	def serialize(self, message):
		"""
		C{message} is a L{google.protobuf.message.Message}.

		Returns a C{list}, the serialized form of C{message}.
		"""
		keys = message.DESCRIPTOR.fields_by_number.keys()
		if not keys:
			serialized = {}
		else:
			maxFieldNumber = max(keys)
			serialized = {}#[self.fillerValue] * (maxFieldNumber + 1)

			for tag, field in message.DESCRIPTOR.fields_by_number.iteritems():
				value = getattr(message, field.name)
				if field.label == LABEL_REPEATED:
					serializedChild = []
					for child in getattr(message, field.name):
						serializedChild.append(self._getSerializedValue(field, child))
					serialized[field.name] = serializedChild
				else:
					serialized[field.name] = self._getSerializedValue(field, value)

		return serialized


	def _deserializeMessageField(self, message, field, data):
		"""
		Mutates C{message} based on C{data} and C{field}.

		C{message} is a L{google.protobuf.message.Message}.
		C{field} is a L{google.protobuf.descriptor.FieldDescriptor}.
		C{data} is a L{list}, L{int}, L{long}, L{float}, L{bool}, L{str},
			L{unicode}, or L{NoneType}.
		"""
		isBool = (field.type == TYPE_BOOL)
		isEnum = (field.type == TYPE_ENUM)
		if field.label == LABEL_REPEATED:
			messageField = getattr(message, field.name)
			if field.type not in MESSAGE_OR_GROUP:
				for value in _getIterator(data):
					if isBool:
						value = _convertToBool(value)
					elif isEnum:
						_ensureValidEnum(field, value)
					try:
						messageField.append(value)
					except (TypeError, ValueError), e:
						raise PbDecodeError(str(e))
			else:
				for subdata in _getIterator(data):
					self._deserializeMessage(messageField.add(), subdata)
		else:
			if field.type not in MESSAGE_OR_GROUP:
				if isBool:
					data = _convertToBool(data)
				elif isEnum:
					_ensureValidEnum(field, data)
				# Because setattr(..., ..., None) for optional fields is
				# okay, we don't need our own branching here.
				try:
					setattr(message, field.name, data)
				except (TypeError, ValueError), e:
					raise PbDecodeError(str(e))
			else:
				# On "singular fields", we can just grab a child and set
				# properties on it.  Setting a field on the child will cause
				# the child's field to exist in the parent.  See:
				# https://code.google.com/apis/protocolbuffers/docs/reference/python-generated.html#fields
				messageField = getattr(message, field.name)
				self._deserializeMessage(messageField, data)


	def _deserializeMessage(self, message, data):
		"""
		Mutates C{message} based on C{data}.

		C{message} is a L{google.protobuf.message.Message}.
		C{data} is a L{list}.
		"""
		for tag, field in message.DESCRIPTOR.fields_by_number.iteritems():
			try:
				subdata = data[tag]
			except IndexError:
				# Raise even if it was an optional field.
				raise PbDecodeError("For message %r expected index "
					"%r but it was missing." % (message, tag))
			self._deserializeMessageField(message, field, subdata)


	def deserialize(self, message, data):
		"""
		Puts values from C{data} into message C{message}.  The message
		is mutated, not returned.  Existing values are cleared.

		C{message} is a L{google.protobuf.message.Message}.
		C{data} is a L{list}.  Unneeded values are ignored (fillerValue
			is not used).

		If any part of C{data} is invalid, raises L{PbDecodeError}.

		Note that the deserializer is forgiving when it comes to bool fields -
		it will accept 1, 1.0, True, 0, 0.0, -0.0, and False.
		"""
		message.Clear()
		self._deserializeMessage(message, data)
		# We know it's initialized (has every field) because we iterated
		# over the fields, not the serialized data.



try: from refbinder.api import bindRecursive
except ImportError: pass
else: bindRecursive(sys.modules[__name__], _postImportVars)
