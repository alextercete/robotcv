import struct

SEND_ROBOTS_POSITIONS = 1


class BadFormatError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class MessageFormatter:

    @classmethod
    def encode(cls, message_type, message):
        formats = cls.get_encoding_formats(message_type, message)
        return struct.pack(formats, *message)

    @classmethod
    def decode(cls, message_type, message):
        formats = cls.get_decoding_formats(message_type, message)
        return struct.unpack(formats, message)

    @classmethod
    def get_encoding_formats(cls, message_type, message):

        basic_format = {
            SEND_ROBOTS_POSITIONS: 'chh',
        }[message_type]

        return cls.get_formats(basic_format, len(basic_format), len(message))

    @classmethod
    def get_decoding_formats(cls, message_type, message):

        basic_format, minimum_length = {
            SEND_ROBOTS_POSITIONS: ('chh', 5),
        }[message_type]

        return cls.get_formats(basic_format, minimum_length, len(message))

    @classmethod
    def get_formats(cls, basic_format, minimum_length, message_length):

        if message_length % minimum_length > 0:
            raise BadFormatError('Message length ({0}) is not multiple of {1}!'\
                                     .format(message_length, minimum_length))

        return '=' + basic_format * int(message_length / minimum_length)
