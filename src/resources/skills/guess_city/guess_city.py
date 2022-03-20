from random import choice

from src.resources.skills.skill import Skill


class GuessCity(Skill):
    INIT_CITIES = {
        'москва': ['1533899/b3a00a1f31ab1d664699'],
        'нью-йорк': ['1030494/26316c9fda1b9bef5760'],
        'париж': ['1521359/b76a945d7e6fcf29c351']
    }
    START_GAME_WORDS = ['начать', 'старт', 'поехали']

    def handle_dialog(self, request, response):
        user_id = request['session']['user_id']

        # 1. Просьба представиться нового пользователя
        if request['session']['new']:
            self.say(response, 'Привет! Назови свое имя!')
            self.init_dialog(request)
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

        # 4. Проверка ответа
        guess_city = self.get_city(request)

        if guess_city is None:
            self.say(response, 'Ты не назвал город!')
            return

        if guess_city.lower() == self.sessionStorage[user_id]['guess_city']:
            if len(self.sessionStorage[user_id]['cities']) == 0:
                message = 'Ты угадал! К сожалению ты угадал все города и' \
                          ' поэтому я не смогу больше с тобой играть! Пока.'
                self.say(response, message)
                response['end_session']['response'] = True
                return
            else:
                self.ask_city(request, response)
        else:
            self.say(response, 'Неправильно! Попробуй еще')

    def init_dialog(self, request):
        user_id = request['session']['user_id']
        self.sessionStorage[user_id] = {
            'first_name': None,
            'started': False,
            'guess_city': None,
            'cities': self.INIT_CITIES
        }

    def ask_city(self, request, response):
        user_id = request['session']['user_id']
        cities = self.sessionStorage[user_id]['cities']
        city = choice(list(cities.keys()))

        self.sessionStorage[user_id]['guess_city'] = city

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

            response['response']['buttons'] = [
                {
                    'title': choice(self.START_GAME_WORDS),
                    'payload': {},
                    'hide': True
                }
            ]

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
            response['response']['buttons'] = [
                {
                    'title': choice(self.START_GAME_WORDS),
                    'payload': {},
                    'hide': True
                }
            ]

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
