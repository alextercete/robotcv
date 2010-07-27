import struct

# Start and end of transmission
SOT = chr(0x01)
EOT = chr(0x02)

# Messages
SEND_ROBOTS_POSITIONS = chr(0xf5)

class BadFormatError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class MessageFormatter:

    @classmethod
    def encode(cls, message_type, data):
        encoded_data = cls.encode_data(message_type, data)
        message_length = chr(len(message_type + encoded_data))

        return '{0}{1}{2}{3}{4}'.format(SOT,
                                        message_length,
                                        message_type,
                                        encoded_data,
                                        EOT)

    @classmethod
    def encode_data(cls, message_type, data):
        formats = cls.get_encoding_formats(message_type, data)
        return struct.pack(formats, *data)

    @classmethod
    def decode_data(cls, message_type, data):
        formats = cls.get_decoding_formats(message_type, data)
        return struct.unpack(formats, data)

    @classmethod
    def get_encoding_formats(cls, message_type, data):

        basic_format = {
            SEND_ROBOTS_POSITIONS: 'hh',
        }[message_type]

        return cls.get_formats(basic_format, len(basic_format), len(data))

    @classmethod
    def get_decoding_formats(cls, message_type, data):

        basic_format, minimum_length = {
            SEND_ROBOTS_POSITIONS: ('hh', 4),
        }[message_type]

        return cls.get_formats(basic_format, minimum_length, len(data))

    @classmethod
    def get_formats(cls, basic_format, minimum_length, data_length):

        if data_length % minimum_length > 0:
            raise BadFormatError('Message length ({0}) is not multiple of {1}!'\
                                     .format(data_length, minimum_length))

        return '=' + basic_format * int(data_length / minimum_length)
