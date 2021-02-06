# project/server/infrastructure/views.py


from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from mongoengine.base import datastructures

from project.server.models import Cafeteria, Item
from project.server.helper import require_logged_in_user, filter_non_available_items

infra_blueprint = Blueprint('infra', __name__)


class CafeteriaAPI(MethodView):
    """
    Cafeteria Resource
    """
    @require_logged_in_user
    def get(self, cafe_id=None, user=None, token_response=None, **kwargs):
        if cafe_id:
            cafes = Cafeteria.objects(cafe_owner=user, id=cafe_id)
        else:
            cafes = Cafeteria.objects(cafe_owner=user)
        responseObject = {
            'status': 'success',
            'data': []
            }
        if cafes:
            for cafe in cafes:
                cafe_object = {
                    "cafe_id":cafe.id,
                    "name":cafe.cafe_name,
                    "cafe_opens_at":cafe.cafe_start_time,
                    "cafe_closes_at":cafe.cafe_close_time,
                    "cafe_address": cafe.address,
                    "cafe_pincode": cafe.pincode,
                    "cafe_city": cafe.city
                }
                responseObject['data'].append(cafe_object)
        return make_response(jsonify(responseObject)), 200
    
    @require_logged_in_user
    def post(self, user=None, token_response=None, **kwargs):
        post_data = request.get_json()
        cafe = Cafeteria(
            cafe_owner = user,
            cafe_name = post_data.get("name"),
            city = post_data.get("city"),
            address = post_data.get("address"),
            pincode = post_data.get("pincode"),
            cafe_start_time = post_data.get("start_time"),
            cafe_close_time = post_data.get("close_time")
        )
        cafe.save()
        responseObject = {
            'status': 'success',
            'data': {
                'cafe_id': cafe.id,
                'name': cafe.cafe_name,
                'city': cafe.city,
                'address': cafe.address,
                'pincode': cafe.pincode,
                'cafe_start_time': cafe.cafe_start_time,
                'cafe_close_time': cafe.cafe_close_time,
                'registered_on': cafe.registered_on,
                "msg":'cafeteria Created Successfully'
            }
        }
        return make_response(jsonify(responseObject)), 201
    
    @require_logged_in_user
    def delete(self, user=None, cafe_id=None, token_response=None, **kwargs):
        cafe = Cafeteria.objects(cafe_owner=user, id=cafe_id).get()
        cafe.delete()
        responseObject = {
            'status': 'success',
            'data': {
                "msg": f"Cafe {cafe.cafe_name} deleted Successfully"
            }
        }
        return make_response(jsonify(responseObject)), 200

    @require_logged_in_user
    def put(self, user=None, cafe_id=None, token_response=None, **kwargs):
        post_data = request.get_json()
        cafe = Cafeteria.objects.get(id=cafe_id)
        cafe.address = post_data.get("address")
        cafe.save()
        responseObject = {
            'status': 'success',
            'data': {
                'cafe_id': cafe.id,
                'name': cafe.cafe_name,
                'city': cafe.city,
                'address': cafe.address,
                'pincode': cafe.pincode,
                'cafe_start_time': cafe.cafe_start_time,
                'cafe_close_time': cafe.cafe_close_time,
                'registered_on': cafe.registered_on,
                "msg": f"Cafe {cafe.cafe_name} updated Successfully"
            }
        }
        return make_response(jsonify(responseObject)), 200



class ItemAPI(MethodView):
    """
    Item Resource
    """
    @require_logged_in_user
    def get(self, cafe_id=None, item_id=None, user=None, token_response=None, **kwargs):
        cafe = Cafeteria.objects.get(id=cafe_id)
        if item_id:
            items = Item.objects(cafe=cafe, id=item_id)
        else:
            items = Item.objects(cafe=cafe)
        items = list(filter_non_available_items(items))
        responseObject = {
            'status': 'success',
            'data': []
            }
        if items:
            for item in items:
                cafe_object = {
                    "cafe_name":cafe.cafe_name,
                    "item_name": item.item_name,
                    "cafe_opens_at":cafe.cafe_start_time,
                    "cafe_closes_at":cafe.cafe_close_time,
                }
                responseObject['data'].append(cafe_object)
        return make_response(jsonify(responseObject)), 200
    
    @require_logged_in_user
    def post(self, cafe_id=None, user=None, token_response=None, **kwargs):
        post_data = request.get_json()
        cafe = Cafeteria.objects(id=cafe_id).get()
        item = Item(
            cafe = cafe,
            item_name = post_data.get("name"),
            item_available_hours = post_data.get("item_available_hours")
        )
        item.save()
        responseObject = {
            'status': 'success',
            'data': {
                'cafe_id': cafe.id,
                'cafe_name': cafe.cafe_name,
                'name': item.item_name,
                'item_available_hours':item.item_available_hours,
                "msg":'Item Created Successfully'
            }
        }
        return make_response(jsonify(responseObject)), 201
    
    @require_logged_in_user
    def delete(self, user=None, cafe_id=None, item_id=None, token_response=None, **kwargs):
        item = Item.objects.get(id=item_id, cafe=cafe_id)
        item.delete()
        responseObject = {
            'status': 'success',
            'data': {
                "msg": f"Item {item.name} deleted Successfully"
            }
        }
        return make_response(jsonify(responseObject)), 200

    @require_logged_in_user
    def put(self, user=None, cafe_id=None, item_id=None, token_response=None, **kwargs):
        post_data = request.get_json()
        cafe = Cafeteria.objects.get(id=cafe_id)
        item = Item.objects.get(cafe=cafe, id=item_id)
        item.item_name = post_data.get("name")
        item.item_available_hours = post_data.get("item_available_hours")
        item.save()
        responseObject = {
            'status': 'success',
            'data': {
                'item_id':item.id,
                'cafe_id': cafe.id,
                'cafe_name': cafe.cafe_name,
                'cafe_start_time': cafe.cafe_start_time,
                'cafe_close_time': cafe.cafe_close_time,
                'item_name': item.item_name,
                'item_available_from': item.item_available_hours,
                "msg": f"Item {item.item_name} updated Successfully"
            }
        }
        return make_response(jsonify(responseObject)), 200



# define the API resources
cafeteria_view = CafeteriaAPI.as_view('cafeteria_api')
item_view = ItemAPI.as_view('item_api')

# add Rules for API Endpoints
infra_blueprint.add_url_rule(
    '/user/cafeteria/', 
    defaults={'cafe_id': None},
    view_func=cafeteria_view,
    methods=['GET',]
)
infra_blueprint.add_url_rule(
    '/user/cafeteria/',
    view_func=cafeteria_view,
    methods=['POST',]
)
infra_blueprint.add_url_rule(
    '/user/cafeteria/<int:cafe_id>',
    view_func=cafeteria_view,
    methods=['GET', 'PUT', 'DELETE']
)




infra_blueprint.add_url_rule(
    '/user/cafeteria/<int:cafe_id>/item/', 
    defaults={'item_id': None},
    view_func=item_view,
    methods=['GET',]
)
infra_blueprint.add_url_rule(
    '/user/cafeteria/<int:cafe_id>/item/',
    view_func=item_view,
    methods=['POST',]
)
infra_blueprint.add_url_rule(
    '/user/cafeteria/<int:cafe_id>/item/<int:item_id>',
    view_func=item_view,
    methods=['GET', 'PUT', 'DELETE']
)



