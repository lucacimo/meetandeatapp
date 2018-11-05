from models import Base, User, Request, Proposal, Meetup
from flask import Flask, jsonify, request, abort, g, render_template
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from oauth import facebook, googleplus

from flask.ext.httpauth import HTTPBasicAuth
import json
import requests
from utilities import geo_location, valid_meal_time, valid_date_and_time

auth = HTTPBasicAuth()

engine = create_engine('sqlite:///usersWithOAuth.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

FOURSQUARE_CLIENT_ID = 'NR3JDICWIRELVJCHGT4JWJJIV2NROPO5NEUXGCBNQZDAXLTJ'
FOURSQUARE_SECRET = 'JLLLEYAFKXWACLTNOA4HKPF1JI201W30AK5LFHSQWH55UNSE'


def add_and_commit(obj):
    try:
        session.add(obj)
        session.commit()
    except:
        session.rollback()
        raise


def delete_and_commit(obj):
    try:
        session.delete(obj)
        session.commit()
    except:
        session.rollback()
        raise


@auth.verify_password
def verify_password(username_or_token, password):
    # Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/clientOAuth', methods=['GET'])
def test():
    return render_template('clientOAuth.html')


@app.route('/<provider>/login', methods=['POST', 'GET'])
def login(provider):
    if provider == 'facebook':
        if 'code' not in request.args:
            abort(400)

        redirect_uri = 'http://localhost:5000/facebook/login'
        data = dict(code=request.args['code'], redirect_uri=redirect_uri)
        user = facebook.get_auth_session(data=data, decoder=json.loads)
        me = user.get('me').json()

        params = {'fields': 'name,email,picture'}
        headers = {'Accept': '"application/json'}
        url = 'https://graph.facebook.com/v2.10/%s' % me['id']
        response = user.get(url=url, params=params, headers=headers)
        response = json.loads(response.text)

        name = response['name']
        picture = response['picture']['data']['url']
        email = response['email']

    if provider == 'google':
        if 'code' not in request.args:
            abort(400)

        redirect_uri = 'http://localhost:5000/google/login'
        data = dict(code=request.args['code'], redirect_uri=redirect_uri, grant_type='authorization_code')
        user = googleplus.get_auth_session(data=data, decoder=json.loads)

        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        response = user.get(url=url)
        response = json.loads(response.text)

        name = response['name']
        picture = response['picture']
        email = response['email']

    user = session.query(User).filter_by(email=email).first()
    if not user:
        user = User(username=name, picture=picture, email=email)
        session.add(user)
        session.commit()

    token = user.generate_auth_token(600)

    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/v1/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/api/v1/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if username is None or password is None:
        abort(400)

    if session.query(User).filter_by(email=email).first() is not None:
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message': 'user already exists'}), 200
    user = User(username=username)
    user.hash_password(password)
    if email:
        user.email = email
    else:
        user.email = ''

    session.add(user)
    session.commit()
    return jsonify(
        {'username': user.username}), 201


@app.route('/api/v1/users', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def users_handler():

    if request.method == 'GET':
        users = session.query(User).all()
        user_list = [user.serialize for user in users]
        return jsonify({'users': user_list})

    if request.method == 'PUT':
        username = request.json.get('username')
        email = request.json.get('email')
        picture = request.json.get('picture')

        user = session.query(User).filter_by(username=g.user.username).first()

        if username:
            user.username = username
        if email:
            user.email = email
        if picture:
            user.picture = picture

        session.add(user)
        session.commit()

    if request.method == 'DELETE':
        user = session.query(User).filter_by(username=g.user.username).first()
        session.delete(user)
        session.commit()

    return jsonify({'user': user.username})


@app.route('/api/v1/users/<int:id>')
@auth.login_required
def get_user(id):
    user = session.query(User).filter_by(id=id).first()
    if not user:
        abort(404)
    return jsonify(user.serialize)


@app.route('/api/v1/request', methods=['POST', 'GET'])
@auth.login_required
def requests_handler():

    if request.method == 'POST':
        meal_type = request.json.get('meal_type')
        meal_time = request.json.get('meal_time')
        location = request.json.get('location')

        if meal_type is None or meal_time is None or location is None:
            abort(400)

        if not valid_meal_time(meal_time):
            abort(400)

        request_event = Request(meal_type=meal_type, meal_time=meal_time, location=location)
        request_event.user_id = g.user.id

        location = location.replace(" ", "")
        lat, lon = geo_location(location)

        request_event.lat = lat
        request_event.lon = lon
        add_and_commit(request_event)

        return jsonify(request_event.serialize)

    if request.method == 'GET':
        event_requests = session.query(Request).all()
        event_requests_list = [event_request.serialize for event_request in event_requests]

        return jsonify({'requests': event_requests_list})


@app.route('/api/v1/request/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def request_handler(id):
    if request.method == 'GET':
        event_request = session.query(Request).filter_by(id=id).first()
        if not event_request:
            abort(404)
        return jsonify(event_request.serialize)

    if request.method == 'PUT':

        event_request = session.query(Request).filter_by(id=id).first()
        if event_request.user_id != g.user.id:
            abort(400)

        meal_type = request.json.get('meal_type')
        meal_time = request.json.get('meal_time')
        location = request.json.get('location')

        if meal_type:
            event_request.meal_type = meal_type
        if meal_time:
            if not valid_meal_time(meal_time):
                abort(400)
                event_request.meal_time = meal_time
            event_request.meal_time = meal_time

        if location:
            lat, lon = geo_location(location)
            event_request.location = location
            event_request.lat = lat
            event_request.lon = lon

        add_and_commit(event_request)

    if request.method == 'DELETE':
        event_request = session.query(Request).filter_by(id=id).first()
        if event_request.user_id != g.user.id:
            abort(400)

        delete_and_commit(event_request)

    return jsonify(event_request.serialize)


@app.route('/api/v1/proposal', methods=['POST', 'GET'])
@auth.login_required
def proposals_handler():
    if request.method == 'POST':
        user_proposed_to = request.json.get("user_proposed_to")
        request_id = request.json.get("request_id")
        date_and_time = request.json.get("date_and_time")

        if user_proposed_to is None or request_id is None or date_and_time is None:
            abort(400)

        if not valid_date_and_time(date_and_time):
            abort(400)

        event_request = session.query(Request).filter_by(id=request_id).first()
        if event_request.user_id == g.user.id or g.user.id == user_proposed_to:
            abort(400)

        proposal = Proposal(user_proposed_from=g.user.id,
                            user_proposed_to=user_proposed_to,
                            request_id=request_id,
                            date_and_time=date_and_time)

        add_and_commit(proposal)

        return jsonify(proposal.serialize)

    if request.method == 'GET':
        proposals = session.query(Proposal) \
        .filter((Proposal.user_proposed_to == g.user.id) | (Proposal.user_proposed_from == g.user.id))

        proposal_list = [proposal.serialize for proposal in proposals]

        return jsonify({'proposals': proposal_list})


@app.route('/api/v1/proposal/<int:id>', methods=['PUT', 'GET', 'DELETE'])
@auth.login_required
def proposal_handler(id):
    if request.method == 'PUT':
        proposal = session.query(Proposal).filter_by(id=id).first()

        if not proposal:
            abort(404)
        if g.user.id != proposal.user_proposed_from:
            abort(400)

        user_proposed_to = request.json.get("user_proposed_to")
        request_id = request.json.get("request_id")

        if user_proposed_to:
            proposal.user_proposed_to = user_proposed_to
        if request_id:
            proposal.request_id = request_id

        add_and_commit(proposal)

    if request.method == 'GET':
        proposal = session.query(Proposal).filter_by(id=id).first()
        if not proposal:
            abort(404)
        if g.user.id != proposal.user_proposed_to and g.user.id != proposal.user_proposed_from:
            abort(400)

    if request.method == 'DELETE':
        proposal = session.query(Proposal).filter_by(id=id).first()

        if g.user.id != proposal.user_proposed_from:
            abort(400)
        delete_and_commit(proposal)

    return jsonify(proposal.serialize)


@app.route('/api/v1/meetups', methods=['POST', 'GET'])
@auth.login_required
def meetups_handler():
    if request.method == 'POST':
        proposal_id = request.json.get("proposal_id")

        if proposal_id is None:
            abort(400)
        proposal = session.query(Proposal).filter_by(id=proposal_id).first()
        if not proposal:
            abort(400)
        if proposal.user_proposed_from == g.user.id or proposal.user_proposed_to != g.user.id:
            abort(400)

        event_request = session.query(Request).filter_by(id=proposal.request_id).first()
        url = 'https://api.foursquare.com/v2/venues/explore'
        params = {
            'client_id': FOURSQUARE_CLIENT_ID,
            'client_secret': FOURSQUARE_SECRET,
            'v':'20170801',
            'll': "%s,%s" % (event_request.lat, event_request.lon),
            'query': event_request.meal_type,
            'limit': 5
        }
        resp = requests.get(url=url, params=params)
        data = json.loads(unicode(resp.text))

        venue = data['response']['groups'][0]['items'][0]['venue']
        name = venue['name']

        if 'address' in venue['location']:
                address = "%s, %s" %(venue['location']['address'], venue['location']['city'])
        else:
            address = venue['location']['city']

        meetup = Meetup(user_proposed_from=proposal.user_proposed_from,
                        user_proposed_to=proposal.user_proposed_to,
                        venue_name=name,
                        address=address,
                        date_and_time=proposal.date_and_time)

        add_and_commit(meetup)

        return jsonify(meetup.serialize)

    if request.method == 'GET':
        meetups = session.query(Meetup) \
            .filter((Meetup.user_proposed_to == g.user.id) | (Meetup.user_proposed_from == g.user.id))

        meetups_list = [proposal.serialize for proposal in meetups]

        return jsonify({'meetups': meetups_list})


@app.route('/api/v1/meetups/<int:id>', methods=['PUT', 'GET', 'DELETE'])
@auth.login_required
def meetup_handler(id):
    meetup = session.query(Meetup).filter_by(id=id).first()

    if not meetup:
        abort(404)
    if g.user.id != meetup.user_proposed_to and g.user.id != meetup.user_proposed_from:
        abort(400)

    if request.method == 'PUT':
        venue_name = request.json.get("venue_name")
        address = request.json.get("address")
        date_and_time = request.json.get("date_and_time")

        if venue_name:
            meetup.venue_name = venue_name
        if address:
            meetup.address = address
        if date_and_time:
            if not valid_date_and_time(date_and_time):
                abort(400)
            meetup.date_and_time = date_and_time
        add_and_commit(meetup)

        return jsonify(meetup.serialize)

    if request.method == 'GET':
        return jsonify(meetup.serialize)

    if request.method == 'DELETE':
        delete_and_commit(meetup)
        return jsonify(meetup.serialize)

if __name__ == '__main__':
    app.debug = True
    # app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='localhost', port=5000)