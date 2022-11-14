import json

import requests
from typing import Optional
from config_data import config

# город, ID районов города
url_city = "https://hotels4.p.rapidapi.com/locations/v2/search"
# ID города, гостиница, адрес, цена, удаленность от центра
url_hotel = "https://hotels4.p.rapidapi.com/properties/list"
# фото гостиницы по ID
url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"


headers = {
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
	"X-RapidAPI-Key": config.RAPID_API_KEY
}


def city_search(user_city: str) -> Optional[dict]:
	"""
	Запрос к API сайта для получения названия города/района города и его ID
	:param user_city: введеный пользователем город
	:return: словарь с ключем: название города/района города; значение: ID
	"""
	city_querystring = {"query": user_city, "locale": "ru_RU", "currency": "RUB"}
	city_response = requests.request("GET", url_city, headers=headers, params=city_querystring, timeout=15)
	cities_dict = {}
	if city_response.status_code == 200:
		dict_city_response = json.loads(city_response.text)
		districts = dict_city_response['suggestions'][0]['entities']
		for dist in districts:
			cities_dict[dist['name']] = dist['destinationId']
		if len(cities_dict) == 0:
			return None
		return cities_dict
	else:
		return None


def hotel_search(
		city_id: str,
		check_in: str,
		check_out: str,
		sort: str,
		min_price: str,
		max_price: str,
		distance: str
) -> Optional[list]:
	"""
	Запрос к API сайта для получения списка отелей
	:param city_id: ID города/района, выбранного пользователем
	:param check_in: дата заезда
	:param check_out: дата выезда
	:param sort: параметр сортировки списка результатов
	:param distance: максимальное расстояние до центра
	:param max_price: максимальная стоимость проживания в сутки
	:param min_price: минимальная стоимость проживания в сутки
	:return: словарь с отелями
	"""
	hotel_querystring = {
		"destinationId": city_id,
		"pageNumber": "1",
		"pageSize": "100",
		"checkIn": check_in,
		"checkOut": check_out,
		"adults1": "1",
		"sortOrder": sort,
		"locale": "ru_RU",
		"currency": "RUB"
	}
	if hotel_querystring['sortOrder'] == 'DISTANCE_FROM_LANDMARK':
		hotel_querystring['priceMin'] = min_price
		hotel_querystring['priceMax'] = max_price
		hotels_result = []
		hotel_response = requests.request("GET", url_hotel, headers=headers, params=hotel_querystring, timeout=30)
		if hotel_response.status_code == 200:
			hotels_dict_result = json.loads(hotel_response.text)
			hotels_list = hotels_dict_result['data']['body']['searchResults']['results']
			for hotel in hotels_list:
				if float(hotel['landmarks'][0]['distance'].replace(',', '.').split(' ')[0]) <= int(distance):
					hotels_result.append(hotel)
			if len(hotels_result) > 0:
				return hotels_result
			else:
				return None
		else:
			return None

	else:
		hotel_response = requests.request("GET", url_hotel, headers=headers, params=hotel_querystring, timeout=30)
		if hotel_response.status_code == 200:
			hotels_dict_result = json.loads(hotel_response.text)
			hotels_result = hotels_dict_result['data']['body']['searchResults']['results']
			return hotels_result
		else:
			return None


def photo_search(hotel_id: str, num: int) -> Optional[list]:
	"""
	Запрос к API для получения фото отеля
	:param hotel_id: ID отеля
	:param num: количество фото для вывода в результат
	:return: список с ссылками на фото
	"""
	photo_querystring = {"id": hotel_id}
	photo_response = requests.request("GET", url_photos, headers=headers, params=photo_querystring)
	if photo_response.status_code == 200:
		hotel_photos_dict = json.loads(photo_response.text)
		list_photos = hotel_photos_dict["hotelImages"]
		url_results = []
		for info in list_photos:
			url_photo = str(info['baseUrl']).split('_')[0] + '.jpg'
			url_results.append(url_photo)
		return url_results[:num]
	else:
		return None
