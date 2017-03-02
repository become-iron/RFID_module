# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from logic import Readers

# Полезные ссылки:
# Representational state transfer — https://en.wikipedia.org/wiki/Representational_state_transfer

app = Flask(__name__)


@app.route('/')
def index():
    # TODO (Н): выдавать инфу по API
    return "Hello, reader!"


@app.route('/readers/', methods=['GET'])
def get_readers():
    """Возвращает список настроек для ридеров"""
    # curl -i -X GET http://localhost:5000/readers/
    # curl -i http://localhost:5000/readers/

    # 200 - возвращен список настроек
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify(Readers.get_readers())


@app.route('/readers/', methods=['POST'])
def add_reader():
    """Добавляет настройки для ридера"""
    # curl -i -H "Content-Type: application/json" -X POST -d "{"""reader_id""": """1""", """bus_addr""": 1, """port_number""": 1}" http://localhost:5000/readers/

    # 201 - создан новый ресурс (с настройками)
    # 400 - ошибка в запросе, ошибки в названиях полей, передан не json
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify(Readers.add_reader(request.json))



@app.route('/readers/', methods=['PUT'])
def update_readers():
    """Заменяет все настройки ридеров переданными"""

    # 200 - настройки обновлены
    # 400 - ошибка в запросе, ошибки в названиях полей, передан не json
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/', methods=['DELETE'])
def delete_readers():
    """Удаляет все настройки ридеров"""

    # 200 - настройки удалены
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/<reader_id>/', methods=['GET'])
def get_reader(reader_id):
    """Возвращает настройки ридера"""

    # 200 - возвращен список настроек
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/<reader_id>/', methods=['PUT'])
def update_reader(reader_id):
    """Обновляет настройки ридера"""

    # 200 - настройки обновлены
    # 400 - ошибка в запросе, ошибки в названиях полей, передан не json
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/<reader_id>/', methods=['DELETE'])
def delete_reader(reader_id):
    """Удаляет ридер"""

    # 200 - настройки удалены
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/<reader_id>/start/', methods=['PUT'])
# @app.route('/readers/<reader_id>/', methods=['PUT'])
def start_reader(reader_id):
    """Подключает ридер"""

    # 200 - ридер подключен
    # 400 - ошибка в запросе, ошибки в названиях полей, передан не json
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/<reader_id>/stop/', methods=['PUT'])
# @app.route('/readers/<reader_id>/', methods=['PUT'])
def stop_reader(reader_id):
    """Отключает ридер"""

    # 200 - ридер отключен
    # 400 - ошибка в запросе, ошибки в названиях полей, передан не json
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


# Эта функция, скорее всего, не нужна
@app.route('/readers/<reader_id>/tags/inventory/', methods=['GET'])
# @app.route('/readers/<reader_id>/inventory/', methods=['GET'])
def inventory(reader_id):
    """Возвращает идентификаторы меток"""

    # 200 - идентификаторы возвращены
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['GET'])
def read_tags(reader_id):
    """Возвращает информацию с меток"""

    # 200 - информация возвращена
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['PUT'])
def write_tags(reader_id):
    """Записывает информацию в метки"""

    # 200 - информация записана
    # 400 - ошибка в запросе, ошибки в названиях полей, передан не json
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['DELETE'])
def clear_tags(reader_id):
    """Очищает информацию с меток"""

    # 200 - информация очищена
    # 404 - по данному адресу ничего не найдено
    # 405 - метод не соответсвует адресу
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
