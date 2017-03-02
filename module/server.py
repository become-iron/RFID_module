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


@app.route('/readers/', methods=['POST'])
def add_reader():
    """Добавляет настройки для ридера"""
    # curl -i -H "Content-Type: application/json" -X POST -d "{"""reader_id""": """1""", """bus_addr""": 1, """port_number""": 1}" http://localhost:5000/readers/

    http_code = 201     # создан новый ресурс (с настройками)
    response = Readers.add_reader(request.json)

    if 'error' in response:
        http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json
    return jsonify(response), http_code


@app.route('/readers/', methods=['GET'])
def get_readers():
    """Возвращает список настроек для ридеров"""
    # curl -i -X GET http://localhost:5000/readers/
    # curl -i http://localhost:5000/readers/

    http_code = 200     # возвращен список настроек
    response = Readers.get_readers()
    
    return jsonify(response), http_code


@app.route('/readers/<reader_id>/', methods=['GET'])
def get_reader(reader_id):
    """Возвращает настройки ридера"""
    # curl -i -X GET http://localhost:5000/readers/1/
    # curl -i http://localhost:5000/readers/1/

    http_code = 200     # возвращен список настроек
    response = Readers.get_reader(reader_id)

    return jsonify({}), http_code


@app.route('/readers/', methods=['PUT'])
def update_readers():
    """Заменяет все настройки ридеров переданными"""
    # curl -i -H "Content-Type: application/json" -X POST -d "{"""reader_id""": """1""", """bus_addr""": 1, """port_number""": 1}" http://localhost:5000/readers/

    http_code = 200     # настройки обновлены
    response = Readers.update_readers()

    if 'error' in response:
        http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify({}), http_code


@app.route('/readers/<reader_id>/', methods=['PUT'])
def update_reader(reader_id):
    """Обновляет настройки ридера"""

    http_code = 200     # настройки обновлены
    response = Readers.update_reader(reader_id)

    if 'error' in response:
        http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify({}), http_code


@app.route('/readers/', methods=['DELETE'])
def delete_readers():
    """Удаляет все настройки ридеров"""
    # curl -i -X DELETE http://localhost:5000/readers/

    http_code = 200     # настройки удалены
    response = Readers.delete_readers()

    return jsonify({})


@app.route('/readers/<reader_id>/', methods=['DELETE'])
def delete_reader(reader_id):
    """Удаляет ридер"""
    # curl -i -X DELETE http://localhost:5000/readers/1/

    http_code = 200     # настройки удалены
    response = Readers.delete_reader(reader_id)

    return jsonify({})


# Эта функция, скорее всего, не нужна
@app.route('/readers/<reader_id>/tags/inventory/', methods=['GET'])
def inventory(reader_id):
    """Возвращает идентификаторы меток"""

    http_code = 200     # идентификаторы возвращены
    response = Readers.inventory(reader_id)

    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['GET'])
def read_tags(reader_id):
    """Возвращает информацию с меток"""

    http_code = 200     # информация возвращена
    response = Readers.read_tags(reader_id)

    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['PUT'])
def write_tags(reader_id):
    """Записывает информацию в метки"""

    http_code = 200     # информация записана
    response = Readers.write_tags(reader_id)

    if 'error' in response:
        http_code = 400     # ошибка в запросе, ошибки в названиях полей, передан не json

    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['DELETE'])
def clear_tags(reader_id):
    """Очищает информацию с меток"""
    # curl -i -X DELETE http://localhost:5000/readers/tags/

    http_code = 200     # 
    response = Readers.clear_tags(reader_id)

    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
