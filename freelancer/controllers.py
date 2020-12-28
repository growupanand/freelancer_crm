from freelancer import db, session, request, functions
from flask import jsonify
from datetime import datetime
from bson import ObjectId, json_util
from bson.json_util import dumps
from bson.json_util import loads
import json


def submit_query(data):
    query_data = {}
    query_data['name'] = data['query_name']
    query_data['contact'] = data['query_contact']
    query_data['content'] = data['query_content']
    query_data['timestamp'] = datetime.utcnow()
    return db.query_collection.insert_one(query_data)


# login user
def login(username, password):
    session['user'] = None
    session['logged_in'] = False
    result = {}
    result['result'] = False
    result['next'] = 'login'
    # validate data
    password = None if str.strip(password) == '' else str.strip(password)
    if None in (username, password):
        result['msg'] = 'Username or Password cannot be Empty.'
        return result
    q = db.user_collection.find_one({'username': username, 'password': password})
    if q == None:
        result['msg'] = 'Username or Password is wrong.'
        return result
    else:
        session['user'] = {}
        session['user']['username'] = username
        if session['user']['username'] == 'admin':
            session['user']['type'] = 'admin'
        else:
            session['user']['type'] = 'customer'
        session['logged_in'] = True
        result['result'] = True
        result['msg'] = 'Login Success.'
        result['next'] = 'admin'
        return result


# add_person
def add_person(data):
    result = {}
    result['result'] = False
    required_fields = ['name']
    query_data = {}
    empty_field = []
    for field in required_fields:
        query_data[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
        if query_data[field] == None:
            empty_field.append(field)
    if len(empty_field) > 0:
        result['result'] = False
        result['msg'] = 'Fields cannot be empty: ' + ','.join(empty_field)
    else:
        query_data['created'] = datetime.utcnow()
        query_data['numbers'] = []
        for number in data.getlist('number[]'):
            query_data['numbers'].append(number)
        db.persons_collection.insert_one(query_data)
        result['result'] = True
    return result


# find person
def get_person_list(query=None):
    result = {}
    result['result'] = False
    query = str.strip(query)
    mongo_query = {}
    if not query == '' or not query == None:
        mongo_query = {'$or': [
            {'name': {'$regex': '.*' + query + '.*'}},
            {'numbers': {'$regex': '.*' + query + '.*'}}
        ]}
    q = db.persons_collection.find(mongo_query).sort('name',1)
    persons = []
    for i in q:
        i['_id'] = str(i['_id'])
        i['created'] = i['created'].isoformat()
        persons.append(i)
    result['result'] = True
    result['persons'] = persons
    return result


def get_renewal_list(month):  # month should 1-12
    # get policy id list of maximum expiry date
    policy_array = []
    q = db.motor_policy_collection.aggregate([
        {'$match': {"$expr": {"$eq": [{"$month": "$expiry_date"}, int(month)]}}},
        {'$sort': {'expiry_date': -1}},
        {'$group': {
            '_id': "$person_id",
            'expiry_date': {'$first': "$expiry_date"},
            'policy_id': {'$first': '$_id'}
        }}
    ])
    for i in q:
        policy_array.append(i['policy_id'])
    policy_list = []
    q = db.motor_policy_collection.aggregate([
        {'$match': {'_id': {'$in': policy_array}}},
        {'$addFields': {'day': {'$dayOfMonth': '$expiry_date'}}},
        {'$sort': {'day': 1}},
        {'$lookup': {
            'from': "persons",
            'localField': "person_id",
            'foreignField': "_id",
            'as': "person"
        }},
        {'$addFields': {'name': {"$arrayElemAt": ["$person.name", 0]}}},
        {'$project': {'_id': 1, 'expiry_date': 1, 'day': 1, 'name': 1, 'policy_status': 1}}
    ])
    for i in q:
        i['_id'] = str(i['_id'])
        i['expiry_date'] = i['expiry_date'].isoformat()
        policy_list.append(i)
    return policy_list


def view_renewal(_id):
    result = {}
    result['result'] = False
    policy = db.motor_policy_collection.find_one({'_id': ObjectId(_id)})
    if policy == None:
        result['msg'] = 'Policy ID not found.'
        return result
    person = db.persons_collection.find_one({'_id': policy['person_id']})
    if person == None:
        result['msg'] = 'Person ID not found.'
        return result
    registration = db.motor_registration_collection.find_one({'_id': policy['registration_id']})
    if registration == None:
        result['msg'] = 'Registration ID not found.'
        return result
    result['result'] = True
    data = {}
    data['person_id'] = str(person['_id'])
    data['policy_id'] = str(policy['_id'])
    data['registration_id'] = str(registration['_id'])
    data['name'] = person['name']
    data['numbers'] = person['numbers']
    data['policy_number'] = policy['policy_number']
    data['expiry_date'] = policy['expiry_date'].isoformat()
    data['policy_company'] = policy['company']
    data['policy_type'] = policy['policy_type']
    data['idv'] = policy['idv']
    data['ncb'] = policy['ncb']
    data['discount'] = policy['discount']
    data['premium'] = policy['premium']
    data['renewed_policy'] = str(policy['renewal_id'])
    data['registration_number'] = registration['registration_number']
    data['vehicle_company'] = registration['company']
    data['vehicle_model'] = registration['model']
    data['vehicle_cc'] = registration['cc']
    data['vehicle_year'] = registration['mfg']
    data['followup'] = []
    for i in policy['followup']:
        i['created'] = i['created'].isoformat()
        data['followup'].append(i)
    result['data'] = data
    return result


def post_policy_followup(data):
    result = {}
    result['result'] = False
    policy_id = ObjectId(data['policy_id'])
    remark = str.strip(data['remark'])
    policy_status = data['policy_status']
    if policy_status == '':
        result['msg'] = 'Kindly select policy status.'
        return result
    q = db.motor_policy_collection.update_one({'_id': policy_id}, {
        '$push': {
            'followup': {
                'remark': remark,
                'created': datetime.utcnow()
            }
        },
        '$set': {'policy_status': policy_status}
    })
    if q.acknowledged:
        result['result'] = True
    return result


def add_contact_number(_id, data):
    result = {}
    result['result'] = False
    number = str.strip(data)
    if number == '':
        result['msg'] = 'Number cannot be Empty!'
        return result
    q = db.persons_collection.update_one({'_id':ObjectId(_id)}, {
        '$push':{'numbers':number}
    })
    if q.acknowledged:
        result['result'] = True
        result['new_id'] = q.upserted_id
    return result


def add_contact_email(_id, data):
    result = {}
    result['result'] = False
    email = str.strip(data)
    if email == '':
        result['msg'] = 'Email cannot be Empty!'
        return result
    q = db.persons_collection.update_one({'_id':ObjectId(_id)}, {
        '$push':{'emails':email}
    })
    if q.acknowledged:
        result['result'] = True
        result['new_id'] = q.upserted_id
    return result