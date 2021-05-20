from freelancer import db, session
from datetime import datetime
import re


class user:

    def __init__(self, _id=None):
        self._id = self.user_id = _id

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

    # add new person in database
    def add_person(self, name, numbers, source_type=None, source_data=None):
        result = {}
        result['result'] = False
        result['msg'] = 'Something went wrong.'
        name = str.strip(name)
        if name in [None, '']:
            result['msg'] = 'Name cannot be empty.'
            return result
        source_type = None if str.strip(source_type) == '' else str.strip(source_type)
        source_data = None if str.strip(source_data) == '' else str.strip(source_data)
        person = {
            'user_id': self._id,
            'created': datetime.utcnow(),
            'name': name,
            'numbers': numbers,
            'source_type': source_type,
            'source_data': source_data
        }
        insert_person = db.persons_collection.insert_one(person)
        if insert_person.acknowledged:
            result['result'] = True
            result['new_id'] = insert_person.inserted_id
        return result

    # add new motor insurance company
    def add_motor_insurance_company(self, company_name):
        company_name = str.lower(company_name)
        #check if compnay_name already exist
        company_exist = db.motor_insurance_companies_collection.find_one({"user_id":self.user_id, "company_name":company_name})
        if company_exist is not None:
            return {"result" : False, "msg" : "Company already exist."}
        #add compnay name in database
        add_company = db.motor_insurance_companies_collection.insert_one({
            "user_id":self.user_id,
            "company_name" : company_name
        })
        if add_company.acknowledged:
            return {"result":True, "new_id" : add_company.inserted_id}
        else:
            return {"result":False, "msg" : "Something went wrong."}

    # get all motor insurance company list
    def get_motor_insurance_company_list(self):
        company_list = db.motor_insurance_companies_collection.find({"user_id":self.user_id}, {"user_id":0})
        return company_list

    # delete motor insurance company
    def delete_motor_insurance_company(self, company_id):
        # check if company exist
        company_exist = db.motor_insurance_companies_collection.find_one(
            {"user_id": self.user_id, "_id": company_id})
        if company_exist is None:
            return {"result": False, "msg": "Company not exist."}
        # delete company
        delete_company = db.motor_insurance_companies_collection.delete_one({
            "user_id":self.user_id,
            "_id":company_id
        })
        if delete_company.acknowledged:
            return {"result":True}
        else:
            return {"result":False, "msg": "something went wrong."}


class Person:

    def __init__(self, _id=None):
        self._id = _id
        self.db_data = None
        if self._id != None:
            self.db_data = db.persons_collection.find_one({'_id': _id})
            if self.db_data != None:
                self.name = self.db_data['name'] if 'name' in self.db_data else None
                self.numbers = self.db_data['numbers'] if 'numbers' in self.db_data else []
                self.emails = self.db_data['emails'] if 'emails' in self.db_data else []
                self.dob = self.db_data['dob'] if 'dob' in self.db_data else None
                self.source_type = self.db_data['source_type'] if 'source_type' in self.db_data else None
                self.source_data = self.db_data['source_data'] if 'source_data' in self.db_data else None

    # get all person list
    def get(self):
        db_data = db.persons_collection.find()
        return db_data

    # find person
    def find(self, query_fields, query_value):
        query_value = str.strip(query_value)
        query = {}
        if len(query_fields) > 0:
            query['$or'] = []
            for field in query_fields:
                query['$or'].append(
                    {field: {'$regex':query_value, '$options' : 'i'}}
                )
        db_data = db.persons_collection.find(query)
        return db_data

    # update date of birth
    def update_dob(self, dob):
        result = {'result' : False}
        dob = None if str.strip(dob) in (
            None, '') else datetime.strptime(dob, "%Y-%m-%d")
        if db.persons_collection.update_one({'_id': self._id}, {'$set':{'dob' : dob}}).acknowledged:
            result['result'] = True
            result['dob'] = dob
        return result


    # add contact number
    def add_contact_number(self, number):
        result = {}
        result['result'] = False
        number = str.strip(number)
        if number == '':
            result['msg'] = 'Number cannot be Empty!'
            return result
        insert_number = db.persons_collection.update_one({'_id': self._id}, {
            '$push': {'numbers': number}
        })
        if insert_number.acknowledged:
            result['result'] = True
            result['new_id'] = insert_number.upserted_id
        return result

    # remove contact number
    def remove_contact_number(self, number):
        result = {}
        result['result'] = False
        number = str.strip(number)
        if number == '':
            result['msg'] = 'Number cannot be Empty!'
            return result
        delete_number = db.persons_collection.update_one({'_id': self._id}, {
            '$pull': {
                'numbers': number
            }
        })
        if delete_number.acknowledged:
            result['result'] = True
        return result

    # add contact email
    def add_contact_email(self, email):
        result = {}
        result['result'] = False
        email = str.strip(email)
        if email == '':
            result['msg'] = 'Email cannot be Empty!'
            return result
        insert_email = db.persons_collection.update_one({'_id': self._id}, {
            '$push': {'emails': email}
        })
        if insert_email.acknowledged:
            result['result'] = True
            result['new_id'] = insert_email.upserted_id
        return result

    # remove contact email
    def remove_contact_email(self, email):
        result = {}
        result['result'] = False
        email = str.strip(email)
        if email == '':
            result['msg'] = 'Email cannot be Empty!'
            return result
        remove_email = db.persons_collection.update_one({'_id': self._id}, {
            '$pull': {
                'emails': email
            }
        })
        if remove_email.acknowledged:
            result['result'] = True
        return result

    # add vehicle registration
    def add_registration(self, registration_number, registration_name=None, registration_date=None,
                         company=None, model=None, cc=None, fuel=None, mfg=None):
        result = {}
        result['result'] = False
        registration_number = str.strip(registration_number)
        if registration_number == '' or registration_number == None:
            result['msg'] = 'Registration number cannot be empty.'
            return result
        elif not re.match("[a-zA-Z]{2}[0-9]{1,2}[a-zA-Z]{1,3}[0-9]{4}", registration_number):
            result['msg'] = 'Registration number is not valid.'
            return result
        company = None if str.strip(company) == '' else str.strip(company)
        registration_name = None if str.strip(registration_name) == '' else str.strip(registration_name)
        registration_date = None if str.strip(registration_date) in (
            None, '') else datetime.strptime(registration_date, "%Y-%m-%d")
        model = None if str.strip(model) == '' else str.strip(model)
        cc = None if str.strip(cc) == '' else str.strip(cc)
        fuel = None if str.strip(fuel) == '' else str.strip(fuel)
        mfg = None if str.strip(mfg) == '' else str.strip(mfg)
        registration = {
            'created': datetime.utcnow(),
            'person_id': self._id,
            'registration_number': registration_number,
            'registration_name': registration_name,
            'registration_date': registration_date,
            'company': company,
            'model': model,
            'cc': cc,
            'fuel': fuel,
            'mfg': mfg
        }
        insert_registration = db.motor_registration_collection.insert_one(registration)
        if insert_registration.acknowledged:
            result['result'] = True
            result['new_id'] = insert_registration.inserted_id
        return result

    # get all vehicle registration list of this person
    def get_registration_list(self):
        self.registration_list = []
        for registration in db.motor_registration_collection.find({'person_id': self._id}):
            self.registration_list.append(Registration(registration['_id']))
        return self.registration_list

    # delete person
    def delete_person(self):
        result = {}
        result['result'] = False
        result['msg'] = 'Something went wrong.'
        # delete all health policy
        for policy in self.get_health_policy_list():
            policy.delete_policy()
        # delete all vehicle
        for registration in self.get_registration_list():
            registration.delete_registration()
        # delete person data
        delete_person_data = db.persons_collection.delete_one({'_id': self._id})
        if delete_person_data.acknowledged:
            result['result'] = True
        return result

    # add health policy
    def add_health_policy(self, expiry_date, policy_owner=None, policy_number=None, policy_type=None,
                          company=None, idv=None, ncb=None, premium=None, own_business=None):
        result = {}
        result['result'] = False
        result['msg'] = 'Something went wrong.'
        if expiry_date in (None, ''):
            result['msg'] = 'Expiry date cannot be empty.'
            return result
        expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
        policy_owner = None if str.strip(policy_owner) == '' else str.strip(policy_owner)
        policy_number = None if str.strip(policy_number) == '' else str.strip(policy_number)
        policy_type = None if str.strip(policy_type) == '' else str.strip(policy_type)
        company = None if str.strip(company) == '' else str.strip(company)
        idv = None if str.strip(idv) == '' else str.strip(idv)
        ncb = None if str.strip(ncb) == '' else str.strip(ncb)
        premium = None if str.strip(premium) == '' else str.strip(premium)
        policy = {
            'created': datetime.utcnow(),
            'expiry_date': expiry_date,
            'person_id': self._id,
            'policy_owner': policy_owner,
            'policy_number': policy_number,
            'policy_type': policy_type,
            'company': company,
            'idv': idv,
            'ncb': ncb,
            'premium': premium,
            'own_business': own_business,
        }
        insert_policy = db.health_policy_collection.insert_one(policy)
        if insert_policy.acknowledged:
            result['result'] = True
            result['new_id'] = insert_policy.inserted_id
        return result

    # get health policy list
    def get_health_policy_list(self):
        self.health_policy_list = []
        for policy in db.health_policy_collection.find({'person_id': self._id}):
            self.health_policy_list.append(Policy_health(policy['_id']))
        return self.health_policy_list


class Registration:

    def __init__(self, _id=None):
        self._id = _id
        self.db_data = None
        if self._id != None:
            # get registration data from database
            self.db_data = db.motor_registration_collection.find_one({'_id': self._id})
            if self.db_data != None:
                self.person_id = self.db_data['person_id']
                self.person = Person(self.person_id)
                self.registration_number = self.db_data[
                    'registration_number'] if 'registration_number' in self.db_data else None
                self.registration_name = self.db_data[
                    'registration_name'] if 'registration_name' in self.db_data else None
                self.company = self.db_data['company'] if 'company' in self.db_data else None
                self.model = self.db_data['model'] if 'model' in self.db_data else None
                self.cc = self.db_data['cc'] if 'cc' in self.db_data else None
                self.mfg = self.db_data['mfg'] if 'mfg' in self.db_data else None
                self.fuel = self.db_data['fuel'] if 'fuel' in self.db_data else None
                self.registration_date = self.db_data[
                    'registration_date'] if 'registration_date' in self.db_data else None
                self.created = self.db_data['created'] if 'created' in self.db_data else None

    # add motor policy
    def add_motor_policy(self, expiry_date, policy_number=None, policy_type=None,
                         company=None, idv=None, ncb=None, premium=None, own_business=None, o_dap=None):
        result = {}
        result['result'] = False
        result['msg'] = 'Something went wrong.'
        if expiry_date in (None, ''):
            result['msg'] = 'Expiry date cannot be empty.'
            return result
        expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
        policy_number = None if str.strip(policy_number) == '' else str.strip(policy_number)
        policy_type = None if str.strip(policy_type) == '' else str.strip(policy_type)
        company = None if str.strip(company) == '' else str.strip(company)
        idv = None if str.strip(idv) == '' else str.strip(idv)
        ncb = None if str.strip(ncb) == '' else str.strip(ncb)
        premium = None if str.strip(premium) == '' else str.strip(premium)
        policy = {
            'created': datetime.utcnow(),
            'expiry_date': expiry_date,
            'registration_id': self._id,
            'person_id': self.person_id,
            'policy_number': policy_number,
            'policy_type': policy_type,
            'company': company,
            'idv': idv,
            'ncb': ncb,
            'premium': premium,
            'own_business': own_business,
            'o_dap': o_dap
        }
        insert_policy = db.motor_policy_collection.insert_one(policy)
        if insert_policy.acknowledged:
            result['result'] = True
            result['new_id'] = insert_policy.inserted_id
        return result

    # get policy list
    def get_motor_policy_list(self):
        self.motor_policy_list = []
        for policy in db.motor_policy_collection.find({'registration_id': self._id}):
            self.motor_policy_list.append(Policy_motor(policy['_id']))
        return self.motor_policy_list

    # update registration data
    def update_registration(self, registration_number=None, registration_name=None, registration_date=None,
                            company=None, model=None, cc=None, fuel=None, mfg=None):
        result = {}
        result['result'] = False
        registration = {
            'last_updated': datetime.utcnow(),
            'registration_date': registration_date,
        }
        if not registration_number is None:
            registration_number = str.strip(registration_number)
            if registration_number == '':
                result['msg'] = 'Registration number cannot be empty.'
                return result
            elif not re.match("[a-zA-Z]{2}[0-9]{1,2}[a-zA-Z]{1,3}[0-9]{4}", registration_number):
                result['msg'] = 'Registration number is not valid.'
                return result
            else:
                registration['registration_number'] = registration_number
        if not registration_date is None:
            registration['registration_date'] = None if str.strip(registration_date) in (
                None, '') else datetime.strptime(registration_date, "%Y-%m-%d")
        if not registration_name is None:
            registration['registration_name'] = None if str.strip(registration_name) == '' else str.strip(
                registration_name)
        if not company is None:
            registration['company'] = None if str.strip(company) == '' else str.strip(company)
        if not model is None:
            registration['model'] = None if str.strip(model) == '' else str.strip(model)
        if not cc is None:
            registration['cc'] = None if str.strip(cc) == '' else str.strip(cc)
        if not fuel is None:
            registration['fuel'] = None if str.strip(fuel) == '' else str.strip(fuel)
        if not mfg is None:
            registration['mfg'] = None if str.strip(mfg) == '' else str.strip(mfg)
        update_registration = db.motor_registration_collection.update_one({'_id': self._id}, {
            "$set": registration
        })
        if update_registration.acknowledged:
            result['result'] = True
        return result

    # delete vehicle registration
    def delete_registration(self):
        result = {}
        result['result'] = False
        # delete vehcle all policy
        for policy in self.get_motor_policy_list():
            policy.delete_policy()
        delete_registration = db.motor_registration_collection.delete_one({'_id': self._id})
        if delete_registration.acknowledged:
            result['result'] = True
        return result


class Policy_motor:

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
                self.claim_status = self.db_data['claim_status'] if 'claim_status' in self.db_data else None
                self.o_dap = self.db_data['o_dap'] if 'o_dap' in self.db_data else None
                self.created = self.db_data['created'] if 'created' in self.db_data else None
                self.person_id = self.db_data['person_id'] if 'person_id' in self.db_data else None
                self.person = Person(self.person_id)
                self.registration_id = self.db_data['registration_id'] if 'expiry_date' in self.db_data else None
                self.registration = Registration(self.registration_id)
                self.renewal_id = self.db_data['renewal_id'] if 'renewal_id' in self.db_data else None
                self.renewal_policy = Policy_motor(self.renewal_id)
                self.old_policy = db.motor_policy_collection.find_one({'renewal_id': self._id})

    # find motor policy
    def find(self, query, search_filter):
        policy_list = []
        if search_filter == 'policy_number':
            policy_list = db.motor_policy_collection.find({
                'policy_number': {'$regex':'^'+query+'$', '$options' : 'i'}
            })
        elif search_filter == 'reg_number':
            #find registration_id
            registration = db.motor_registration_collection.find_one({
                'registration_number':{'$regex':'^'+query+'$', '$options' : 'i'}
            })
            if registration is not None:
                policy_list = db.motor_policy_collection.find({
                    'registration_id': registration['_id']
                })
        result = []
        for policy in policy_list:
            result.append({
                'policy_id':policy['_id'],
                'name':db.persons_collection.find_one({'_id':policy['person_id']})['name'],
                'policy_number':policy['policy_number'],
                'expiry_date':policy['expiry_date']
            })
        return result

    # get follow up data
    def get_followup_list(self):
        self.followup_list = db.followup_collection.find({'policy_id': self._id})
        return self.followup_list

    # get renewal list
    def get_renewal_list(self, month, year):  # month should 1-12
        # get policy id list of maximum expiry date
        policy_id_list = []
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
            policy_id_list.append(i['policy_id'])
        policy_list = db.motor_policy_collection.aggregate([
            {'$match': {'_id': {'$in': policy_id_list}}},
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
        renewal_list = []
        for policy in policy_list:
            if 'renewal_id' in policy:
                if policy['renewal_id'] not in (None, False):
                    if Policy_motor(policy['renewal_id']).own_business:
                        policy['policy_status'] = 'won'
                    else:
                        policy['policy_status'] = 'lost'
            renewal_list.append(policy)
        return renewal_list

    # post policy followup
    def post_policy_followup(self, remark, status='followup'):
        result = {}
        result['result'] = False
        followup = {
            'policy_id': self._id,
            'person_id': self.person_id,
            'registration_id': self.registration_id,
            'remark': str.strip(remark),
            'created': datetime.utcnow(),
            'policy_type': 'motor',
            'status': status
        }
        insert_followup = db.followup_collection.insert_one(followup)
        self.update_motor_policy(policy_status=status)
        if insert_followup.acknowledged:
            result['result'] = True
            result['new_id'] = insert_followup.inserted_id
        return result

    # update policy data
    def update_motor_policy(self, expiry_date=None, policy_number=None, policy_type=None,
                            company=None, idv=None, ncb=None, premium=None, own_business=None, o_dap=None,
                            renewal_id=None, policy_status=None, lost_reason=None, claim_status=None):
        result = {}
        result['result'] = False
        result['msg'] = 'Something went wrong.'
        policy = {
            'last_updated': datetime.utcnow(),
        }
        if not expiry_date is None:
            if expiry_date == '':
                result['msg'] = 'Expiry date cannot be empty.'
                return result
            else:
                policy['expiry_date'] = datetime.strptime(expiry_date, "%Y-%m-%d")
        if not policy_number is None:
            policy['policy_number'] = None if str.strip(policy_number) == '' else str.strip(policy_number)
        if not policy_type is None:
            policy['policy_type'] = None if str.strip(policy_type) == '' else str.strip(policy_type)
        if not company is None:
            policy['company'] = None if str.strip(company) == '' else str.strip(company)
        if not idv is None:
            policy['idv'] = None if str.strip(idv) == '' else str.strip(idv)
        if not ncb is None:
            policy['ncb'] = None if str.strip(policy_number) == '' else str.strip(ncb)
        if not premium is None:
            policy['premium'] = None if str.strip(premium) == '' else str.strip(premium)
        if not own_business is None:
            policy['own_business'] = own_business
        if not o_dap is None:
            policy['o_dap'] = o_dap
        if not lost_reason is None:
            policy['lost_reason'] = lost_reason
        if not claim_status is None:
            policy['claim_status'] = claim_status
        if not renewal_id is None:
            policy['renewal_id'] = None if str.strip(renewal_id) == '' else renewal_id
        if not policy_status is None:
            policy['policy_status'] = None if str.strip(policy_status) == '' else str.strip(policy_status)
        update_policy = db.motor_policy_collection.update_one({'_id': self._id}, {
            "$set": policy
        })
        if update_policy.acknowledged:
            result['result'] = True
            result['msg'] = 'Policy updated successfully.'
        return result

    # delete policy
    def delete_policy(self):
        result = {}
        result['result'] = False
        # delete renewal id in old policy
        if self.old_policy != None:
            old_policy = Policy_motor(self.old_policy['_id'])
            old_policy.update_motor_policy(renewal_id='', policy_status='')
        # delete followup of this policy
        db.followup_collection.delete_many({'policy_id': self._id})
        delete_policy = db.motor_policy_collection.delete_one({'_id': self._id})
        if delete_policy.acknowledged:
            result['result'] = True
        return result


class Policy_health:

    def __init__(self, _id=None):
        self._id = _id
        self.db_data = None
        if self._id != None:
            # get policy data from database
            self.db_data = db.health_policy_collection.find_one({'_id': self._id})
            if self.db_data != None:
                self.expiry_date = self.db_data['expiry_date']
                self.policy_owner = self.db_data['policy_owner'] if 'policy_owner' in self.db_data else None
                self.policy_number = self.db_data['policy_number'] if 'policy_number' in self.db_data else None
                self.policy_type = self.db_data['policy_type'] if 'policy_type' in self.db_data else None
                self.company = self.db_data['company'] if 'company' in self.db_data else None
                self.idv = self.db_data['idv'] if 'idv' in self.db_data else None
                self.ncb = self.db_data['ncb'] if 'ncb' in self.db_data else None
                self.premium = self.db_data['premium'] if 'premium' in self.db_data else None
                self.claim_status = self.db_data['claim_status'] if 'claim_status' in self.db_data else None
                self.own_business = self.db_data['own_business'] if 'own_business' in self.db_data else None
                self.created = self.db_data['created'] if 'created' in self.db_data else None
                self.person_id = self.db_data['person_id'] if 'person_id' in self.db_data else None
                self.person = Person(self.person_id)
                self.renewal_id = self.db_data['renewal_id'] if 'renewal_id' in self.db_data else None
                self.renewal_policy = Policy_health(self.renewal_id)
                self.old_policy = db.health_policy_collection.find_one({'renewal_id': self._id})

    # get follow up data
    def get_followup_list(self):
        self.followup_list = db.followup_collection.find({'policy_id': self._id})
        return self.followup_list

    # get renewal list
    def get_renewal_list(self, month, year):  # month should 1-12
        # get policy id list of maximum expiry date
        policy_id_list = []
        q = db.health_policy_collection.aggregate([
            {'$match': {
                "$and": [
                    {"$expr": {"$eq": [{"$month": "$expiry_date"}, int(month)]}},
                    {"$expr": {"$lt": [{"$year": "$expiry_date"}, int(year) + 1]}}
                ]}},
            {'$sort': {'expiry_date': -1}},
            {'$group': {
                '_id': "person_id",
                'expiry_date': {'$first': "$expiry_date"},
                'policy_id': {'$first': '$_id'}
            }}
        ])
        for i in q:
            policy_id_list.append(i['policy_id'])
        policy_list = db.health_policy_collection.aggregate([
            {'$match': {'_id': {'$in': policy_id_list}}},
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
        renewal_list = []
        for policy in policy_list:
            if 'renewal_id' in policy:
                if policy['renewal_id'] != None:
                    if Policy_health(policy['renewal_id']).own_business:
                        policy['policy_status'] = 'won'
                    else:
                        policy['policy_status'] = 'lost'
            renewal_list.append(policy)
        return renewal_list

    # post policy followup
    def post_policy_followup(self, remark, status='followup'):
        result = {}
        result['result'] = False
        followup = {
            'policy_id': self._id,
            'person_id': self.person_id,
            'remark': str.strip(remark),
            'created': datetime.utcnow(),
            'policy_type': 'health',
            'status': status
        }
        insert_followup = db.followup_collection.insert_one(followup)
        self.update_health_policy(policy_status=status)
        if insert_followup.acknowledged:
            result['result'] = True
            result['new_id'] = insert_followup.inserted_id
        return result

    # update policy data
    def update_health_policy(self, expiry_date=None, policy_owner=None, policy_number=None, policy_type=None,
                             company=None, idv=None, ncb=None, premium=None, own_business=None,
                             renewal_id=None, policy_status=None, claim_status=None):
        result = {}
        result['result'] = False
        result['msg'] = 'Something went wrong.'
        policy = {
            'last_updated': datetime.utcnow(),
        }
        if not expiry_date is None:
            if expiry_date == '':
                result['msg'] = 'Expiry date cannot be empty.'
                return result
            else:
                policy['expiry_date'] = datetime.strptime(expiry_date, "%Y-%m-%d")
        if not policy_owner is None:
            policy['policy_owner'] = None if str.strip(policy_owner) == '' else str.strip(policy_owner)
        if not policy_number is None:
            policy['policy_number'] = None if str.strip(policy_number) == '' else str.strip(policy_number)
        if not policy_type is None:
            policy['policy_type'] = None if str.strip(policy_type) == '' else str.strip(policy_type)
        if not company is None:
            policy['company'] = None if str.strip(company) == '' else str.strip(company)
        if not idv is None:
            policy['idv'] = None if str.strip(idv) == '' else str.strip(idv)
        if not ncb is None:
            policy['ncb'] = None if str.strip(policy_number) == '' else str.strip(ncb)
        if not premium is None:
            policy['premium'] = None if str.strip(premium) == '' else str.strip(premium)
        if not own_business is None:
            policy['own_business'] = own_business
        if not claim_status is None:
            policy['claim_status'] = claim_status
        if not renewal_id is None:
            policy['renewal_id'] = None if str.strip(renewal_id) == '' else renewal_id
        if not policy_status is None:
            policy['policy_status'] = None if str.strip(policy_status) == '' else str.strip(policy_status)
        update_policy = db.health_policy_collection.update_one({'_id': self._id}, {
            "$set": policy
        })
        if update_policy.acknowledged:
            result['result'] = True
        return result

    # delete policy
    def delete_policy(self):
        result = {}
        result['result'] = False
        # delete renewal id in old policy
        if self.old_policy != None:
            old_policy = Policy_health(self.old_policy['_id'])
            old_policy.update_health_policy(renewal_id='', policy_status='')
        # delete followup of this policy
        db.followup_collection.delete_many({'policy_id': self._id})
        delete_policy = db.health_policy_collection.delete_one({'_id': self._id})
        if delete_policy.acknowledged:
            result['result'] = True
        return result


class Lead:

    def __init__(self, _id=None):
        self._id = _id

    def create_policy_lead(self, policy_type, source, name, expiry_date, contact_detail):
        create_lead = db.lead_collection.insert_one({
            'created': datetime.utcnow(),
            'type': 'insurance',
            'policy_type': policy_type,
            'source': source,
            'name': name,
            'expiry_date': expiry_date,
            'contact_detail': contact_detail
        })
        if create_lead.acknowledged:
            result = {'result': True, 'msg': 'Success', 'new_id': create_lead.inserted_id}
        else:
            result = {'result': False, 'msg': 'Lead not created for some reason.'}
        return result


class vehicle:

    def __init__(self, _id=None):
        self._id = _id
        # get vehicle models list automaticaly if vehicle_id is given
        if not self._id == None:
            self.db_data = db.vehicle_collection.find_one({'_id': self._id})
            self.models = self.db_data['models'] if 'models' in self.db_data else []

    # add vehicle company
    def add_vehicle_company(self, user_id, company_name):
        result = {
            'result': False,
            'msg': 'Something went wrong'
        }
        if company_name in ('', None):
            return result
        # check if vehicle company is not already exist in db
        if not db.vehicle_collection.find({'company_name': company_name}).count() > 0:
            # if not exist insert company
            add_vehicle_company = db.vehicle_collection.insert_one({
                'user_id': user_id,
                'company_name': company_name
            })
            if add_vehicle_company.acknowledged:
                result = {
                    'result': True,
                    'new_id': add_vehicle_company.inserted_id,
                    'msg': 'successfully added vehicle company.'
                }
        else:
            result['msg'] = 'Company already exist.'
        return result

    # get vehicle company list
    def get_vehicle_list(self, user_id=None):
        result = []
        query = {}
        if not user_id == None:
            query['user_id'] = user_id
        for vehicle in db.vehicle_collection.find(query).sort('company_name', 1):
            result.append(vehicle)
        return result

    # add vehicle company
    def add_vehicle_model(self, user_id, company_id, model_name):
        result = {
            'result': False,
            'msg': 'Something went wrong'
        }
        if model_name in ('', None) or company_id in ('', None):
            return result
        model_exist = False
        vehicle = db.vehicle_collection.find_one({'user_id': user_id, '_id': company_id})
        if 'models' in vehicle:
            for model in vehicle['models']:
                if model['name'] == model_name:
                    model_exist = True
        if not model_exist:
            add_vehicle_model = db.vehicle_collection.update_one(
                {
                    'user_id': user_id,
                    '_id': company_id
                },
                {
                    '$push': {
                        'models': {
                            'name': model_name
                        }
                    }
                })
            if add_vehicle_model.acknowledged:
                result = {
                    'result': True,
                    'msg': 'successfully added vehicle model.'
                }
        else:
            result['msg'] = 'Model already exist.'
        return result

    # get vehicle model list
    def get_vehicle_model_list(self, company_name):
        result = []
        vehicle = db.vehicle_collection.find_one({'company_name': company_name})
        if 'models' in vehicle:
            for model in vehicle['models']:
                result.append(model)
        return result

    # delete vehicle model
    def delete_vehicle_model(self, company_id, model_name):
        result = {
            'result': False,
            'msg': 'Something went wrong'
        }
        delete_model = db.vehicle_collection.update_one({'_id': company_id}, {
            '$pull': {
                'models': {'name': model_name}
            }})

        if delete_model.acknowledged:
            result['result'] = True
            result['msg'] = 'Successfully deleted model.'
        return  result

    # delete vehicle company
    def delete_vehicle_company(self, company_id):
        result = {
            'result': False,
            'msg': 'Something went wrong'
        }
        delete_company = db.vehicle_collection.delete_one({'_id': company_id})
        if delete_company.acknowledged:
            result['result'] = True
            result['msg'] = 'Successfully deleted company.'
        return result