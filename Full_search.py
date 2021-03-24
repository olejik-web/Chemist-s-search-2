import sys
from pprint import pprint
from Need_Function import need_function, lonlat_distance
from io import BytesIO
import requests
from PIL import Image
toponym_to_find = input()
# object_width, object_height = int(input()), int(input())
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json",
    }
response = requests.get(geocoder_api_server, params=geocoder_params)
if not response:
    pass
json_response = response.json()
# pprint(json_response)
object_width, object_height = need_function(json_response)
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
toponym_coodrinates = toponym["Point"]["pos"]
toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": ",".join([str(object_width), str(object_height)]),
    "l": "map",
    'pt': '{},{},pmwtm1'.format(toponym_longitude, toponym_lattitude)
}
map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)
global_object_width = object_width
global_object_height = object_height
distance = 0
name = ''
chemist_address = ''
work_time = ''
def find_chemist():
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    address_ll = ",".join([toponym_longitude, toponym_lattitude])
    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }
    response = requests.get(search_api_server, params=search_params)
    if not response:
        pass    
    json_response = response.json()
    object_width, object_height = need_function(json_response)
    organization = json_response["features"][0]
    global name
    global chemist_address
    global work_time
    work_time = organization["properties"]["CompanyMetaData"]["Hours"]['text']
    name = organization["properties"]["CompanyMetaData"]["name"]
    chemist_address = organization["properties"]["CompanyMetaData"]["address"]
    point = organization["geometry"]["coordinates"]
    global distance
    distance = lonlat_distance((float(point[0]), float(point[1])), 
                               (float(toponym_longitude), 
                                float(toponym_lattitude)))
    org_point = "{0},{1}".format(point[0], point[1])
    map_params = {
        "ll": org_point,
        "spn": ",".join([str((object_width + global_object_width) * 3), 
                         str((object_height + global_object_height) * 3)]),
        "l": "map",
        "pt": '~'.join(("{0},pma".format(org_point), 
                        "{0},pmb".format(address_ll)))
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)  
    return response
Image.open(BytesIO(find_chemist().content)).show()
print('Расстояние:', distance)
print('Work time:', work_time)
print('Name:', name)
print('Address:', chemist_address)