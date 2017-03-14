import ctypes
import os

__all__ = ('Reader',)


RFID_LIB = ctypes.CDLL(os.getcwd() + r'\RFID.dll')  # подключение библиотеки для работы с RFID-ридером
# определение возвращаемых функциями типов данных
RFID_LIB.new_reader.restype = ctypes.c_void_p  # WARN CHECK хранение FEDM_ISCReaderModule * в void *
RFID_LIB.connect_reader.restype = ctypes.c_int
RFID_LIB.inventory.restype = ctypes.c_int
RFID_LIB.inventory.read_tag = ctypes.c_int
RFID_LIB.inventory.write_tag = ctypes.c_int
RFID_LIB.get_error_text.restype = ctypes.c_char_p

DEF_AMOUNT_OF_TAGS = 10  #: максимальное количество меток по умолчанию

# TODO
# (пока не действует)
# Принципы работы:
# экземпляр класса FEDM_ISCReaderModule создаётся при коннекте ридера и удаляется при дисконнекте

# TODO: привести типы в соответствии с C++-модулем


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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
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
        # self._reader = None  # удаляем экзмепляр ридера
        return 0

    def inventory(self) -> tuple or int:
        """Возвращает идентификаторы меток"""
        # TODO какое-то некорректное создание указателя
        tag_ids = ((ctypes.c_ubyte * 255) * DEF_AMOUNT_OF_TAGS)()
        r_code = RFID_LIB.inventory(self._reader, tag_ids)
        print(tag_ids)
        print(*tag_ids)
        print(*(tag_id.raw for tag_id in tag_ids))
        if r_code == 0:
            return tuple(tag_id.raw for tag_id in tag_ids)
        else:
            return r_code

    def read_tag(self, tag_id: str) -> tuple or int:
        """
        Возвращает данные с метки
        Принимает:
            - tag_id (str): идентификатор метки
        """
        # TODO
        tags_data = ((ctypes.c_char * 255) * DEF_AMOUNT_OF_TAGS)()
        r_code = RFID_LIB.read_tag(self._reader, ctypes.c_char_p(tag_id), tags_data)
        if r_code == 0:
            return tuple(tag_data.decode('utf-8') for tag_data in tags_data)
        else:
            return r_code

    def write_tag(self, tag_id: str, data: list or tuple) -> int:
        """
        Записывает данные в метку
        Принимает:
            - tag_id (str): идентификатор метки
            - data (list or tuple): содержит в себе данные для меток (str)
        """
        # TODO
        tags_data = ((ctypes.c_char * 255) * DEF_AMOUNT_OF_TAGS)(*data[DEF_AMOUNT_OF_TAGS])
        r_code = RFID_LIB.read_tag(self._reader, ctypes.c_char_p(tag_id), tags_data)
        if r_code == 0:
            return 0
        else:
            return r_code

    def get_error_text(self, code: int) -> str:
        """Возвращает текст ошибки по соответствующему коду"""
        text = RFID_LIB.get_error_text(self._reader, ctypes.c_int(code)).decode('utf-8')
        if len(text) == 0:
            text = 'Невалидный код ошибки: {0}'.format(code)
        return text


if __name__ == '__main__':
    # Первый способ работы с ридером (с авто-дисконнектом после окончания работы)
    with Reader(1, 1) as my_reader:
        my_reader.connect()

    # Второй способ
    my_reader = Reader(1, 1)
    my_reader.connect()
    my_reader.disconnect()
