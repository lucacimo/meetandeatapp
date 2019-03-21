import os

FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')
FACEBOOK_SECRET = os.getenv('FACEBOOK_SECRET')
FACEBOOK_ACCESS_TOKEN_URL = os.getenv('FACEBOOK_ACCESS_TOKEN_URL')

GOOGLE_PLUS_CLIENT_ID = os.getenv('GOOGLE_PLUS_CLIENT_ID')
GOOGLE_PLUS_SECRET = os.getenv('GOOGLE_PLUS_SECRET')
GOOGLE_PLUS_ACCESS_TOKEN_URL = os.getenv('GOOGLE_PLUS_ACCESS_TOKEN_URL')

FACEBOOK_REDIRECT_URI = 'https://meetandeatapp.herokuapp.com/facebook/login'
GOOGLE_REDIRECT_URI = 'https://meetandeatapp.herokuapp.com/google/login'

FOURSQUARE_CLIENT_ID = os.getenv('FOURSQUARE_CLIENT_ID')
FOURSQUARE_SECRET = os.getenv('FOURSQUARE_SECRET')

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
