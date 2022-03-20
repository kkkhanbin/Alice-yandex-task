import random

from src.resources.skills.skill import Skill


class CityPhoto(Skill):
    CITIES = {
        'москва': ['1533899/b3a00a1f31ab1d664699'],
        'нью-йорк': ['1030494/26316c9fda1b9bef5760'],
        'париж': ['1521359/b76a945d7e6fcf29c351']
    }

    def handle_dialog(self, request, response):
        user_id = request['session']['user_id']

        # если пользователь новый, то просим его представиться.
        if request['session']['new']:
            response['response']['text'] = 'Привет! Назови свое имя!'
            # создаем словарь в который в будущем положим имя пользователя
            self.sessionStorage[user_id] = {'first_name': None}
            return

        # если пользователь не новый, то попадаем сюда.
        # если поле имени пустое, то это говорит о том,
        # что пользователь еще не представился.
        if self.sessionStorage[user_id]['first_name'] is None:
            # в последнем его сообщение ищем имя.
            first_name = self.get_first_name(request)
            # если не нашли, то сообщаем пользователю что не расслышали.
            if first_name is None:
                response['response']['text'] = \
                    'Не расслышала имя. Повтори, пожалуйста!'
            # если нашли, то приветствуем пользователя.
            # И спрашиваем какой город он хочет увидеть.
            else:
                self.sessionStorage[user_id]['first_name'] = first_name
                response['response'][
                    'text'] = 'Приятно познакомиться, ' \
                              + first_name.title() \
                              + '. Я - Алиса. Какой город хочешь увидеть?'
                # получаем варианты buttons из ключей нашего словаря cities
                response['response']['buttons'] = [
                    {
                        'title': city.title(),
                        'hide': True
                    } for city in self.CITIES
                ]
        # если мы знакомы с пользователем и он нам что-то написал,
        # то это говорит о том, что он уже говорит о городе,
        # что хочет увидеть.
        else:
            # ищем город в сообщение от пользователя
            city = self.get_city(request)
            # если этот город среди известных нам,
            # то показываем его (выбираем одну из двух картинок случайно)
            if city in self.CITIES:
                response['response']['card'] = {}
                response['response']['card']['type'] = 'BigImage'
                response['response']['card']['title'] = 'Этот город я знаю.'
                response['response']['card']['image_id'] = random.choice(
                    self.CITIES[city])
                response['response']['text'] = 'Я угадал!'
            # если не нашел, то отвечает пользователю
            # 'Первый раз слышу об этом городе.'
            else:
                response['response']['text'] = \
                    'Первый раз слышу об этом городе. Попробуй еще разок!'

    @staticmethod
    def get_city(request):
        # перебираем именованные сущности
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
