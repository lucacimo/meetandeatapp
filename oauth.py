from rauth import OAuth2Service

FACEBOOK_CLIENT_ID = '1854520568210189'
FACEBOOK_SECRET = '3400f584edd4b57456bef3c04ac3deff'

GOOGLE_PLUS_CLIENT_ID = '100069966217-3g9gi0nc45krsh800sd87pniu08i148s.apps.googleusercontent.com'
GOOGLE_PLUS_SECRET = 'z1SITx4R5BkhZbI-1nrQwLgE'

facebook = OAuth2Service(
    client_id=FACEBOOK_CLIENT_ID,
    client_secret=FACEBOOK_SECRET,
    name='facebook',
    authorize_url='https://graph.facebook.com/oauth/authorize',
    access_token_url='https://graph.facebook.com/oauth/access_token',
    base_url='https://graph.facebook.com/')

googleplus = OAuth2Service(
    client_id=GOOGLE_PLUS_CLIENT_ID,
    client_secret=GOOGLE_PLUS_SECRET,
    name='google',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    base_url='https://accounts.google.com/o/oauth2/auth')