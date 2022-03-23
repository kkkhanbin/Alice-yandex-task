import math

import requests

from src.resources.skills.skill import Skill


class CityAssistant(Skill):
    def handle_dialog(self, request, response):
        user_id = request['session']['user_id']
        if request['session']['new']:
            response['response']['text'] = \
                'Привет! Я могу показать город или ' \
                'сказать расстояние между городами!'
            return
        # Получаем города из нашего
        cities = self.get_cities(request)
        if not cities:
            response['response'][
                'text'] = 'Ты не написал название не одного города!'
        elif len(cities) == 1:
            response['response']['text'] = 'Этот город в стране - ' + \
                                      self.get_geo_info(cities[0], 'country')
        elif len(cities) == 2:
            distance = self.get_distance(
                self.get_geo_info(cities[0], 'coordinates'),
                self.get_geo_info(cities[1], 'coordinates'))
            response['response']['text'] = \
                'Расстояние между этими городами: ' + \
                str(round(distance)) + ' км.'
        else:
            response['response']['text'] = 'Слишком много городов!'

    @staticmethod
    def get_cities(request):
        cities = []
        for entity in request['request']['nlu']['entities']:
            if entity['type'] == 'YANDEX.GEO':
                if 'city' in entity['value']:
                    cities.append(entity['value']['city'])
        return cities

    @staticmethod
    def get_distance(p1, p2):
        # p1 и p2 - это кортежи из двух элементов - координаты точек
        radius = 6373.0

        lon1 = math.radians(p1[0])
        lat1 = math.radians(p1[1])
        lon2 = math.radians(p2[0])
        lat2 = math.radians(p2[1])

        d_lon = lon2 - lon1
        d_lat = lat2 - lat1

        a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(
            lat2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

        distance = radius * c
        return distance

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

    @staticmethod
    def get_coordinates(city_name):
        try:
            # url, по которому доступно API Яндекс.Карт
            url = "https://geocode-maps.yandex.ru/1.x/"
            # параметры запроса
            params = {
                "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                # город, координаты которого мы ищем
                'geocode': city_name,
                # формат ответа от сервера, в данном случае JSON
                'format': 'json'
            }
            # отправляем запрос
            response = requests.get(url, params)
            # получаем JSON ответа
            json = response.json()
            # получаем координаты города
            # (там написаны долгота(longitude), широта(latitude) через пробел)
            # посмотреть подробное описание JSON-ответа можно
            # в документации по адресу https://tech.yandex.ru/maps/geocoder/
            coordinates_str = json['response']['GeoObjectCollection'][
                'featureMember'][0]['GeoObject']['Point']['pos']
            # Превращаем string в список, так как
            # точка - это пара двух чисел - координат
            long, lat = map(float, coordinates_str.split())
            # Вернем ответ
            return long, lat
        except Exception as e:
            return e

    def get_geo_info(self, city_name, type_info):
        if type_info == 'country':
            return self.get_country(city_name)
        elif type_info == 'coordinates':
            return self.get_coordinates(city_name)
