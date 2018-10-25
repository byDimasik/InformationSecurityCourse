import struct
from os import stat
from PIL import Image


class LSBError(Exception):
    pass


class LSB:
    def __init__(self):
        self.__current_w = 0
        self.__current_h = 0
        self.__last_w = 0
        self.__last_h = 0

    @staticmethod
    def _decompose(bytes_):
        """
        Decompose a binary data into an array of bits
        :param bytes_: binary data
        :return: array of bits (e.g. [1, 1, 0, 0, ..., 1])
        """
        decomposed_data = []

        data_bytes = struct.pack("i", len(bytes_)) + bytes_  # [data_size_bytes] + data

        for b in data_bytes:
            for i in range(7, -1, -1):
                decomposed_data.append((b >> i) & 0x1)

        return decomposed_data

    @staticmethod
    def _compose(decomposed_data, get_size=False):
        """
        Compose an array of bits into a binary data
        :param decomposed_data: array of bits
        :param get_size:
        :return: if get_size is True return int from first 4 bytes else return binary data
        """
        bytes_ = bytearray()
        length = len(decomposed_data)

        for i in range(len(decomposed_data) // 8):
            byte = 0
            for j in range(0, 8):
                if i * 8 + j < length:
                    byte = (byte << 1) | decomposed_data[i * 8 + j]

            bytes_.append(byte)

        bytes_ = bytes(bytes_)

        if get_size:
            return struct.unpack("i", bytes_[:4])[0]
        else:
            return bytes_

    @staticmethod
    def _set_bit(number, position, bit):
        """
        Set the i-th bit of number to bit
        :param number: 
        :param position: position
        :param bit: 
        :return: number with new bit
        """
        mask = 1 << position

        number &= ~mask  # set i-th bit to 0
        if bit:  # if bit is not 0, set to 1
            number |= mask

        return number

    def insertion(self, input_file_name, output_file_name, payload_file_name):
        """
        Insert payload file into LSB bits of an image
        :param input_file_name: file_name of source image
        :param output_file_name: file_name of result image
        :param payload_file_name: file_name of file with data to insertion
        """
        input_image = Image.open(input_file_name)
        (width, height) = input_image.size

        max_payload_size = width * height * 3.0  # max payload_file size in bits
        payload_file_size = stat(payload_file_name).st_size

        if payload_file_size > max_payload_size - 4:  # minus 4 for size == int 4 bytes
            raise LSBError('Payload file too large')

        output_image = Image.new('RGBA', (width, height))

        input_image_data = list(input_image.convert("RGBA").getdata())
        output_image_data = input_image_data

        index_in_data = 0
        with open(payload_file_name, "rb") as payload_file:
            while True:
                data = payload_file.read()
                if not data:
                    break

                decomposed_data = self._decompose(data)

                for i in decomposed_data:
                    (r, g, b, a) = input_image_data[index_in_data // 3]
                    position = index_in_data % 3
                    if position == 0:
                        r = self._set_bit(r, 0, i)
                    elif position == 1:
                        g = self._set_bit(g, 0, i)
                    else:
                        b = self._set_bit(b, 0, i)

                    output_image_data[index_in_data // 3] = (r, g, b, a)
                    index_in_data += 1

        output_image.putdata(output_image_data)
        output_image.save(output_file_name, "BMP")

    def extract(self, input_image_name, output_file_name):
        """
        Extract data inserted into LSB of the input file
        :param input_image_name:
        :param output_file_name:
        """
        input_image = Image.open(input_image_name)
        input_image_data = list(input_image.convert("RGBA").getdata())

        read_bits = 0
        file_size = None
        with open(output_file_name, "wb") as output_file:
            data_bits = []
            for (r, g, b, a) in input_image_data:
                data_bits.append(r & 1)
                data_bits.append(g & 1)
                data_bits.append(b & 1)

                read_bits += 3
                if read_bits == 33:
                    file_size = self._compose(data_bits, get_size=True)
                    data_bits = [data_bits[-1]]
                    continue

                if file_size and (read_bits - 32) // 8 > file_size:
                    break

            if file_size and len(data_bits) != 0:
                data = self._compose(data_bits)
                file_size -= output_file.write(data[:file_size])
