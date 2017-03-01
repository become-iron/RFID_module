import ctypes
import os
import logging as log
from typing import List

__all__ = ('Reader',)

# конфигурация логирования
# "ERROR: 2017-02-26 16:50:00,685. FECOM: (-1033) communication process not started"
log.basicConfig(format='%(levelname)s: %(asctime)-15s. %(message)s', level=log.INFO)

RFID_LIB = ctypes.CDLL(os.getcwd() + r'\RFID.dll')  # подключение библиотеки для работы с RFID-ридером
# определение возвращаемых функциями типов данных
RFID_LIB.new_reader.restype = ctypes.c_void_p  # WARN CHECK
RFID_LIB.connect_reader.restype = ctypes.c_int
RFID_LIB.inventory.restype = ctypes.c_int
RFID_LIB.inventory.read_tag = ctypes.c_int
RFID_LIB.inventory.write_tag = ctypes.c_int
RFID_LIB.get_error_text.restype = ctypes.c_char_p

DEF_AMOUNT_OF_TAGS = 10  #: максимальное количество меток по умолчанию


class Reader(object):
    """Класс для управления ридером"""
    def __init__(self):
        self._reader = RFID_LIB.new_reader()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def connect(self, bus_addr: int, port_number: int) -> None or str:
        """Производит соединение с ридером"""
        r_code = RFID_LIB.connect_reader(
            self._reader,
            ctypes.c_ubyte(bus_addr),
            ctypes.c_int(port_number),
        )
        if r_code != 0:
            return self.get_error_text(r_code)

    def disconnect(self) -> None:
        """Производит разъединение с ридером"""
        RFID_LIB.disconnect_reader(self._reader)

    def inventory(self) -> list or str:
        # TODO
        tag_ids = ((ctypes.c_char * 255) * DEF_AMOUNT_OF_TAGS)()
        r_code = RFID_LIB.inventory(self._reader, tag_ids)
        if r_code != 0:
            return [tag_id.decode('utf-8') for tag_id in tag_ids]
        else:
            return self.get_error_text(r_code)

    def read_tag(self, tag_id: str):
        # TODO
        tags_data = ((ctypes.c_char * 255) * DEF_AMOUNT_OF_TAGS)()
        r_code = RFID_LIB.read_tag(self._reader, ctypes.c_char_p(tag_id), tags_data)
        if r_code != 0:
            return [tag_data.decode('utf-8') for tag_data in tags_data]
        else:
            return self.get_error_text(r_code)

    def write_tag(self, tag_id: str, info: List[str]) -> None or str:
        # TODO
        tags_data = ((ctypes.c_char * 255) * DEF_AMOUNT_OF_TAGS)(*info[DEF_AMOUNT_OF_TAGS])
        r_code = RFID_LIB.read_tag(self._reader, ctypes.c_char_p(tag_id), tags_data)
        if r_code == 0:
            return self.get_error_text(r_code)

    def get_error_text(self, code: int) -> str:
        """Возвращает текст ошибки по соответствующему коду"""
        text = RFID_LIB.get_error_text(self._reader, ctypes.c_int(code)).decode('utf-8')
        if len(text) == 0:
            log.error('Невалидный код ошибки: {0}'.format(code))
        else:
            log.error(text)
            return text


if __name__ == '__main__':
    # Первый способ работы с ридером (с авто-дисконнектом после окончания работы)
    with Reader() as reader:
        reader.connect(1, 1)

    # Второй способ
    reader.connect(1, 1)
    reader.disconnect()
