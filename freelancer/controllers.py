from freelancer import db, session, models
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



def post_policy_followup(data):
    result = {}
    result['result'] = False
    policy_status = data['policy_status']
    policy_id = ObjectId(data['policy_id'])
    policy_data = db.motor_policy_collection.find_one({'_id': policy_id})
    new_data = {
        'policy_id': policy_data['_id'],
        'person_id': policy_data['person_id'],
        'registration_id': policy_data['registration_id'],
        'remark': str.strip(data['remark']),
        'created': datetime.utcnow(),
        'policy_type': 'motor'
    }
    if policy_status == '':
        result['msg'] = 'Kindly select policy status.'
        return result
    q = db.followup_collection.insert_one(new_data)
    if q.acknowledged:
        result['result'] = True
        result['new_id'] = str(q.inserted_id)
        db.motor_policy_collection.update_one({'_id': policy_id}, {
            '$set': {'policy_status': policy_status}
        })
    return result


def add_contact_number(person_id, data):
    result = {}
    result['result'] = False
    number = str.strip(data)
    if number == '':
        result['msg'] = 'Number cannot be Empty!'
        return result
    q = db.persons_collection.update_one({'_id': ObjectId(person_id)}, {
        '$push': {'numbers': number}
    })
    if q.acknowledged:
        result['result'] = True
        result['new_id'] = q.upserted_id
    return result


def remove_contact_number(person_id, number):
    result = {}
    result['result'] = False
    q = db.persons_collection.update_one({'_id': ObjectId(person_id)}, {
        '$pull': {
            'numbers': number
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
    q = db.persons_collection.update_one({'_id': ObjectId(person_id)}, {
        '$push': {'emails': email}
    })
    if q.acknowledged:
        result['result'] = True
        result['new_id'] = q.upserted_id
    return result


def remove_email(person_id, email):
    result = {}
    result['result'] = False
    q = db.persons_collection.update_one({'_id': ObjectId(person_id)}, {
        '$pull': {
            'emails': email
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
    result['msg'] = 'Something went wrong.'
    person_id = ObjectId(person_id)
    # delete all vehicle
    for vehicle in db.motor_registration_collection.find({'person_id': person_id}):
        delete_vehicle(vehicle['_id'])
    # delete person data
    delete_person_data = db.persons_collection.delete_one({'_id': person_id})
    if delete_person_data.acknowledged:
        result['result'] = True
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
    elif not re.match("[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{1,2}[0-9]{4}", query_data['registration_number']):
        result['msg'] = 'Registration number is not valid.'
        return result
    else:
        for field in ['registration_name', 'company', 'model', 'cc', 'fuel', 'mfg']:
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


def view_vehicle(registration_id):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    # check registration id is valid
    registration_id = str.strip(str(registration_id))
    if registration_id == '':
        result['msg'] = 'Registration id cannot be empty.'
        return result
    q = db.motor_registration_collection.find_one({'_id': ObjectId(registration_id)}, {'created': 0})
    if q:
        result['result'] = True
        q['_id'] = str(q['_id'])
        q['registration_id'] = q['_id']
        q['person_id'] = str(q['person_id'])
        if not q['registration_date'] == None:
            q['registration_date'] = q['registration_date'].isoformat()
        if 'created' in q:
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
    registration_id = ObjectId(registration_id)
    vehicle = db.motor_registration_collection.find_one({'_id': registration_id})
    # delete vehcle all policy
    for policy in db.motor_policy_collection.find({'registration_id': registration_id}):
        delete_policy = delete_vehicle_policy(policy['_id'])
    delete_registration = db.motor_registration_collection.delete_one({'_id': registration_id})
    if delete_registration.acknowledged:
        result['result'] = True
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
    if not re.match("[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{1,2}[0-9]{4}", query_data['registration_number']):
        result['msg'] = 'Registration number is not valid.'
        return result
    for field in ['registration_name', 'company', 'model', 'cc', 'fuel', 'mfg']:
        query_data[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
    d = str.strip(str(data['registration_date']))
    query_data['registration_date'] = None if d == '' else datetime.strptime(d, "%Y-%m-%d")
    query_data['last_updated'] = datetime.utcnow()
    q = db.motor_registration_collection.update_one({'_id': ObjectId(_id)}, {
        "$set": query_data
    })
    if q.acknowledged:
        result['result'] = True
    return result


def add_motor_policy(data):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    required_fields = ['registration_number', 'expiry_date', 'registration_id']
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
        for i in ('own_business', 'o_dap'):
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
    return result


def view_vehicle_policy(policy_id):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    q = db.motor_policy_collection.find_one({'_id': ObjectId(policy_id)}, {'followup': 0, 'renewal_id': 0})
    if q:
        result['result'] = True
        q['_id'] = str(q['_id'])
        q['registration_id'] = str(q['registration_id'])
        q['person_id'] = str(q['person_id'])
        if not q['expiry_date'] == None:
            q['expiry_date'] = q['expiry_date'].isoformat()
        if 'created' in q:
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
    policy_id = ObjectId(policy_id)
    # delete renewal id in old policy
    old_policy = db.motor_policy_collection.find_one({'renewal_id': policy_id})
    if old_policy:
        delete_renewal_id = db.motor_policy_collection.update_one(
            {'_id': old_policy['_id']},
            {"$set": {"renewal_id": None, "policy_status": None}}
        )
    # delete followup of this policy
    delete_followup = db.followup_collection.delete_many({'policy_id': policy_id})
    delete_policy = db.motor_policy_collection.delete_one({'_id': ObjectId(policy_id)})
    if delete_policy.acknowledged:
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
        query_data[field] = None if not field in data or str.strip(data[field]) == '' else str.strip(data[field])
    query_data['own_business'] = True if 'own_business' in data else False
    query_data['o_dap'] = True if 'o_dap' in data else False
    d = str.strip(str(data['expiry_date']))
    query_data['expiry_date'] = None if d == '' else datetime.strptime(d, "%Y-%m-%d")
    query_data['last_updated'] = datetime.utcnow()
    q = db.motor_policy_collection.update_one({'_id': ObjectId(_id)}, {
        "$set": query_data
    })

    if q.acknowledged:
        result['result'] = True
    return result


def add_renewal_motor_policy(data):
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    old_policy_id = ObjectId(data['policy_id'])
    remark = data['remark']
    expiry_date = data['expiry_date']
    old_policy = db.motor_policy_collection.find_one({'_id': old_policy_id})
    if not old_policy:
        result['msg'] = 'Old policy not found.'
        return result
    new_policy = {
        'person_id': old_policy['person_id'],
        'registration_id': old_policy['registration_id']
    }
    if expiry_date in ['None', None, '']:
        result['msg'] = 'Expiry date is invalid.'
        return result
    d = str.strip(str(expiry_date))
    new_policy['expiry_date'] = datetime.strptime(d, "%Y-%m-%d")
    for field in ['policy_number', 'policy_type', 'company', 'idv', 'ncb', 'premium']:
        new_policy[field] = None if str.strip(data[field]) == '' else str.strip(data[field])
    for i in ('own_business', 'o_dap'):
        new_policy[i] = True if i in data else False
    new_policy['created'] = datetime.utcnow()
    insert_new_policy = db.motor_policy_collection.insert_one(new_policy)
    if insert_new_policy.acknowledged:
        result['result'] = True
        new_policy['_id'] = insert_new_policy.inserted_id
        result['new_id'] = str(new_policy['_id'])
        # add new policy id, policy status in old policy data
        db.motor_policy_collection.update_one({'_id': old_policy_id}, {
            '$set': {'policy_status': 'renewed', 'renewal_id': new_policy['_id']}
        })
        # add followup
        followup = {
            'remark': 'Policy renewed!\n' + str.strip(data['remark']),
            'created': datetime.utcnow(),
            'policy_id': old_policy['_id'],
            'person_id': new_policy['person_id'],
            'registration_id': new_policy['registration_id'],
            'policy_type': 'motor'
        }
        db.followup_collection.insert_one(followup)
    return result
