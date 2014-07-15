from unittest import TestCase
from protojson import pbliteserializer, alltypes_pb2


def _getExpectedDefaults():
	expectedDefaults = [
		None, # 0
		0, # 1
		1, # 2
		0, # and so on
		0,
		0,
		0,
		0,
		0,
		0,
		0,
		1.5,
		0,
		0,
		u'',
		'moo',
		[ # 16
			None, None, None, None, None, None, None, None, None,
			None, None, None, None, None, None, None, None, 0],
		None, # 17
		[None, 0],
		None,
		None,
		1,
		None,
		None,
		None,
		None,
		None,
		None,
		None,
		None,
		None,
		[], # 31
		[],
		[],
		[],
		[],
		[],
		[],
		[],
		[],
		[],
		[],
		[],
		[],
		[],
		[],
		[], # 46
		None, # 47
		[], # 48
		[], # 49
		1, # 50
	]
	return expectedDefaults


class PbLiteSerializeTests(TestCase):
	"""
	Tests for L{pbliteserializer.PbLiteSerializer.serialize}.
	"""

	def test_defaults(self):
		message = alltypes_pb2.TestAllTypes()
		serializer = pbliteserializer.PbLiteSerializer()
		ser = serializer.serialize(message)

		self.assertEqual(_getExpectedDefaults(), ser)


	def test_serializeDeserialize(self):
		"""
		This is a port of Closure Library's closure/goog/proto2/pbserializer_test.html
		testSerializationAndDeserialization.
		"""
		message = alltypes_pb2.TestAllTypes()
		
		# Set the fields.
		# Singular.
		message.optional_int32 = 101
		message.optional_int64 = 102
		message.optional_uint32 = 103
		message.optional_uint64 = 104
		message.optional_sint32 = 105
		message.optional_sint64 = 106
		message.optional_fixed32 = 107
		message.optional_fixed64 = 108
		message.optional_sfixed32 = 109
		message.optional_sfixed64 = 110
		message.optional_float = 111.5
		message.optional_double = 112.5
		message.optional_bool = True
		message.optional_string = 'test'
		message.optional_bytes = 'abcd'

		# Note: setting OptionGroup.a is wrong and leads to disaster.
		message.optionalgroup.a = 111

		message.optional_nested_message.b = 112

		message.optional_nested_enum  = alltypes_pb2.TestAllTypes.FOO

		# Repeated.
		message.repeated_int32.append(201)
		message.repeated_int32.append(202)

		# Skip a few repeated fields so we can test how null array values are
		# handled.
		message.repeated_string.append('foo')
		message.repeated_string.append('bar')

		message.required_int32 = 1

		# Serialize.
		serializer = pbliteserializer.PbLiteSerializer()
		pblite = serializer.serialize(message)

		self.assertTrue(isinstance(pblite, list))

		# Assert that everything serialized properly.
		self.assertEqual(101, pblite[1])
		self.assertEqual(102, pblite[2])
		self.assertEqual(103, pblite[3])
		self.assertEqual(104, pblite[4])
		self.assertEqual(105, pblite[5])
		self.assertEqual(106, pblite[6])
		self.assertEqual(107, pblite[7])
		self.assertEqual(108, pblite[8])
		self.assertEqual(109, pblite[9])
		self.assertEqual(110, pblite[10])
		self.assertEqual(111.5, pblite[11])
		self.assertEqual(112.5, pblite[12])
		self.assertEqual(1, pblite[13]) # True is serialized as 1
		self.assertEqual('test', pblite[14])
		self.assertEqual('abcd', pblite[15])

		self.assertEqual(111, pblite[16][17])
		self.assertEqual(112, pblite[18][1])

		self.assertEqual(None, pblite[19])
		self.assertEqual(None, pblite[20])

		self.assertEqual(alltypes_pb2.TestAllTypes.FOO, pblite[21])

		self.assertEqual(201, pblite[31][0])
		self.assertEqual(202, pblite[31][1])
		self.assertEqual('foo', pblite[44][0])
		self.assertEqual('bar', pblite[44][1])
		self.assertEqual(1, pblite[50])

		messageDecoded = alltypes_pb2.TestAllTypes()
		serializer.deserialize(messageDecoded, pblite)
		##print "\n\n", message
		##print "\n\n", messageDecoded
		self.assertEqual(
			messageDecoded,
			message,
			"Messages do not match:\n" +
			str(messageDecoded) + "\n!=\n\n" + str(message))


	def test_deserializeSerializeRepeatedMessage(self):
		"""
		Deserializing a repeated Message works.  When serialized, it
		matches the original serialized data.
		"""
		serializer = pbliteserializer.PbLiteSerializer()
		pblite = _getExpectedDefaults()
		# Set the repeated_nested_message
		pblite[48] = [[None, 100], [None, 200]]
		messageDecoded = alltypes_pb2.TestAllTypes()
		serializer.deserialize(messageDecoded, pblite)

		pbliteReencoded = serializer.serialize(messageDecoded)
		self.assertEqual([[None, 100], [None, 200]], pbliteReencoded[48])


	def test_wrongTypeForData(self):
		"""
		If a non-indexable object is passed as the second argument to
		L{PbLiteSerializer.deserialize}, it raises L{TypeError}.
		"""
		serializer = pbliteserializer.PbLiteSerializer()
		for pblite in [None, 3, 4L, 0.5]:
			messageDecoded = alltypes_pb2.TestAllTypes()
			self.assertRaises(
				TypeError,
				lambda: serializer.deserialize(messageDecoded, pblite))


	def test_wrongTypeForMessage(self):
		"""
		If a non-L{Message} is passed as the second argument to
		L{PbLiteSerializer.deserialize}, it raises L{AttributeError}.
		"""
		serializer = pbliteserializer.PbLiteSerializer()
		for messageDecoded in [None, 3, 4L, 0.5, {}, set()]:
			self.assertRaises(
				AttributeError,
				lambda: serializer.deserialize(messageDecoded, []))



class PbLiteDeserializeTests(TestCase):

	def setUp(self):
		self.serializer = pbliteserializer.PbLiteSerializer()


	def test_stringInsteadOfNumber(self):
		"""
		If an index which should contain an int64 field contains a string,
		L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the optional_int64 to a string
		pblite[2] = u'wrong-type'
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_numberTooBig(self):
		"""
		If an index which should contain an int64 field contains a big number
		2**128, L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the optional_int64 to a big number
		pblite[2] = 2**128
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_stringInRepeatedNumber(self):
		"""
		If an index which should contain a list of int64s contains a list of strings,
		L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the repeated_int32
		pblite[31] = [4, u'wrong-type', 5]
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_noneInsteadOfRepeatedNumber(self):
		"""
		If an index which should contain a list of int64s contains a None,
		L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the repeated_int32
		pblite[31] = None
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_noneInsteadOfRepeatedMessage(self):
		"""
		If an index which should contain a list of Messages (more lists)
		contains a None, L{PbLiteSerializer.deserialize} raises
		L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the repeated_nested_message
		pblite[48] = None
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_stringInsteadOfBool(self):
		"""
		If an index which should contain a bool (or bool number) contains
		a string, L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the optional_bool
		pblite[13] = u'wrong-type'
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_stringInRepeatedBool(self):
		"""
		If an index which should contain a list of bools (or bool numbers)
		contains a string, L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the repeated_bool
		pblite[43] = [1, u'wrong-type', 0]
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_badEnumValue(self):
		"""
		If a serialized message has an invalid enum value,
		L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the optional_nested_enum
		pblite[21] = 99 # not a valid enum value
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_badRepeatedEnumValue(self):
		"""
		If a serialized message has an invalid repeated enum value,
		L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the repeated_nested_enum
		pblite[49] = [1, 2, 99, 3] # 99 is not a valid enum value; the others are
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_messageMissingAnIndex(self):
		"""
		If a serialized message is missing an index which it should have,
		L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		pblite.pop()
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_messageExtraIndexOkay(self):
		"""
		If a serialized message has more indices than it should have,
		L{PbLiteSerializer.deserialize} ignores it.
		"""
		pblite = _getExpectedDefaults()
		pblite.append(u'extra-field')
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.serializer.deserialize(messageDecoded, pblite)


	def test_requiredFieldIsNone(self):
		"""
		If a serialized message has a C{None} for a required field,
		L{PbLiteSerializer.deserialize} raises L{PbDecodeError}.
		"""
		pblite = _getExpectedDefaults()
		# Set the required_int32
		pblite[50] = None
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertRaises(
			pbliteserializer.PbDecodeError,
			lambda: self.serializer.deserialize(messageDecoded, pblite))


	def test_optionalFieldWithDefaultIsNone(self):
		"""
		If a serialized message has a C{None} for a optional field with
		a default, L{PbLiteSerializer.deserialize} ignores the None and
		uses the default value.
		"""
		pblite = _getExpectedDefaults()
		# Set the optional_int64
		pblite[2] = None
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertFalse(messageDecoded.HasField("optional_int64"))
		self.assertEqual(1, messageDecoded.optional_int64)


	def test_optionalFieldWithoutDefaultIsNone(self):
		"""
		If a serialized message has a C{None} for a optional field without
		a default, L{PbLiteSerializer.deserialize} ignores the None and
		the decoded Message is missing the field.
		"""
		pblite = _getExpectedDefaults()
		# Set the optional_int32
		pblite[1] = None
		messageDecoded = alltypes_pb2.TestAllTypes()
		self.assertFalse(messageDecoded.HasField("optional_int32"))
		self.assertEqual(0, messageDecoded.optional_int32)
