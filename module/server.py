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
    return jsonify({})


@app.route('/readers/', methods=['POST'])
def add_reader():
    """Добавляет настройки для ридера"""
    # curl  -i -H "Content-Type: application/json" -X POST -d "{"""reader_id""": """1""", """addr_bus""": 1, """port_number""": 1}" http://localhost:5000/readers/
    # TODO (Н): если уже есть настройки для данного ридера, не возвращать ли ошибку?
    return jsonify({})


@app.route('/readers/', methods=['PUT'])
def update_readers():
    """Заменяет все настройки ридеров переданными"""
    return jsonify({})


@app.route('/readers/', methods=['DELETE'])
def delete_readers():
    """Удаляет все настройки ридеров"""
    return jsonify({})


@app.route('/readers/<reader_id>/', methods=['GET'])
def update_reader(reader_id):
    """Возвращает настройки ридера"""
    return jsonify({})


@app.route('/readers/<reader_id>/', methods=['PUT'])
def update_reader(reader_id):
    """Обновляет настройки ридера"""
    return jsonify({})


@app.route('/readers/<reader_id>/', methods=['DELETE'])
def delete_reader(reader_id):
    """Удаляет ридер"""
    return jsonify({})


@app.route('/readers/<reader_id>/start/', methods=['PUT'])
def start_reader(reader_id):
    """Подключает ридер"""
    return jsonify({})


@app.route('/readers/<reader_id>/stop/', methods=['PUT'])
def stop_reader(reader_id):
    """Отключает ридер"""
    return jsonify({})


@app.route('/readers/<reader_id>/tags/inventory/', methods=['GET'])
def inventory(reader_id):
    """Возвращает идентификаторы меток"""
    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['GET'])
def read_tags(reader_id):
    """Возвращает информацию с меток"""
    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['PUT'])
def write_tags(reader_id):
    """Записывает информацию в метки"""
    return jsonify({})


@app.route('/readers/<reader_id>/tags/', methods=['DELETE'])
def clear_tags(reader_id):
    """Очищает информацию с меток"""
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)
