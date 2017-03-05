..  RFID_module documentation master file, created by
    sphinx-quickstart on Sat Mar  4 16:17:56 2017.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Документация для RFID-модуля
============================

Модуль состоит из двух частей, написанных на языках C++ и Python. Модуль предоставляет возможность работы с
RFID-оборудованием (ридером) через код, написанный на языке Python.

Доступ к функциям модуля осуществляется посредством HTTP-запросов по определённому Web API.

Особенности модуля и предоставляемый им функционал:

    - управление несколькими ридерами
    - хранение настроек ридеров
    - соединение с ридером
    - инвентаризация (получения серийных номеров меток)
    - чтение информации с меток
    - запись информации в метки
    - работа с ридерами через HTTP-запросы
    - Web API, созданный в соответствии с архитектурным стилем RESTful API
    - понятный и протестированный код (``unittests``)
    - непонятный код в ``logic.py``
    - ничего не работает
    - Маруся


Устройство репозитория
----------------------

..  warning::

    Файлы из FEIG SDK не добавлены в репозиторий, их нужно будет самостоятельно скопировать в нужные директории

- ``/lib`` — FEIG SDK (заголовочные файлы)

- ``/RFID`` — папка проекта Visual Studio

    - ``dllmain.cpp``
    - ``RFID.vcxproj``
    - ``RFID.sln``

- ``/module`` — основная папка модуля

    - ``RFID.dll``
    - ``reader.py`` — обёртка над C++-модулем, работа с ридером
    - ``logic.py``
    - ``FedmIscCoreVC110.dll``, ``feisc.dll``, ``fefu.dll``, ``fecom.dll``, ``fetcl.dll`` — файлы из FEIG SDK, необходимые для работы ``RFID.dll``


Устройство модуля
-----------------

..  image:: _static/RFID-модуль.png
    :align: center

..  toctree::

   start
   web_api


..
    Indices and tables
    ==================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
