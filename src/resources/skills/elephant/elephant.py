import json
import logging

from flask import request

from src.resources.skills.skill import Skill


class Elephant(Skill):
    SALE_ORDER = ['Слона', 'Кролика']
    PERMISSION_WORDS = ['ладно', 'куплю', 'покупаю', 'хорошо']
    INIT_SUGGESTS = ['Не хочу!', 'Не буду!', 'Отстань.']
    INIT_SALE_INDEX = 0

    def post(self):
        logging.info(f'Request: {request.json!r}')

        response = {
            'session': request.json['session'],
            'version': request.json['version'],
            'response': {
                'end_session': False
            }
        }

        logging.info(f'Response:  {response!r}')

        self.handle_dialog(request.json, response)

        return response

        # return json.dumps(response, ensure_ascii=False)

    def handle_dialog(self, request, response):
        user_id = request['session']['user_id']

        if request['session']['new']:
            # Это новый пользователь.
            # Инициализируем сессию и поприветствуем его.
            # Запишем подсказки, которые мы ему покажем в первый раз
            self.sessionStorage[user_id] = {
                'suggests': self.INIT_SUGGESTS,
                'sale_index': self.INIT_SALE_INDEX
            }

            # Заполняем текст ответа
            response['response']['text'] = \
                f'Привет! Купи {self.SALE_ORDER[self.INIT_SALE_INDEX]}!'
            # Получим подсказки
            response['response']['buttons'] = self.get_suggests(user_id)
            return

        # Пользователя нет в хранилище, но при этом значение
        # session.new = false, что скорее всего означает, что сервер был
        # перезапущен после начала игры
        if user_id not in self.sessionStorage:
            response['response']['text'] = \
                'Я тебя что-то не помню, начни игру заново'
            response['response']['end_session'] = True
            return

        sale_index = self.sessionStorage[user_id]['sale_index']
        sale_obj = self.SALE_ORDER[self.sessionStorage[user_id]['sale_index']]

        # Проверка на согласие покупки
        tokens = request['request']['nlu']['tokens']
        for token in tokens:
            # Здесь не используется функция lower потому что все токены
            # предварительно присылаются в нижнем регистре
            if token in self.PERMISSION_WORDS:

                # Если вещей для продажи не осталось
                if sale_index >= len(self.SALE_ORDER) - 1:
                    response['response']['text'] = \
                        f'{sale_obj} можно найти на Яндекс.Маркете!'
                    response['response']['end_session'] = True

                    return
                else:
                    self.sessionStorage[user_id]['sale_index'] += 1
                    sale_obj = self.SALE_ORDER[
                        self.sessionStorage[user_id]['sale_index']]

                    response['response']['text'] = \
                        f'Спасибо! Вот, держи, купишь еще {sale_obj}?!'

                    return

        # Убеждение в покупке
        response['response']['text'] = \
            f"Все говорят '{request['request']['original_utterance']}', " \
            f"а ты купи {sale_obj}!"
        response['response']['buttons'] = self.get_suggests(user_id)

    def get_suggests(self, user_id):
        sale_obj = self.SALE_ORDER[self.sessionStorage[user_id]['sale_index']]
        session = self.sessionStorage[user_id]

        # Выбираем две первые подсказки из массива.
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in session['suggests'][:2]
        ]

        # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
        session['suggests'] = session['suggests'][1:]
        self.sessionStorage[user_id] = session

        # Если осталась только одна подсказка, предлагаем подсказку
        # со ссылкой на Яндекс.Маркет.
        if len(suggests) < 2:
            suggests.append({
                "title": "Ладно",
                "url": f"https://market.yandex.ru/search?text={sale_obj}",
                "hide": True
            })

        return suggests
