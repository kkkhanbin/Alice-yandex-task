import logging

from flask import Flask
from flask_restful import Api

from src.config import Config
from src.resources import Elephant

# Создание приложения
app = Flask(__name__)
app.config.from_object(Config)

# Инициализация расширений
api = Api(app)
api.add_resource(Elephant, '/post')

logging.basicConfig(level=logging.INFO)
