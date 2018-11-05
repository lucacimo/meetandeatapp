import httplib2
import json
import datetime

API_KEY = 'AIzaSyCu04p0LvyjuUVP1PKGRyI_i1vTHqRI_cg'


def geo_location(location):

    location = location.replace(" ", "")
    url = 'https://maps.googleapis.com/maps/api/geocode/json?&address=%s&key=%s' % (location, API_KEY)
    r = httplib2.Http()
    result = json.loads(r.request(url, 'GET')[1])

    lat = "{0:.2f}".format(result['results'][0]['geometry']['location']['lat'])
    lon = "{0:.2f}".format(result['results'][0]['geometry']['location']['lng'])

    return lat, lon


def valid_meal_time(meal_time):
    if meal_time != 'breakfast' and meal_time != 'lunch' and meal_time != 'dinner':
        return False
    else:
        return True


def valid_date_and_time(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M')
        return True
    except ValueError as err:
        return False