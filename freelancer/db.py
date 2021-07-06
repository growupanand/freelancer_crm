import pymongo
import os

# get db address and name from environment variable
db_address = os.environ.get('db_address', "mongodb://localhost")
selected_db = os.environ.get('db_name', "test_crm")


client = pymongo.MongoClient(db_address)
db = client[selected_db]
users_collection = db['users']
contacts_collection = db['contacts']
vehicles_collection = db['vehicles']
insurance_policies_collection = db['insurance_policies']
vehicle_companies_collection = db['vehicle_companies']
insurance_companies_collection = db['insurance_companies']
followups_collection = db['followups']
test_collection = db['test']
