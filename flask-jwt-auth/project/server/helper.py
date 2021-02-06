import datetime
from flask import request, make_response, jsonify

from project.server.models import User


def require_logged_in_user(view_func):
    """
    Decorator ensuring that a valid user made the request.
    """
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            decoded_data = User.decode_auth_token(auth_token)
            if not isinstance(decoded_data, str):
                token_response, user = decoded_data[0], decoded_data[1]
                return view_func(*args, **kwargs, user=user, token_response=token_response)
            responseObject = {
                'status': 'fail',
                'message': decoded_data
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401
    return decorated


def get_auth_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(" ")[1]
    else:
        return ''



def filter_non_available_items(items):
    week_day = datetime.datetime.today().weekday()
    current_time = datetime.datetime.now()
    present_day_time = (current_time.hour * 60) + current_time.minute
    for item in items:
        for hours_info in item.item_available_hours:
            if hours_info['day'] == str(week_day) and present_day_time > hours_info['opens_at'] and present_day_time < hours_info['closes_at']:
                yield item
