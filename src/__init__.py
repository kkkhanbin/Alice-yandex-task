import logging

from flask import Flask
from flask_restful import Api

from src.config import Config
from src.resources.skills import Elephant, GuessCity, CityPhoto


def add_resources(api: Api, *resources):
    """
    Добавляет ресурсы в Api
    :param resources: Коллекция, где первое значение - ресурс, а второе - путь
    """

    for resource, route in resources:
        api.add_resource(resource, route)


# Создание приложения
app = Flask(__name__)
app.config.from_object(Config)

# Инициализация расширений
api = Api(app)
add_resources(
    api, (Elephant, '/skill/elephant'), (GuessCity, '/skill/guess_city'),
    (CityPhoto, '/skill/city_photo'))

logging.basicConfig(level=logging.INFO)
