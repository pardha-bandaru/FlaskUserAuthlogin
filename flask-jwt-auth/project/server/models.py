# project/server/models.py
import jwt
import datetime
from mongoengine.errors import ValidationError

from mongoengine.fields import (
    DateTimeField, DictField, IntField, ListField, SequenceField,
    StringField, EmailField, ReferenceField, MapField, EmbeddedDocumentField)


from project.server import app, db, bcrypt


class User(db.DynamicDocument):
    """ User Model for storing user related details """
    id = SequenceField(required=True, primary_key=True)
    user_name = StringField(min_length=4)
    password = StringField(required=True)
    email = EmailField(required=True, unique=True)
    phone = StringField(min_length=10, required=True, unique=True)
    registered_on = DateTimeField(default=datetime.datetime.now)

    def clean(self):
        self.password = bcrypt.generate_password_hash(
            self.password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
    
    meta = {
        "indexes": ["email", "phone"],
        "ordering": ["-registered_on"]
    }

    @staticmethod
    def encode_auth_token(user_id):
        """
        Generates the Auth Token
        :return: string
        """
        user_id = str(user_id)
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=5, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload, User.objects.get(id=payload['sub'])
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class BlacklistToken(db.DynamicDocument):
    """
    Token Model for storing JWT tokens
    """
    id = SequenceField(required=True, primary_key=True)
    token = StringField(max_length=500, required=True, unique=True)
    blacklisted_on = DateTimeField(default=datetime.datetime.now)


    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.objects(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

class Cafeteria(db.DynamicDocument):
    id = SequenceField(required=True, primary_key=True)
    cafe_owner = ReferenceField(User)
    cafe_name = StringField(min_length=4)
    city = StringField(required=True)
    address = StringField(required=True)
    pincode = IntField(required=True)
    cafe_start_time = IntField(min_value=0, max_value=1440, required=True)
    cafe_close_time = IntField(min_value=0, max_value=1440, required=True)
    registered_on = DateTimeField(default=datetime.datetime.now)

    def clean(self):
        opens_at = self.cafe_start_time
        closes_at = self.cafe_close_time
        if closes_at < opens_at or not isinstance(closes_at, int) or not isinstance(opens_at, int):
            raise ValidationError("Invalid Opening and closing hours")


class Item(db.DynamicDocument):
    id = SequenceField(required=True, primary_key=True)
    cafe = ReferenceField(Cafeteria)
    item_name = StringField(required=True)
    item_available_hours = ListField(DictField())

    def clean(self):
        item_available_hours = self.item_available_hours
        if len(item_available_hours) != 7:
            raise ValidationError("Total week days not matching. Need to fill for all week")
        for day_opening_timings in item_available_hours:
            opens_at = day_opening_timings.get("opens_at")
            closes_at = day_opening_timings.get("closes_at")
            if closes_at < opens_at or not isinstance(closes_at, int) or not isinstance(opens_at, int):
                raise ValidationError("Invalid Opening and closing hours")
    