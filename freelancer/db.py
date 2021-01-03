import pymongo

client = pymongo.MongoClient("mongodb://localhost",27017)


db = client['uafs_crm'] #uafs freelancer database
#db = client['vw_crm'] #vw database
query_collection = db['queries']
user_collection = db['users']
persons_collection = db['persons']
motor_policy_collection = db['motor_insurance_policy']
motor_registration_collection = db['motor_registration']
