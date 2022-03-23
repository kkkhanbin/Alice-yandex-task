import requests

from src.resources.skills.skill import Skill


class Translator(Skill):
    def handle_dialog(self, request, response):
        tokens = request['request']['nlu']['tokens']

        if request['session']['new']:
            response['response']['text'] = \
                'Привет, это русско-английский переводчик. ' \
                'Вводи любые слова и я их переведу'
            return

        response['response']['text'] = self.translate(' '.join(tokens))

    @staticmethod
    def translate(text):
        url = "https://translated-mymemory---" \
              "translation-memory.p.rapidapi.com/api/get"

        querystring = {"langpair": "ru|en", "q": text, "mt": "1",
                       "onlyprivate": "0", "de": "a@b.c"}

        headers = {
            'x-rapidapi-key':
                "cf310ba722msh9a748fa70e3d17ep1d069bjsndbacc72e62b3",
            'x-rapidapi-host':
                "translated-mymemory---translation-memory.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers,
                                    params=querystring)

        return response.json()['responseData']['translatedText']


print(Translator.translate('Привет стекло'))
