import sys
import pymongo

selected_db = 'uafs_crm'

if len(sys.argv)>1 and sys.argv[1] == 'vw':
    selected_db = 'vw_crm'

client = pymongo.MongoClient("mongodb://localhost",27017)

db = client[selected_db]
query_collection = db['queries']
user_collection = db['users']
persons_collection = db['persons']
motor_policy_collection = db['motor_insurance_policy']
motor_registration_collection = db['motor_registration']
followup_collection = db['followup']
health_policy_collection = db['health_insurance_policy']
lead_collection = db['leads']
