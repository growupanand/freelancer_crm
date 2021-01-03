from freelancer import db, session
from datetime import datetime
from bson import ObjectId
import re

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
        q = db.persons_collection.insert_one(query_data)
        if q.acknowledged:
            result['result'] = True
            result['new_id'] = str(q.inserted_id)
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


def get_renewal_list(month, year):  # month should 1-12
    # get policy id list of maximum expiry date
    policy_array = []
    q = db.motor_policy_collection.aggregate([
        {'$match':{
             "$and":[
                 {"$expr": {"$eq": [{"$month": "$expiry_date"}, int(month)]}},
                 {"$expr": {"$lt": [{"$year": "$expiry_date"}, int(year)+1 ]}}
             ]}},
        {'$sort': {'expiry_date': -1}},
        {'$group': {
            '_id': "$registration_id",
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
    data['0_dap'] = policy['0_dap']
    data['own_business'] = policy['own_business']
    data['idv'] = policy['idv']
    data['ncb'] = policy['ncb']
    data['premium'] = policy['premium']
    data['policy_status'] = policy['policy_status'] if 'policy_status' in policy else None
    data['renewal_id'] = str(policy['renewal_id']) if 'renewal_id' in policy else None
    data['registration_number'] = registration['registration_number']
    data['vehicle_company'] = registration['company']
    data['vehicle_model'] = registration['model']
    data['vehicle_cc'] = registration['cc']
    data['vehicle_mfg_year'] = registration['mfg']
    data['followup'] = []
    if 'followup' in policy:
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


def add_contact_number(person_id, data):
    result = {}
    result['result'] = False
    number = str.strip(data)
    if number == '':
        result['msg'] = 'Number cannot be Empty!'
        return result
    q = db.persons_collection.update_one({'_id':ObjectId(person_id)}, {
        '$push':{'numbers':number}
    })
    if q.acknowledged:
        result['result'] = True
        result['new_id'] = q.upserted_id
    return result


def remove_contact_number(person_id, number):
    result = {}
    result['result'] = False
    q = db.persons_collection.update_one({'_id':ObjectId(person_id)}, {
        '$pull':{
            'numbers':number
        }
    })
    if q.acknowledged:
        result['result'] = True
    else:
        result['msg'] = 'Something went wrong.'
    return result


def add_contact_email(person_id, data):
    result = {}
    result['result'] = False
    email = str.strip(data)
    if email == '':
        result['msg'] = 'Email cannot be Empty!'
        return result
    q = db.persons_collection.update_one({'_id':ObjectId(person_id)}, {
        '$push':{'emails':email}
    })
    if q.acknowledged:
        result['result'] = True
        result['new_id'] = q.upserted_id
    return result


def remove_email(person_id, email):
    result = {}
    result['result'] = False
    q = db.persons_collection.update_one({'_id':ObjectId(person_id)}, {
        '$pull':{
            'emails':email
        }
    })
    if q.acknowledged:
        result['result'] = True
    else:
        result['msg'] = 'Something went wrong.'
    return result


def delete_person(person_id):
    result = {}
    result['result'] = False
    registration_list = []
    for i in  db.motor_registration_collection.find({'person_id':ObjectId(person_id)}, {'_id':1}):
        registration_list.append(i['_id'])
    q = db.persons_collection.delete_one({'_id':ObjectId(person_id)})
    if q.acknowledged:
        result['result'] = True
        for i in registration_list:
            delete_vehicle(i)
    else:
        result['msg'] = 'Something went wrong.'
    return result



def add_vehicle(data):
    result = {}
    result['result'] = False
    required_fields = ['registration_number']
    query_data = {}
    empty_field = []
    for field in required_fields:
        query_data[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
        if query_data[field] == None:
            empty_field.append(field)
    if len(empty_field) > 0:
        result['result'] = False
        result['msg'] = 'Fields cannot be empty: ' + ','.join(empty_field)
    elif not re.match("[a-z]{2}[0-9]{2}[a-z]{2}[0-9]{4}", query_data['registration_number']):
        result['msg'] = 'Registration number is not valid.'
        return result
    else:
        for field in ['registration_name', 'company', 'model', 'cc', 'mfg']:
            query_data[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
        d = str.strip(str(data['registration_date']))
        query_data['registration_date'] = None if d == '' else datetime.strptime(d, "%Y-%m-%d")
        query_data['created'] = datetime.utcnow()
        query_data['person_id'] = ObjectId(data['person_id'])
        q = db.motor_registration_collection.insert_one(query_data)
        if q.acknowledged:
            result['result'] = True
            result['new_id'] = str(q.inserted_id)
        else:
            result['msg'] = 'Something went wrong.'
    return result


def view_vehicle(registration_number):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    #check registration number is valid
    registration_number = str.strip(str(registration_number))
    if registration_number == '':
        result['msg'] = 'Registration number cannot be empty.'
        return result
    q = db.motor_registration_collection.find_one({'registration_number': registration_number})
    if q:
        result['result'] = True
        q['_id'] = str(q['_id'])
        q['registration_id'] = q['_id']
        q['person_id'] = str(q['person_id'])
        if not q['registration_date'] == None:
            q['registration_date'] = q['registration_date'].isoformat()
        q['created'] = q['created'].isoformat()
        if 'last_updated' in q:
            q['last_updated'] = q['last_updated'].isoformat()
        result['data'] = q
    else:
        result['msg'] = 'No vehicle found of this registration number.'
    return result


def delete_vehicle(registration_id):
    result = {}
    result['result'] = False
    q = db.motor_registration_collection.delete_one({'_id':ObjectId(registration_id)})
    if q.acknowledged:
        result['result'] = True
        db.motor_policy_collection.delete_many({'registration_id':ObjectId(registration_id)})
    else:
        result['msg'] = 'Something went wrong.'
    return result


def update_vehicle(data):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    query_data = {}
    _id = data['registration_id']
    query_data['registration_number'] = str(str.strip(data['registration_number']))
    if not re.match("[a-z]{2}[0-9]{2}[a-z]{2}[0-9]{4}", query_data['registration_number']):
        result['msg'] = 'Registration number is not valid.'
        return result
    for field in ['registration_name', 'company', 'model', 'cc', 'mfg']:
        query_data[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
    d = str.strip(str(data['registration_date']))
    query_data['registration_date'] = None if d == '' else datetime.strptime(d, "%Y-%m-%d")
    query_data['last_updated'] = datetime.utcnow()
    q = db.motor_registration_collection.update_one({'_id':ObjectId(_id)}, {
        "$set" : query_data
    })
    if q.acknowledged:
        result['result'] = True
    return result


def add_motor_policy(data):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    required_fields = ['registration_number', 'expiry_date']
    query_data = {}
    empty_field = []
    for field in required_fields:
        if data[field] == None or data[field] == '':
            empty_field.append(field)
    if len(empty_field) > 0:
        result['result'] = False
        result['msg'] = 'Fields cannot be empty: ' + ','.join(empty_field)
        return result
    else:
        d = str.strip(str(data['expiry_date']))
        query_data['expiry_date'] = None if d == '' else datetime.strptime(d, "%Y-%m-%d")
        for field in ['registration_number', 'policy_number', 'policy_type', 'company', 'idv', 'ncb', 'premium']:
            query_data[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
        for i in ('own_business', '0_dap'):
            if i in data:
                query_data[i] = True
            else:
                query_data[i] = False
        query_data['created'] = datetime.utcnow()
        query_data['person_id'] = ObjectId(data['person_id'])
        query_data['registration_id'] = db.motor_registration_collection.find_one(
            {'registration_number':data['registration_number']}, {'_id':1})['_id']
        q = db.motor_policy_collection.insert_one(query_data)
        if q.acknowledged:
            result['result'] = True
            result['new_id'] = str(q.inserted_id)
    return result


def view_vehicle_policy(policy_id):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    q = db.motor_policy_collection.find_one({'_id': ObjectId(policy_id)})
    if q:
        result['result'] = True
        q['_id'] = str(q['_id'])
        q['registration_id'] = str(q['registration_id'])
        q['person_id'] = str(q['person_id'])
        if not q['expiry_date'] == None:
            q['expiry_date'] = q['expiry_date'].isoformat()
        q['created'] = q['created'].isoformat()
        if 'last_updated' in q:
            q['last_updated'] = q['last_updated'].isoformat()
        result['data'] = q
    else:
        result['msg'] = 'No policy found.'
    return result


def delete_vehicle_policy(policy_id):
    result = {}
    result['result'] = False
    q = db.motor_policy_collection.delete_one({'_id':ObjectId(policy_id)})
    if q.acknowledged:
        result['result'] = True
    else:
        result['msg'] = 'Something went wrong.'
    return result


def update_vehicle_policy(data):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    query_data = {}
    _id = data['policy_id']
    for field in ['policy_number', 'policy_type', 'company', 'idv', 'ncb', 'premium']:
        query_data[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
    query_data['own_business'] = True if 'own_business' in data else False
    query_data['0_dap'] = True if '0_dap' in data else False
    d = str.strip(str(data['expiry_date']))
    query_data['expiry_date'] = None if d == '' else datetime.strptime(d, "%Y-%m-%d")
    query_data['last_updated'] = datetime.utcnow()
    q = db.motor_policy_collection.update_one({'_id':ObjectId(_id)}, {
        "$set" : query_data
    })
    if q.acknowledged:
        result['result'] = True
    return result


def add_renewal_motor_policy(data):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    required_fields = ['policy_id', 'expiry_date']
    query_data = {}
    empty_field = []
    for field in required_fields:

        if data[field] == None or data[field] == '':
            empty_field.append(field)
    if len(empty_field) > 0:
        result['result'] = False
        result['msg'] = 'Fields cannot be empty: ' + ','.join(empty_field)
        return result
    else:
        d = str.strip(str(data['expiry_date']))
        query_data['expiry_date'] = datetime.strptime(d, "%Y-%m-%d")
        for field in ['policy_number', 'policy_type', 'company', 'idv', 'ncb', 'premium']:
            query_data[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
        for i in ('own_business', '0_dap'):
            if i in data:
                query_data[i] = True
            else:
                query_data[i] = False
        query_data['created'] = datetime.utcnow()
        query_data['person_id'] = ObjectId(data['person_id'])
        query_data['registration_id'] = ObjectId(data['registration_id'])
        q = db.motor_policy_collection.insert_one(query_data)
        if q.acknowledged:
            result['result'] = True
            result['new_id'] = str(q.inserted_id)
            remark = str.strip(data['remark'])
            policy_status = data['policy_status']
            db.motor_policy_collection.update_one({'_id': ObjectId(data['policy_id'])}, {
                '$push': {
                    'followup': {
                        'remark': remark,
                        'created': datetime.utcnow()
                    }
                },
                '$set': {'policy_status': policy_status, 'renewal_id': ObjectId(result['new_id'])}
            })

    return result
