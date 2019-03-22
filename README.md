# Overview
Meet & Eat is a social application for meeting people based on their food interests. The API backend is implemented using the Flask framework.

## Features
● Meet & Eat should leverage the Google Maps API and Foursquare API in order to find a
restaurant for users and geocode locations into latitude and longitude coordinates.

● Users should be able to log in with either a username/password combination or using an
OAuth provider like Google or Facebook. The application should generate it’s own
tokens for users.

https://meetandeatapp.herokuapp.com/

### Endpoints
HTTP Verb | Example URI | Description | Parameters | Logic/Security
------------ | ------------- | ------------- | ------------- | -------------
**POST** | *api/v1/\<provider\>/login* | Allows logging into a specific OAuth provider and returns an access token to the client. | - One-time Auto code | Server looks up user based upon the email address associated with the access token to identify user. <br> If no user exists, then a new one is created.
**POST** | *api/v1/\<provider\>/logout* | Allows logging out of an application and rejects an access token. | - Token | Server looks up user based upon the email address associated with the access token to identify user. <br> It user doesn't exist, return an error.
**GET** | *api/v1/users* | Returns profile information off all users in the database. | - Token | Only logged in users can view user profiles. 
**POST** | *api/v1/users* | Creates a new user without using OAuth. | - username <br> - password | highly recommended to implement secure HTTP if this endpoint is implemented. <br> As long as an existing username isn't in the database, create a new user, otherwise, return an appropriate error.
**PUT** | *api/v1/users/* | Updates a specific user's information. | - Token <br> - new user profile information | Server checks token to make sure only the logged in user can update its profile.
**GET** | *api/v1/users/\<int:id\>* | Returns information for a specific user. | - Token | Only logged in users can view profile information. 
**DELETE** | *api/v1/users/* | Removes a user account. | - Token | Only the user with the correct token can erase its account. 
**GET** | *api/v1/requests* | Shows all open meetup requests. | - Token | Only logged in users can view all open requests. <br> **Advanced feature**: a user should now see their own requests, only everyone else's. 
**POST** | *api/v1/requests* | Makes a new meetup request. | - Token <br> - meetup request information | Only logged in users can make meetup requests. The id of the maker of the request is stored in each request object. 
**GET** | *api/v1/requests/\<int:id\>* | Returns information for a specific meetup request. | - Token | Only logged in users can view the details of a meetup request. 
**PUT** | *api/v1/requests/\<int:id\>* | Updates information about a meetup request. | - Token <br> - new meetup request information | Only the original maker of the request should be able to edit it. 
**DELETE** | *api/v1/requests/\<int:id\>* | Deletes a specific meetup request. | - Token | Only the original maker of the request should be able to delete it.
**POST** | *api/v1/proposals* | Creates a new proposal to meetup on behalf of a user | -Token <br> -request_id | User is verified by the provided token and identified as the maker of the proposal.
**GET** | *api/v1/proposals/\<int:id\>* | Retrieves information about a specific proposal. | - Token | The id of the user should match either the proposal maker or recipient in order to access this view.
**PUT** | *api/v1/proposals/\<int:id\>* | Updates information about a specific proposal. | - Token <br> - New proposal information | The id of the user should match the proposal maker in order to access this view.
**DELETE** | *api/v1/proposals/\<int:id\>* | Deletes a specific proposal. | - Token | The id of the user should match the proposal maker in order to delete a proposal.
**GET** | *api/v1/dates* | Gets all dates for a corresponding user. | - Token | Only the dates that contain the user id as one of the participants should be viewable by that user.
**POST** | *api/v1/dates* | Creates a date request on behalf of a user | -Token <br> Boolean | If True, the recipient of a proposal has accepted this offer and is requesting that the server create a date. If false, the recipient of a proposal rejected a date and the proposal is deleted.
**GET** | *api/v1/dates/\<int:id\>* | Gets information about a specific date | -Token | Only dates where a user is a participant should appear in this view.
**PUT** | *api/v1/dates/\<int:id\>* | Edits information about a specific date | - Token <br> - New date information | Only participants in the date can update the date details.
**DELETE** | *api/v1/dates/\<int:id\>* | Removes a specific date | Token | Only participants in the date can delete a date object.

### Installing
Local

```
mkdir meetandeatapp
cd meetandeatapp
virtualenv -p pythonpath venv
source venv/bin/activate
pip install -r requirements.txt
python views.py
```



## Deployment on Heroku
```
heroku login
heroku create meetandeatapp --buildpack heroku/python
heroku git:remote -a meetandeatapp
git add .
git commit -m "First commit for heroku"
git push heroku master
```
Set the following environment variables: 
```
FACEBOOK_CLIENT_ID 
FACEBOOK_SECRET 
FACEBOOK_ACCESS_TOKEN_URL 

GOOGLE_PLUS_CLIENT_ID 
GOOGLE_PLUS_SECRET 
GOOGLE_PLUS_ACCESS_TOKEN_URL 

FACEBOOK_REDIRECT_URI 
GOOGLE_REDIRECT_URI 

FOURSQUARE_CLIENT_ID 
FOURSQUARE_SECRET 

GOOGLE_MAPS_API_KEY 
APP_SECRET_KEY 

PRODUCTION
```