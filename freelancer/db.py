import pymongo

selected_db = 'test_crm'

client = pymongo.MongoClient("mongodb://localhost",27017)
db = client[selected_db]
users_collection = db['users']
contacts_collection = db['contacts']
vehicles_collection = db['vehicles']
insurance_policies_collection = db['insurance_policies']
vehicle_companies_collection = db['vehicle_companies']
insurance_companies_collection = db['insurance_companies']
followups_collection = db['followups']
test_collection = db['test']
