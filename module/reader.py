import ctypes
import os

__all__ = ('Reader',)


RFID_LIB = ctypes.CDLL(os.getcwd() + r'\RFID.dll')  # подключение библиотеки для работы с RFID-ридером
# определение возвращаемых функциями типов данных
RFID_LIB.new_reader.restype = ctypes.c_void_p  # WARN: хранение FEDM_ISCReaderModule* в void*
RFID_LIB.connect_reader.restype = ctypes.c_int
RFID_LIB.inventory.restype = ctypes.c_int
RFID_LIB.read_tag.restype = ctypes.c_int
RFID_LIB.write_tag.restype = ctypes.c_int
RFID_LIB.get_error_text.restype = ctypes.c_char_p

DEF_AMOUNT_OF_TAGS = 10  # количество меток на паллете по умолчанию
TAG_SIZE = 224  # объём доступной памяти для записи в используемый тип меток

# TODO
# (пока не действует)
# Принципы работы:
# экземпляр класса FEDM_ISCReaderModule создаётся при коннекте ридера и удаляется при дисконнекте

# TODO: cписок ошибок ридера - в отдельный файл


class Reader(object):
    """Класс для управления ридером"""
    def __init__(self, bus_addr: int, port_number: int):
        self.bus_addr = bus_addr  # адрес шины
        self.port_number = port_number  # номер COM-порта
        self.connected = False
        self._reader = RFID_LIB.new_reader()  # указатель на объект ридера или None

    # @property
    # def connected(self):
    #     """Подключен ли ридер"""
    #     return self._reader is not None

    def __del__(self):
        self.disconnect()

    def __repr__(self):
        return 'Reader(bus_addr={!r}, port_number={!r})/{}/'\
            .format(self.bus_addr, self.port_number, 'connected' if self.connected else 'disconnected')

    def connect(self) -> int:
        """Производит соединение с ридером"""
        r_code = RFID_LIB.connect_reader(
            self._reader,
            ctypes.c_ubyte(self.bus_addr),  # c_ubyte = unsigned char
            ctypes.c_int(self.port_number),
        )
        if r_code == 0:
            self.connected = True
            return 0
        else:
            return r_code

    def disconnect(self) -> int:
        """Производит разъединение с ридером"""
        RFID_LIB.disconnect_reader(self._reader)
        self.connected = False
        # self._reader = None  # удаляем экземпляр ридера
        return 0

    def inventory(self) -> tuple or int:
        """
        Возвращает идентификаторы меток
        Возвращает:
            - (tuple) - идентификаторы меток
            - (int) - код ошибки
        """
        tag_ids = (ctypes.c_char_p * DEF_AMOUNT_OF_TAGS)()
        tag_ids[:] = tuple(('\0' * 32).encode('utf-8') for _ in range(DEF_AMOUNT_OF_TAGS))

        r_code = RFID_LIB.inventory(self._reader, tag_ids)
        if r_code == 0:
            return tuple(tag_id.decode('ascii') for tag_id in tag_ids)
        else:
            return r_code

    def read_tag(self, tag_id: str) -> str or int:
        """
        Возвращает данные с метки
        Принимает:
            - tag_id (str): идентификатор метки
        Возвращает:
            - (str) - информация с метки
            - (int) - код ошибки
        """
        tag_id = tag_id.encode('ascii')
        tag_data = ('\0' * TAG_SIZE).encode('cp866')

        r_code = RFID_LIB.read_tag(self._reader, ctypes.c_char_p(tag_id), ctypes.c_char_p(tag_data))
        if r_code == 0:
            return tag_data.decode('cp866')
        else:
            return r_code

    def write_tag(self, tag_id: str, data: str) -> int:
        """
        Записывает данные в метку
        Принимает:
            - tag_id (str): идентификатор метки
            - data (list or tuple): содержит в себе данные для меток (str)
        Возвращает:
            - (int) - код результата
        """
        tag_id = tag_id.encode('ascii')
        data = data[:TAG_SIZE].ljust(TAG_SIZE, '\0')  # удаляются лишние символы или дополняется нулевыми символами
        data = data.encode('cp866')
        r_code = RFID_LIB.write_tag(self._reader, ctypes.c_char_p(tag_id), ctypes.c_char_p(data))
        return r_code

    def get_error_text(self, code: int) -> str:
        """Возвращает текст ошибки по соответствующему коду"""
        text = RFID_LIB.get_error_text(self._reader, ctypes.c_int(code)).decode('ascii')
        if len(text) == 0 or \
           'unknown error code' in text or \
           'Unknown Errorcode' in text or \
           'Unknown error code' in text or \
           'Unknown Program Error' in text:
            text = 'Невалидный код ошибки: {0}'.format(code)
        return text


if __name__ == '__main__':
    my_reader = Reader(1, 1)
    my_reader.connect()
