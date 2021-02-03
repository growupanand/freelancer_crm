from freelancer import db, session
from datetime import datetime

class user:

    def __init__(self, _id=None):
        self._id = _id

    def login(self, username, password):
        session['logged_in'] = False
        session['user'] = {}
        self.username = str.strip(username)
        self.password = str.strip(password)
        result = {}
        result['result'] = False
        result['next'] = 'login'
        # validate data
        if None in (self.username, self.password) or '' in (self.username, self.password):
            result['msg'] = 'Username or Password cannot be Empty.'
            return result
        login_user = db.user_collection.find_one({'username': self.username, 'password': self.password})
        if login_user == None:
            result['msg'] = 'Username or Password is wrong.'
            return result
        session['user']['_id'] = str(login_user['_id'])
        if login_user['username'] in ['admin']:
            session['user']['type'] = 'admin'
            result['next'] = 'admin'
        else:
            session['user']['type'] = 'customer'
            result['next'] = 'customer'
        session['logged_in'] = True
        result['msg'] = 'Login Success.'
        result['result'] = True
        return result


class Person:

    def __init__(self, _id=None):
        self._id = _id
        if self._id != None:
            self.db_data = db.persons_collection.find_one({'_id': _id})
            self._id = self.db_data['_id']
            self.name = self.db_data['name'] if 'name' in self.db_data else None
            self.numbers = self.db_data['numbers'] if 'numbers' in self.db_data else []
            self.source_type = self.db_data['source_type'] if 'source_type' in self.db_data else None
            self.source_data = self.db_data['source_data'] if 'source_data' in self.db_data else None

    # add new person in database
    def add_person(self, name, numbers, source_type, source_data):
        result = {}
        result['result'] = False
        result['msg'] = 'Something went wrong.'
        name = str.strip(name)
        if name in [None, '']:
            result['msg'] = 'Name cannot be empty.'
            return result
        person = {
            'created': datetime.utcnow(),
            'name': name,
            'numbers': numbers
        }
        insert_person = db.persons_collection.insert_one(person)
        if insert_person.acknowledged:
            result['result'] = True
            result['_id'] = insert_person.inserted_id
        return result

    # get all person list
    def get(self):
        db_data = db.persons_collection.find()
        return db_data

    # find person
    def find(self, query_fields, query_value):
        query_value = str.strip(query_value)
        query = {}
        if len(query_fields)>0:
            query['$or'] = []
            for field in query_fields:
                query['$or'].append(
                    {field: {'$regex': '.*' + query_value + '.*'}}
                )
        db_data = db.persons_collection.find(query)
        return db_data

class Registration:

    def __init__(self, _id=None):
        self._id = _id
        if self._id != None:
            # get registration data from database
            self.db_data = db.motor_registration_collection.find_one({'_id': self._id})
            self.person_id = self.db_data['person_id']
            self.person = Person(self.person_id)
            self.registration_number = self.db_data[
                'registration_number'] if 'registration_number' in self.db_data else None
            self.registration_name = self.db_data['registration_name'] if 'registration_name' in self.db_data else None
            self.company = self.db_data['company'] if 'company' in self.db_data else None
            self.model = self.db_data['model'] if 'model' in self.db_data else None
            self.cc = self.db_data['cc'] if 'cc' in self.db_data else None
            self.mfg = self.db_data['mfg'] if 'mfg' in self.db_data else None
            self.registration_date = self.db_data['registration_date'] if 'registration_date' in self.db_data else None
            self.created = self.db_data['created'] if 'created' in self.db_data else None

class Policy:

    def __init__(self, _id=None):
        self._id = _id
        self.db_data = None
        if self._id != None:
            # get policy data from database
            self.db_data = db.motor_policy_collection.find_one({'_id': self._id})
            if self.db_data != None:
                self.expiry_date = self.db_data['expiry_date']
                self.policy_number = self.db_data['policy_number'] if 'policy_number' in self.db_data else None
                self.policy_type = self.db_data['policy_type'] if 'policy_type' in self.db_data else None
                self.company = self.db_data['company'] if 'company' in self.db_data else None
                self.idv = self.db_data['idv'] if 'idv' in self.db_data else None
                self.ncb = self.db_data['ncb'] if 'ncb' in self.db_data else None
                self.premium = self.db_data['premium'] if 'premium' in self.db_data else None
                self.own_business = self.db_data['own_business'] if 'own_business' in self.db_data else None
                self.o_dap = self.db_data['o_dap'] if 'o_dap' in self.db_data else None
                self.created = self.db_data['created'] if 'created' in self.db_data else None
                self.person_id = self.db_data['person_id'] if 'person_id' in self.db_data else None
                self.person = Person(self.person_id)
                self.registration_id = self.db_data['registration_id'] if 'expiry_date' in self.db_data else None
                self.registration = Registration(self.registration_id)
                self.renewal_id = self.db_data['renewal_id'] if 'renewal_id' in self.db_data else None
                self.renewal_policy = Policy(self.renewal_id)
                self.old_policy = db.motor_policy_collection.find_one({'renewal_id': self._id})

    # get follow up data
    def get_followup_list(self):
        self.followup_list = db.followup_collection.find({'policy_id':self._id})
        return self.followup_list

    # get renewal list
    def get_renewal_list(self, month, year):  # month should 1-12
        # get policy id list of maximum expiry date
        policy_array = []
        q = db.motor_policy_collection.aggregate([
            {'$match': {
                "$and": [
                    {"$expr": {"$eq": [{"$month": "$expiry_date"}, int(month)]}},
                    {"$expr": {"$lt": [{"$year": "$expiry_date"}, int(year) + 1]}}
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
            {'$project': {'_id': 1, 'expiry_date': 1, 'day': 1, 'name': 1, 'policy_status': 1, 'renewal_id': 1}}
        ])
        for i in q:
            i['renewal_id'] = i['renewal_id'] if 'renewal_id' in i else None
            i['renewal_business'] = False
            if not i['renewal_id'] in (None, 'None'):
                renewal_policy = db.motor_policy_collection.find_one({'_id': i['renewal_id']})
                i['renewal_business'] = renewal_policy['own_business'] if 'own_business' in renewal_policy else False
            policy_list.append(i)
        return policy_list
