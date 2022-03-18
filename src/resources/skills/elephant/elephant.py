import json
import logging

from flask import request

from src.resources.skills.skill import Skill


class Elephant(Skill):
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
                'suggests': [
                    "Не хочу.",
                    "Не буду.",
                    "Отстань!",
                ]
            }
            # Заполняем текст ответа
            response['response']['text'] = 'Привет! Купи слона!'
            # Получим подсказки
            response['response']['buttons'] = self.get_suggests(user_id)
            return

        # Сюда дойдем только, если пользователь не новый,
        # и разговор с Алисой уже был начат
        # Обрабатываем ответ пользователя.
        # В req['request']['original_utterance'] лежит весь текст,
        # что нам прислал пользователь
        # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
        # то мы считаем, что пользователь согласился.
        tokens = request['nlu']['tokens']
        for token in tokens:
            # Здесь не используется функция lower потому что все токены
            # предварительно присылаются в нижнем регистре
            if token in ['ладно', 'куплю', 'покупаю', 'хорошо']:
                # Пользователь согласился, прощаемся.
                response['response']['text'] = \
                    'Слона можно найти на Яндекс.Маркете!'
                response['response']['end_session'] = True
                return

        # Если нет, то убеждаем его купить слона!
        response['response']['text'] = \
            f"Все говорят '{request['request']['original_utterance']}', " \
            f"а ты купи слона!"
        response['response']['buttons'] = self.get_suggests(user_id)

    def get_suggests(self, user_id):
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
                "url": "https://market.yandex.ru/search?text=слон",
                "hide": True
            })

        return suggests
