import logging

from flask import Flask
from flask_restful import Api

from src.config import Config
from src.resources.skills import Elephant, GuessCity

# Создание приложения
app = Flask(__name__)
app.config.from_object(Config)

# Инициализация расширений
api = Api(app)
api.add_resource(Elephant, '/skill/elephant')
api.add_resource(GuessCity, '/skill/guess_city')

logging.basicConfig(level=logging.INFO)
