from random import choice

import requests

from src.resources.skills.skill import Skill


class GuessCity(Skill):
    INIT_CITIES = {
        'москва': ['1533899/b3a00a1f31ab1d664699'],
        'нью-йорк': ['1030494/26316c9fda1b9bef5760'],
        'париж': ['1521359/b76a945d7e6fcf29c351']
    }
    START_GAME_WORDS = ['начать', 'старт', 'поехали']
    HELP_WORDS = ['помощь']
    HELP_MESSAGE = \
        'Это игра "Угадай город по фото". Вам показывается фото города и вы ' \
        'должны угадать название этого города.'
    SHOW_MAP_MESSAGE = 'Покажи город на карте'

    def handle_dialog(self, request, response):
        user_id = request['session']['user_id']

        # 1. Просьба представиться нового пользователя
        if request['session']['new']:
            self.say(response, f'Привет! {self.HELP_MESSAGE} Назови свое имя!')
            self.init_dialog(request, response)
            return

        # 2. Получение имени пользователя
        if self.sessionStorage[user_id]['first_name'] is None:
            self.get_name(request, response)
            return

        # 3. Согласие на игру
        if not self.sessionStorage[user_id]['started']:
            if self.start_game(request, response) is False:
                return
            else:
                self.ask_city(request, response)

        self.add_button(response, 'Помощь')

        # 4. Проверка ответа
        tokens = request['request']['nlu']['tokens']
        if 'command' in request['request']:
            command = request['request']['command']
        else:
            command = ' '.join(tokens)
        guess_city = self.get_city(request)

        for help_word in self.HELP_WORDS:
            if help_word in tokens:
                self.say(response, self.HELP_MESSAGE)
                return

        if not self.sessionStorage[user_id]['question_set']:
            if 'нет' in tokens:
                self.exit(response)
                return
            elif 'да' in tokens:
                self.ask_city(request, response)
                return
            elif self.SHOW_MAP_MESSAGE.lower() in command:
                self.ask_play_again(response)
                return

        if self.sessionStorage[user_id]['city_guessed']:
            if self.get_country(
                    self.sessionStorage[user_id]['guess_city']).lower() in\
                    tokens:
                self.ask_play_again(response)
                self.sessionStorage[user_id]['city_guessed'] = False
                self.sessionStorage[user_id]['question_set'] = False
            else:
                self.say(response, 'Неправильно! Попробуй еще')
            return

        if guess_city is None:
            self.say(response, 'Ты не назвал город!')
            return

        if guess_city.lower() == self.sessionStorage[user_id]['guess_city']:
            self.add_button(
                response, self.SHOW_MAP_MESSAGE,
                f'https://yandex.ru/maps/?mode=search&text={guess_city}')

            if len(self.sessionStorage[user_id]['cities']) == 0:
                message = 'Ты угадал! К сожалению ты угадал все города и' \
                          ' поэтому я не смогу больше с тобой играть! Пока.'
                self.say(response, message)
                self.exit(response)
                return
            else:
                self.say(response, 'Правильно! А в какой стране этот город?')
                self.sessionStorage[user_id]['city_guessed'] = True
                return
        else:
            self.say(response, 'Неправильно! Попробуй еще')

    def ask_play_again(self, response):
        self.say(response, 'Правильно! Сыграем еще?')
        self.add_button(response, 'Да')
        self.add_button(response, 'Нет')

    @staticmethod
    def add_button(response, title, url = None):
        button = {
            'title': title,
            'payload': {},
            'hide': True
        }

        if url is not None:
            button['url'] = url

        response['response']['buttons'].append(button)

    def init_dialog(self, request, response):
        user_id = request['session']['user_id']
        self.sessionStorage[user_id] = {
            'first_name': None,
            'started': False,
            'guess_city': None,
            'cities': self.INIT_CITIES.copy(),
            'question_set': False,
            'city_guessed': False
        }

    def ask_city(self, request, response):
        user_id = request['session']['user_id']
        cities = self.sessionStorage[user_id]['cities']
        city = choice(list(cities.keys()))

        self.sessionStorage[user_id]['guess_city'] = city
        self.sessionStorage[user_id]['question_set'] = True

        response['response']['card'] = {}
        response['response']['card']['type'] = 'BigImage'
        response['response']['card']['title'] = 'Угадай этот город!'
        response['response']['card']['image_id'] = choice(cities[city])
        self.say(response, 'Угадай этот город!')

        del self.sessionStorage[user_id]['cities'][city]

    def start_game(self, request, response):
        user_id = request['session']['user_id']
        tokens = request['request']['nlu']['tokens']

        for start_word in self.START_GAME_WORDS:
            # Если стартовое слово было сказано
            if start_word in tokens:
                self.sessionStorage[user_id]['started'] = True

        # Стартовое слово не было сказано
        if not self.sessionStorage[user_id]['started']:
            self.say(response, 'Может, начнем игру?')
            self.add_button(
                response, choice(self.START_GAME_WORDS).capitalize())

            return False

    def get_name(self, request, response):
        user_id = request['session']['user_id']
        first_name = self.get_first_name(request)

        if first_name is None:
            self.say(response, 'Не расслышала имя. Повтори, пожалуйста!')
        else:
            self.sessionStorage[user_id]['first_name'] = first_name
            self.say(response, f'Приятно познакомиться, '
                               f'{first_name.title()}. Я - Алиса.')
            self.add_button(
                response, choice(self.START_GAME_WORDS).capitalize())

    @staticmethod
    def say(response, text: str):
        response['response']['text'] = text

    @staticmethod
    def get_city(request):
        # Перебираем именованные сущности
        for entity in request['request']['nlu']['entities']:
            # если тип YANDEX.GEO то пытаемся получить город(city),
            # если нет, то возвращаем None
            if entity['type'] == 'YANDEX.GEO':
                # возвращаем None, если не нашли сущности с типом YANDEX.GEO
                return entity['value'].get('city', None)

    @staticmethod
    def get_first_name(request):
        # перебираем сущности
        for entity in request['request']['nlu']['entities']:
            # находим сущность с типом 'YANDEX.FIO'
            if entity['type'] == 'YANDEX.FIO':
                # Если есть сущность с ключом 'first_name',
                # то возвращаем ее значение.
                # Во всех остальных случаях возвращаем None.
                return entity['value'].get('first_name', None)

    @staticmethod
    def get_country(city_name):
        try:
            url = "https://geocode-maps.yandex.ru/1.x/"
            params = {
                "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                'geocode': city_name,
                'format': 'json'
            }
            data = requests.get(url, params).json()
            # все отличие тут, мы получаем имя страны
            return data['response']['GeoObjectCollection'][
                'featureMember'][0]['GeoObject']['metaDataProperty'][
                'GeocoderMetaData']['AddressDetails']['Country']['CountryName']
        except Exception as e:
            return e

    def exit(self, response):
        response['response']['end_session'] = True
