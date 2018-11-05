from sqlalchemy import Column, Integer, Float, String, ForeignKey, UniqueConstraint, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'picture': self.picture
        }

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        user_id = data['id']
        return user_id


class Request(Base):
    __tablename__= 'request'
    id = Column(Integer, primary_key=True)
    meal_type = Column(String(32))
    meal_time = Column(String(32))
    location = Column(String(32))
    lat = Column(String)
    lon = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'meal_type': self.meal_type,
            'meal_time': self.meal_time,
            'location': self.location,
            'lat': self.lat,
            'lon:': self.lon,
            'user_id': self.user_id
        }


class Proposal(Base):
    __tablename__= 'proposal'

    id = Column(Integer, primary_key=True)
    request_id = Column(ForeignKey("request.id"), unique=True)
    user_proposed_from = Column(Integer, ForeignKey("user.id"))
    user_proposed_to = Column(Integer, ForeignKey("user.id"))
    date_and_time = Column(String)
    request = relationship(Request)

    proposed_from = relationship("User", foreign_keys=[user_proposed_from])
    proposed_to = relationship("User", foreign_keys=[user_proposed_to])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_proposed_from': self.user_proposed_from,
            'user_proposed_to': self.user_proposed_to,
            'request_id': self.request_id,
            'date_and_time': self.date_and_time
        }


class Meetup(Base):
    __tablename__='meetup'
    id = Column(Integer, primary_key=True)
    user_proposed_from = Column(Integer, ForeignKey("user.id"))
    user_proposed_to = Column(Integer, ForeignKey("user.id"))

    venue_name = Column(String)
    address = Column(String)
    date_and_time = Column(String)

    proposed_from = relationship("User", foreign_keys=[user_proposed_from])
    proposed_to = relationship("User", foreign_keys=[user_proposed_to])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_proposed_from': self.user_proposed_from,
            'user_proposed_to': self.user_proposed_to,
            'venue_name': self.venue_name,
            'address': self.address,
            'date_and_time': self.date_and_time
        }

engine = create_engine('sqlite:///usersWithOAuth.db')

Base.metadata.create_all(engine)
