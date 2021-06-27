from flask import session
from freelancer import db
import bcrypt
import re
import datetime


class User:

    def __init__(self, _id=None):
        self._id = _id
        # create contact class without contact id in user class
        self.contact = Contact()
        self.contact.user_id = self._id
        self.contact.vehicle = Vehicle()
        self.contact.vehicle.user_id = self._id
        self.contact.vehicle.policy = Policy()
        self.contact.vehicle.policy.user_id = self._id

    # create contact class with contact id in user class
    def Contact(self, _id):
        # check if user id is set
        if self._id is None:
            raise Exception('user _id not set!')
        self.contact = Contact(_id)
        self.contact.user_id = self._id
        self.contact.vehicle = Vehicle()
        self.contact.vehicle.user_id = self._id
        self.contact.vehicle.contact_id = _id
        self.contact.vehicle.policy = Policy()
        self.contact.vehicle.policy.policy_type = 'motor'
        self.contact.vehicle.policy.user_id = self._id

    def create_user(self, username, password, full_name):
        user = {
            'created': datetime.datetime.utcnow(),
            'username': str(username).strip().lower(),
            'password': str(password).strip(),
            'full_name': str(full_name).strip().lower(),
            'role': 'agent'
        }
        # validate data
        is_valid = True
        invalid_fields = {}
        # check required fields are not empty
        for field in ('username', 'password', 'full_name'):
            if user[field] == '':
                is_valid = False
                invalid_fields[field] = 'Cannot be empty!'
        if not is_valid:
            return {
                'result': False,
                'msg': 'Check fields:\n' + ', '.join(invalid_fields),
                'invalid_fields': invalid_fields
            }
        # check if username already exist
        username_exist = db.users_collection.find_one({'username': user['username']})
        if username_exist is not None:
            return {
                'result': False,
                'msg': 'username already exist!',
                'invalid_fields': {'username': 'change username'}
            }
        # create user
        # hash password
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user['password'] = hashed_password
        create = db.users_collection.insert_one(user)
        # if create user successfull
        if create.acknowledged:
            return {
                'result': True
            }
        # else send error
        return {
            'result': False,
            'msg': 'Database error'
        }

    def login(self, username, password):
        session.clear()
        username = str(username).strip().lower()
        password = str(password).strip()
        # validate data
        if '' in ('username', 'password'):
            return {
                'result': False,
                'msg': 'username or password cannot be empty!'
            }
        # check if username is exist
        user_exist = db.users_collection.find_one({'username': username})
        if user_exist is not None:
            # check if password match
            password_match = bcrypt.checkpw(str.encode(password), user_exist['password'])
            if password_match:
                # set login in session
                session['logged_in'] = True
                session['user'] = {
                    '_id': str(user_exist['_id']),
                    'username': user_exist['username'],
                    'full_name': user_exist['full_name'],
                    'role': user_exist['role']
                }
                return {
                    'result': True,
                    'msg': 'login successfully!'
                }
            # if user not exist or password not match
        return {
            'result': False,
            'msg': 'username or password is wrong!'
        }

    def logout(self):
        session.clear()
        return {'result': True}


class Contact:

    def __init__(self, _id=None):
        self._id = _id
        # create vehicle class without vehicle id in contact class
        self.vehicle = Vehicle()
        if self._id is not None:
            self.vehicle.contact_id = self._id

    # create vehicle class with vehicle id in contact class
    def Vehicle(self, _id):
        self.vehicle = Vehicle(_id)
        self.vehicle.contact_id = self._id
        self.vehicle.user_id = self.user_id
        self.vehicle.policy = Policy()
        self.vehicle.policy.policy_type = 'motor'
        self.vehicle.policy.user_id = self.user_id
        self.vehicle.policy.contact_id = self._id
        self.vehicle.policy.vehicle_id = _id

    def create_contact(self, source_type, source_name, full_name, mobile_number, email):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        result = {'result': False, 'msg': 'something went wrong!'}
        contact = {
            'created': datetime.datetime.utcnow(),
            'user_id': self.user_id,
            'source_type': str(source_type).strip().lower(),
            'source_name': str(source_name).strip().lower(),
            'full_name': str(full_name).strip().lower(),
            'mobile_number': str(mobile_number).strip().lower(),
            'email': str(email).strip().lower()
        }
        # validate data
        is_valid = True
        invalid_fields = {}
        for field in ('source_type', 'source_name', 'full_name', 'mobile_number'):
            # check for empty fields
            if contact[field] == '':
                is_valid = False
                invalid_fields[field] = 'Cannot be empty!'
        if 'mobile_number' not in invalid_fields:
            # check if mobile number is 10 digit
            if not re.match('[0-9]{10}', contact['mobile_number']):
                is_valid = False
                invalid_fields['mobile_number'] = 'Mobile Number should be 10 digit!'
        # if all required fields are valid create contact in database
        if not is_valid:
            return {
                'result': False,
                'msg': 'Check fields:\n' + ', '.join(invalid_fields),
                'invalid_fields': invalid_fields
            }
        # convert mobile number to array
        contact['mobile_numbers'] = []
        contact['mobile_numbers'].append(contact['mobile_number'])
        contact.pop('mobile_number')
        create = db.contacts_collection.insert_one(contact)
        if create.acknowledged:
            result = {
                'result': True,
                '_id': create.inserted_id,
                'msg': 'Contact create successfully!'
            }
        return result

    def get_contacts(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        result = {'result': False, 'msg': 'something went wrong!'}
        contact_list = []
        for contact in db.contacts_collection.find({"user_id": self.user_id}).sort('full_name'):
            contact_list.append(contact)
        return {
            'result': True,
            'data': contact_list
        }

    def get_contact_details(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if contact _id is set
        if self._id is None:
            raise Exception('contact _id not set')
        contact = db.contacts_collection.find_one({'_id': self._id, 'user_id': self.user_id})
        if contact is None:
            return {
                'result': False,
                'msg': 'Contact not found!'
            }
        self.user_id = contact['user_id']
        self.source_type = contact['source_type']
        self.source_name = contact['source_name']
        self.full_name = contact['full_name']
        self.mobile_numbers = contact['mobile_numbers']
        self.email = contact['email']
        self.data = contact
        return {
            'result': True,
            'data': contact
        }

    def add_mobile_number(self, mobile_number, _id=None):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if contact _id is set
        if self._id is None:
            raise Exception('contact _id not set')
        # check if mobile number is 10 digit
        if not re.match('[0-9]{10}', mobile_number):
            return {
                'result': False,
                'msg': 'Mobile Number should be 10 digit!',
                'invalid fields': {'contact_mobile_number': 'Mobile Number should be 10 digit!'}
            }
        added = db.contacts_collection.update_one({'_id': self._id, 'user_id': self.user_id}, {
            '$push': {
                'mobile_numbers': mobile_number
            }
        })
        if added.acknowledged:
            return {'result': True, 'msg': 'contact mobile number added successfully!'}
        return {'result': False, 'msg': 'something went wrong!'}

    def update_contact_details(self, _id=None, source_type=None, source_name=None, full_name=None,
                               mobile_numbers=None,
                               email=None):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if contact _id is set
        if self._id is None:
            raise Exception('contact _id not set')
        # get data
        data = {
            'source_type': str(source_type).strip().lower(),
            'source_name': str(source_name).strip().lower(),
            'full_name': str(full_name).strip().lower(),
            'mobile_numbers': mobile_numbers,
            'email': str(email).strip().lower()
        }
        contact_fields = ('source_type', 'source_name', 'full_name', 'mobile_numbers')
        # which fields need to update
        update_fields = []
        for field in contact_fields:
            if data[field] is not None:
                update_fields.append(field)
        if len(update_fields) == 0:
            return {'result': False, 'msg': 'no field is for update!'}
        # validate data
        is_valid = True
        invalid_fields = {}
        for field in ('source_type', 'source_name', 'full_name', 'email'):
            if field in update_fields:
                # check for empty fields
                if data[field] == '':
                    is_valid = False
                    invalid_fields[field] = 'Cannot be empty!'
        if 'mobile_numbers' in update_fields:
            # check if mobile numbers are in array format
            if not isinstance(data['mobile_numbers'], list):
                return {'result': False, 'msg': 'mobiles numbers are not in array format'}
            # check if mobile number is 10 digit
            invalid_numbers = []
            for number in data['mobile_numbers']:
                if not re.match('[0-9]{10}', number):
                    invalid_numbers.append(number)
            if len(invalid_numbers) > 0:
                is_valid = False
                invalid_fields['mobile_numbers'] = 'Mobile Number should be 10 digit:\n' + ','.join(invalid_numbers)
        # if any field is invalid
        if not is_valid:
            return {
                'result': False,
                'msg': 'Check fields:\n' + ', '.join(invalid_fields),
                'invalid_fields': invalid_fields
            }
        # if all fields are valid
        update = db.contacts_collection.update_one({'_id': self._id, 'user_id': self.user_id}, {
            '$set': data
        })
        # if contact updated in database
        if update.acknowledged:
            return {'result': True, 'msg': 'contact udpated successfully!'}
        # else show error
        return {'result': False, 'msg': 'something went wrong!'}

    def delete_contact(self, _id=None):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if contact _id is set
        if self._id is None:
            raise Exception('contact _id not set')
        # delete vehicles of this contact
        for vehicle in self.vehicle.get_vehicles()['data']:
            self.Vehicle(vehicle['_id'])
            self.vehicle.delete_vehicle()
        # delete contact in database
        delete = db.contacts_collection.delete_one({'_id': self._id, 'user_id': self.user_id})
        if delete.acknowledged:
            return {'result': True, 'msg': 'contact deleted successfully!'}
        return {'result': False, 'msg': 'something went wrong!'}


class Vehicle:

    def __init__(self, _id=None):
        self._id = _id
        # create policy class without policy id
        self.policy = Policy()
        self.policy.type = 'motor'
        if self._id is not None:
            self.policy.vehicle_id = self._id

    def Policy(self, _id):
        self.policy = Policy(_id)
        self.policy.policy_type = 'motor'
        self.policy.user_id = self.user_id
        self.policy.vehicle_id = self._id

    def create_vehicle_company(self, company_name):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # validate data
        data = str(company_name).strip().lower()
        if data == '':
            return {
                'result': False,
                'msg': 'new company name cannot be empty'
            }
        # create new vehicle company in database
        create = db.vehicle_companies_collection.insert_one({
            'created': datetime.datetime.utcnow(),
            'user_id': self.user_id,
            'company_name': data
        })
        if create.acknowledged:
            return {'result': True, '_id': create.inserted_id}
        return {'result': False, 'msg': 'something went wrong'}

    def delete_vehicle_company(self, company_id):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        delete = db.vehicle_companies_collection.delete_one({'_id':company_id, 'user_id': self.user_id})
        if delete.acknowledged:
            return {'result':True, 'msg': 'Vehicle Company deleted successfully!'}
        return {'result': False, 'msg': 'Something went wrong!'}

    def get_vehicle_companies(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        company_list = db.vehicle_companies_collection.find({"user_id": self.user_id}).sort('company_name')
        return {
            'result': True,
            'data': company_list
        }

    def get_vehicle_company_details(self, company_id):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        data = db.vehicle_companies_collection.find_one({"user_id": self.user_id, '_id': company_id})
        return {
            'result': True,
            'data': data
        }

    def create_vehicle_model(self, company_name, model_name):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # validate data
        data = {
            'company_name': str(company_name).strip().lower(),
            'model_name': str(model_name).strip().lower()
        }
        for field in data:
            if data[field] == '':
                return {
                    'result': False,
                    'msg': 'new ' + field + ' cannot be empty'
                }
        # create new vehicle model in database
        create = db.vehicle_companies_collection.update_one({
            'user_id': self.user_id,
            'company_name': data['company_name']
        },
            {
                '$push': {
                    'models': data['model_name']
                }
            }
        )
        print(data)
        if create.acknowledged:
            return {'result': True, 'msg': 'model added successfully!'}
        return {'result': False, 'msg': 'something went wrong'}

    def delete_vehicle_company_model(self, company_id, model_name):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        delete = db.vehicle_companies_collection.update_one({'_id':company_id, 'user_id': self.user_id}, {
            '$pull': {
                'models': model_name
            }
        })
        if delete.acknowledged:
            return {'result':True, 'msg': 'Vehicle model deleted successfully!'}
        return {'result': False, 'msg': 'Something went wrong!'}

    def create_vehicle(self, registration_number, registration_name, registration_date, vehicle_company, vehicle_model,
                       vehicle_cc, vehicle_mfg, vehicle_fuel_type):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if contact _id is set
        if self.contact_id is None:
            raise Exception('contact _id not set')
        # get data
        vehicle = {
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'created': datetime.datetime.utcnow(),
            'registration_number': str(registration_number).strip().lower(),
            'registration_name': str(registration_name).strip().lower(),
            'registration_date': registration_date,
            'vehicle_company': str(vehicle_company).strip().lower(),
            'vehicle_model': str(vehicle_model).strip().lower(),
            'vehicle_cc': vehicle_cc,
            'vehicle_mfg': vehicle_mfg,
            'vehicle_fuel_type': vehicle_fuel_type
        }
        # validate data
        is_valid = True
        invalid_fields = {}
        for field in ('registration_number', 'registration_name', 'vehicle_company', 'vehicle_model'):
            if vehicle[field] == '':
                is_valid = False
                invalid_fields[field] = 'Cannot be empty!'
        # validate registration number
        if 'registration_number' not in invalid_fields:
            if not re.match("[a-z]{2}[0-9]{1,2}[a-z]{1,3}[0-9]{4}", vehicle['registration_number']):
                is_valid = False
                invalid_fields['registration_number'] = 'Not valid format - xx00xxxx'
        if not is_valid:
            return {'result': False, 'msg': 'check fields:\n' + ', '.join(invalid_fields),
                    'invalid_fields': invalid_fields}
        # if registration date is set then format it for mongodb database
        if vehicle['registration_date'] != '':
            vehicle['registration_date'] = datetime.datetime.strptime(vehicle['registration_date'], '%Y-%m-%d')
        # all fields are valid create vehicle in database
        create = db.vehicles_collection.insert_one(vehicle)
        if create.acknowledged:
            return {'result': True, 'msg': 'vehicle created successfully!', '_id': create.inserted_id}
        return {'result': False, 'msg': 'something went wrong'}

    def get_vehicles(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if contact _id is set
        if self.contact_id is None:
            raise Exception('contact _id not set')
        vehicles = db.vehicles_collection.find({'user_id': self.user_id, 'contact_id': self.contact_id})
        return {'result': True, 'data': vehicles}

    def get_vehicle_details(self):
        # check if vehicle id is set
        if self._id is None:
            raise Exception('vehicle id is not set')
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # get vehicle data from database
        vehicle = db.vehicles_collection.find_one({'_id': self._id, 'user_id': self.user_id})
        if vehicle is None:
            return {'result': False, 'msg': 'vehicle not found'}
        self.data = vehicle
        return {'result': True, 'data': self.data}

    def update_vehicle_details(self, registration_number, registration_name, registration_date, vehicle_company,
                               vehicle_model,
                               vehicle_cc, vehicle_mfg, vehicle_fuel_type):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if vehicle _id is set
        if self._id is None:
            raise Exception('vehicle _id not set')
        # get data
        vehicle = {
            'updated': datetime.datetime.utcnow(),
            'registration_number': str(registration_number).strip().lower(),
            'registration_name': str(registration_name).strip().lower(),
            'registration_date': registration_date,
            'vehicle_company': str(vehicle_company).strip().lower(),
            'vehicle_model': str(vehicle_model).strip().lower(),
            'vehicle_cc': vehicle_cc,
            'vehicle_mfg': vehicle_mfg,
            'vehicle_fuel_type': vehicle_fuel_type
        }
        # validate data
        is_valid = True
        invalid_fields = {}
        for field in ('registration_number', 'registration_name', 'vehicle_company', 'vehicle_model'):
            if vehicle[field] == '':
                is_valid = False
                invalid_fields[field] = 'Cannot be empty!'
        if vehicle['vehicle_company'] == 'none':
            is_valid = False
            invalid_fields['vehicle_company'] = 'Cannot be empty!'
        # validate registration number
        if 'registration_number' not in invalid_fields:
            if not re.match("[a-z]{2}[0-9]{1,2}[a-z]{1,3}[0-9]{4}", vehicle['registration_number']):
                is_valid = False
                invalid_fields['registration_number'] = 'Not valid format - xx00xxxx'
        if not is_valid:
            return {'result': False, 'msg': 'check fields:\n' + ', '.join(invalid_fields),
                    'invalid_fields': invalid_fields}
        # if registration date is set then format it for mongodb database
        if vehicle['registration_date'] != '':
            vehicle['registration_date'] = datetime.datetime.strptime(vehicle['registration_date'], '%Y-%m-%d')
        # all fields are valid update vehicle details in database
        update = db.vehicles_collection.update_one({
            '_id': self._id,
            'user_id': self.user_id
        }, {
            '$set': vehicle
        })
        if update.acknowledged:
            return {'result': True, 'msg': 'vehicle details updated successfully!'}
        return {'result': False, 'msg': 'something went wrong'}

    def delete_vehicle(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if vehicle _id is set
        if self._id is None:
            raise Exception('vehicle _id not set')
        # delete this vehicle insurance policies
        for policy in self.policy.get_policies()['data']:
            self.Policy(policy['_id'])
            self.policy.delete_policy()
        # delete vehicle in database
        delete = db.vehicles_collection.delete_one({'_id': self._id, 'user_id': self.user_id})
        if delete.acknowledged:
            return {'result': True, 'msg': 'vehicle deleted successfully!'}
        return {'result': False, 'msg': 'something went wrong!'}


class Policy:

    def __init__(self, _id=None):
        self._id = _id
        self.policy_type = None

    def create_policy(self, policy_type=None, expiry_date=None, own_business=None, policy_number=None, cover_type=None,
                      addon_covers=None, insurance_company=None, idv=None, ncb=None,
                      premium=None, payout=None, discount=None):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if vehicle _id is set
        if self.vehicle_id is None:
            raise Exception('vehicle _id not set')
        # check if policy type is set
        if self.policy_type is None:
            raise Exception('policy type not set!')
        # get data
        policy = {
            'user_id': self.user_id,
            'vehicle_id': self.vehicle_id,
            'created': datetime.datetime.utcnow(),
            'policy_type': policy_type,
            'expiry_date': expiry_date,
            'own_business': own_business,
            'policy_number': str(policy_number).strip().lower(),
            'cover_type': str(cover_type).strip().lower(),
            'addon_covers': addon_covers,
            'insurance_company': str(insurance_company).strip().lower(),
            'idv': idv,
            'ncb': ncb,
            'premium': premium,
            'payout': payout,
            'discount': discount
        }
        # validate data
        is_valid = True
        invalid_fields = {}
        # check required fields
        if policy['expiry_date'] == '':
            is_valid = False
            invalid_fields[field] = 'Cannot be empty!'
        if not is_valid:
            return {'result': False, 'msg': 'check fields:\n' + ', '.join(invalid_fields),
                    'invalid_fields': invalid_fields}
        # format expiry date for mongodb database
        policy['expiry_date'] = datetime.datetime.strptime(policy['expiry_date'], '%Y-%m-%d')
        # if all fields are valid
        create = db.insurance_policies_collection.insert_one(policy)
        if create.acknowledged:
            return {'result': True, 'msg': 'vehicle policy created successfully!', '_id': create.inserted_id}
        return {'result': False, 'msg': 'something went wrong!'}

    def get_policies(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if vehicle _id is set
        if self.vehicle_id is None:
            raise Exception('vehicle _id not set')
        # check if policy type is set
        if self.policy_type is None:
            raise Exception('policy type not set!')
        policies = db.insurance_policies_collection.find({'user_id': self.user_id, 'vehicle_id': self.vehicle_id})
        return {'result': True, 'data': policies}

    def create_insurance_company(self, company_name):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # validate data
        data = str(company_name).strip().lower()
        if data == '':
            return {
                'result': False,
                'msg': 'new company name cannot be empty'
            }
        # create new insurance company in database
        create = db.insurance_companies_collection.insert_one({
            'created': datetime.datetime.utcnow(),
            'user_id': self.user_id,
            'company_name': data
        })
        if create.acknowledged:
            return {'result': True, 'msg': 'insurance company created successfully!', '_id': create.inserted_id}
        return {'result': False, 'msg': 'something went wrong'}

    def delete_insurance_company(self, company_id):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        delete = db.insurance_companies_collection.delete_one({'_id':company_id, 'user_id': self.user_id})
        if delete.acknowledged:
            return {'result': True, 'msg': 'Insurance Company deleted Successfully!'}
        return {'result':False, 'msg': 'Something went wrong'}

    def get_insurance_companies(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        company_list = db.insurance_companies_collection.find({"user_id": self.user_id}).sort('company_name')
        return {
            'result': True,
            'data': company_list
        }

    def get_policy_details(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if policy _id is set
        if self._id is None:
            raise Exception('policy _id not set')
        # check if policy type is set
        if self.policy_type is None:
            raise Exception('policy type not set!')
        if self.policy_type == 'motor':
            # get vehicle policy data from database
            policy = db.insurance_policies_collection.find_one({'_id': self._id, 'user_id': self.user_id})
            if policy is None:
                return {'result': False, 'msg': 'vehicle policy not found'}
            self.data = policy
            return {'result': True, 'data': self.data}
        return {'result': False, 'msg': 'something went wrong'}

    def update_policy(self, policy_type=None, expiry_date=None, own_business=None, policy_number=None, cover_type=None,
                      addon_covers=None, insurance_company=None, idv=None, ncb=None,
                      premium=None, payout=None, discount=None):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if policy _id is set
        if self._id is None:
            raise Exception('policy _id not set')
        # check if policy type is set
        if self.policy_type is None:
            raise Exception('policy type not set!')
        # get data
        policy = {
            'updated': datetime.datetime.utcnow(),
            'policy_type': policy_type,
            'expiry_date': expiry_date,
            'own_business': own_business,
            'policy_number': str(policy_number).strip().lower(),
            'cover_type': str(cover_type).strip().lower(),
            'addon_covers': addon_covers,
            'insurance_company': str(insurance_company).strip().lower(),
            'idv': idv,
            'ncb': ncb,
            'premium': premium,
            'payout': payout,
            'discount': discount
        }
        # validate data
        is_valid = True
        invalid_fields = {}
        # check required fields
        if policy['expiry_date'] == '':
            is_valid = False
            invalid_fields['expiry_date'] = 'Cannot be empty!'
        if policy['insurance_company'] == 'none':
            is_valid = False
            invalid_fields['insurance_company'] = 'Cannot be empty!'
        if not is_valid:
            return {'result': False, 'msg': 'check fields:\n' + ', '.join(invalid_fields),
                    'invalid_fields': invalid_fields}
        # format expiry date for mongodb database
        policy['expiry_date'] = datetime.datetime.strptime(policy['expiry_date'], '%Y-%m-%d')
        # if all fields are valid
        update = db.insurance_policies_collection.update_one({'_id': self._id, 'user_id': self.user_id}, {
            '$set': policy
        })
        if update.acknowledged:
            return {'result': True, 'msg': 'vehicle policy updated successfully!'}
        return {'result': False, 'msg': 'something went wrong!'}

    def delete_policy(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if policy _id is set
        if self._id is None:
            raise Exception('policy _id not set')
        # check if policy type is set
        if self.policy_type is None:
            raise Exception('policy type not set!')
        delete = db.insurance_policies_collection.delete_one({'_id': self._id, 'user_id': self.user_id})
        if delete.acknowledged:
            # remove policy id from renewal id
            db.insurance_policies_collection.update_one({'renewal_id':self._id}, {
                '$unset': {
                    'renewal_id': ''
                }
            })
            return {'result': True, 'msg': 'Vehicle policy deleted successfully!'}
        return {'result': False, 'msg': 'something went wrong'}

    def get_renewals(self, expiry_month, expiry_year):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        policy_list = db.insurance_policies_collection.aggregate([
            {'$addFields': {'expiry_day': {'$dayOfMonth': '$expiry_date'},
                            'expiry_month': {'$month': '$expiry_date'},
                            'expiry_year': {'$year': '$expiry_date'}}},
            {'$match': {'$and': [
                {'user_id': self.user_id},
                {'expiry_month': {'$eq': expiry_month}},
                {'expiry_year': {'$lte': expiry_year}}
            ]}},
            {'$sort': {'expiry_year': -1}},
            {'$group': {
                '_id': '$vehicle_id',

                'policy': {'$first': '$$ROOT'},
                'policy_id': {'$first': '$$ROOT._id'},
                'expiry_date': {'$first': '$$ROOT.expiry_date'},
                'vehicle_id': {'$first': '$$ROOT.vehicle_id'}
            }},
            {'$sort': {'policy.expiry_day': 1}},
            {'$lookup': {
                'from': 'followups',
                "let": { "policy_id": "$policy_id" },
                'pipeline': [
                    {"$match": {"$expr": {"$eq": ["$policy_id", "$$policy_id"]}}},
                    {'$sort': {'created': -1}},
                    {'$limit': 1}
                ],
                'as': 'followups'
            }},
            {'$addFields': {'followups': {
                "$arrayElemAt": ["$followups", 0]
            }}},
            {'$lookup': {
                'from': 'vehicles',
                'localField': 'vehicle_id',
                'foreignField': '_id',
                'as': 'vehicle'
            }},
            {'$addFields': {'vehicle': {
                "$arrayElemAt": ["$vehicle", 0]
            }}},
            {'$lookup': {
                'from': 'contacts',
                'localField': 'vehicle.contact_id',
                'foreignField': '_id',
                'as': 'contact'
            }},
            {'$addFields': {'contact': {
                "$arrayElemAt": ["$contact", 0]
            }}}
        ])
        data = list(policy_list)
        # add policy status field
        for policy in data:
            policy['status'] = None
            if 'renewal_id' in policy['policy']:
                policy['status'] = 'won'
            else:
                if 'followups' in policy:
                    policy['status'] = policy['followups']['policy_status']
        return {'result': True, 'data': data}

    def get_renewal_details(self):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if policy _id is set
        if self._id is None:
            raise Exception('policy _id not set')
        # check if policy type is set
        if self.policy_type is None:
            raise Exception('policy type not set!')
        if self.policy_type == 'motor':
            # get vehicle policy data from database
            policy = db.insurance_policies_collection.find_one({'_id': self._id, 'user_id': self.user_id})
            if policy is None:
                return {'result': False, 'msg': 'vehicle policy not found'}
            self.data = {}
            self.data['policy'] = policy
            self.data['followups'] = db.followups_collection.find({'policy_id':policy['_id']}).sort('created', -1)
            self.user = User(self.user_id)
            # get vehicle details
            self.user.contact.Vehicle(policy['vehicle_id'])
            vehicle = self.user.contact.vehicle.get_vehicle_details()['data']
            self.data['vehicle'] = vehicle
            # get contact details
            self.user.Contact(vehicle['contact_id'])
            contact = self.user.contact.get_contact_details()['data']
            self.data['contact'] = contact
            return {'result': True, 'data': self.data}
        return {'result': False, 'msg': 'something went wrong'}

    def post_followup(self, remark):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if policy _id is set
        if self._id is None:
            raise Exception('policy _id not set')
        # check if policy type is set
        if self.policy_type is None:
            raise Exception('policy type not set!')
        # validate data
        remark = str(remark).strip()
        if remark == '':
            return {
                'result': False,
                'msg': 'check fields!',
                'invalid_fields': {'remark': 'remark cannot be empty'}
            }
        followup = {
            'created': datetime.datetime.utcnow(),
            'user_id': self.user_id,
            'policy_id': self._id,
            'remark': remark,
            'policy_status': 'followup'
        }
        create = db.followups_collection.insert_one(followup)
        if create.acknowledged:
            return {'result': True, '_id': create.inserted_id}
        return {'result': False, 'msg': 'Something went wrong!'}

    def renew_policy(self, expiry_date=None, own_business=None, policy_number=None, cover_type=None,
                      addon_covers=None, insurance_company=None, idv=None, ncb=None,
                      premium=None, payout=None, discount=None):
        # check if user id is set
        if self.user_id is None:
            raise Exception('user _id not set!')
        # check if policy _id is set
        if self._id is None:
            raise Exception('policy _id not set')
        # check if policy type is set
        if self.policy_type is None:
            raise Exception('policy type not set!')
        # set vehicle id
        self.get_policy_details()
        self.vehicle_id = self.data['vehicle_id']
        # validate data
        # check if new expiry date is equal or older then current expiry date
        if int(expiry_date[:4]) <= self.data['expiry_date'].year:
            return {
                'result':False,
                'msg': 'Expiry Year should be greater than current year.',
                'invalid_fields': {'expiry_date': 'Expiry Year should be greater than current year.'}
            }
        # add new policy
        new_policy = self.create_policy(expiry_date=expiry_date, own_business=own_business,
                                                       policy_number=policy_number, cover_type=cover_type,
                                                       addon_covers=addon_covers,
                                                       insurance_company=insurance_company, idv=idv, ncb=ncb,
                                                       premium=premium,
                                                       payout=payout, discount=discount)
        if new_policy['result'] is not True:
            return new_policy
        # update new policy id to renewal id
        db.insurance_policies_collection.update_one({'_id': self._id}, {
            '$set': {
                'renewal_id': new_policy['_id']
            }
        })
        # add policy done remark
        self.post_followup('Policy Renewed!')
        return {'result': True, '_id': new_policy['_id']}