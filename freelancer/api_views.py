from freelancer import app, request, controllers, models, session, db
import json
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime



@app.route('/ajax/submit_query', methods=['POST'])
def submit_query_api():
    result = {}
    result['result'] = False
    query = {}
    query['name'] = request.form.get('name')
    query['contact'] = str.strip(request.form.get('contact'))
    if query['contact'] in (None, ''):
        result['msg'] = 'Contact cannot be empty.'
        return result
    query['remark'] = request.form.get('remark')
    query['created'] = datetime.utcnow()
    insert_query = db.query_collection.insert_one(query)
    if insert_query.acknowledged:
        result['result'] = True
    return dumps(result)


@app.route('/api/login', methods=["POST"])
def login_api():
    username = request.form['username']
    password = request.form['password']
    result = models.user().login(username, password)
    return dumps(result)


@app.route('/api/add_person', methods=['POST'])
def add_person_api():
    if not session.get('logged_in'):
        return dumps({'result': False, 'msg': 'Login required.'})
    result = {'result': False}
    form_data = request.form
    name = form_data['name']
    source_type = form_data['source_type']
    source_data = form_data['source_data']
    numbers = []
    for number in form_data.getlist('number[]'):
        numbers.append(number)
    user_id = ObjectId(session['user']['_id'])
    return dumps(models.user(user_id).add_person(name, numbers, source_type, source_data))


@app.route('/api/get_person_list', methods=['POST'])
def get_person_list_api():
    if not session.get('logged_in'):
        return dumps({'result': False, 'msg': 'Login required.'})
    query = request.form['query']
    if query == None:
        result = models.Person().get()
    else:
        result = models.Person().find(['name', 'numbers'], query)
    return dumps({'result': True, 'data': result.sort('name', 1)})


@app.route('/api/get_motor_renewal_list', methods=['POST'])
def get_motor_renewal_list_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {'result': False}
    month = request.form.get('month')
    year = request.form.get('year')
    result['data'] = models.Policy_motor().get_renewal_list(month, year)
    result['result'] = True
    return dumps(result)


@app.route('/api/view_motor_renewal/<_id>', methods=['POST'])
def view_motor_renewal_api(_id):
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {}
    result['result'] = False
    policy = models.Policy_motor(ObjectId(_id))
    if policy.person == None:
        result['msg'] = 'Person ID not found.'
        return result
    if policy.registration == None:
        result['msg'] = 'Registration ID not found.'
        return result
    data = {}
    data['policy'] = policy.db_data
    data['registration'] = policy.registration.db_data
    data['person'] = policy.person.db_data
    data['renewal_policy'] = policy.renewal_policy.db_data
    data['old_policy'] = policy.old_policy
    data['followup_list'] = policy.get_followup_list()
    result['data'] = data
    result['result'] = True
    return dumps(result)


@app.route('/api/post_policy_followup', methods=['POST'])
def post_policy_followup():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    policy_id = ObjectId(request.form.get('policy_id'))
    remark = request.form.get('remark')
    type = request.form.get('type')
    policy = None
    if type == 'motor':
        policy = models.Policy_motor(policy_id)
    elif type == 'health':
        policy = models.Policy_health(policy_id)
    return dumps(policy.post_policy_followup(remark))


@app.route('/api/add_contact_number', methods=['POST'])
def add_contact_number_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    person_id = ObjectId(request.form.get('_id'))
    number = request.form.get('number')
    return dumps(models.Person(person_id).add_contact_number(number))


@app.route('/api/remove_contact_number', methods=['POST'])
def remove_contact_number_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    person_id = ObjectId(request.form.get('_id'))
    number = request.form.get('number')
    return dumps(models.Person(person_id).remove_contact_number(number))


@app.route('/api/add_contact_email', methods=['POST'])
def add_contact_email_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    person_id = ObjectId(request.form.get('_id'))
    email = request.form.get('email')
    return dumps(models.Person(person_id).add_contact_email(email))


@app.route('/api/remove_email', methods=['POST'])
def remove_email_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    person_id = ObjectId(request.form.get('_id'))
    email = request.form.get('email')
    return dumps(models.Person(person_id).remove_contact_email(email))


@app.route('/api/delete_person', methods=['POST'])
def delete_person_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    person_id = ObjectId(request.form.get('person_id'))
    return dumps(models.Person(person_id).delete_person())


@app.route('/api/add_vehicle', methods=['POST'])
def add_vehicle_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    user_id = ObjectId(session['user']['_id'])
    person_id = ObjectId(request.form.get('person_id'))
    registration_number = request.form.get('registration_number')
    registration_name = request.form.get('registration_name')
    registration_date = request.form.get('registration_date')
    company = request.form.get('company')
    model = request.form.get('model')
    cc = request.form.get('cc')
    fuel = request.form.get('fuel')
    mfg = request.form.get('mfg')
    return dumps(models.Person(person_id).add_registration(registration_number, registration_name,
                                                           registration_date,
                                                           company, model, cc, fuel, mfg))


@app.route('/api/view_vehicle', methods=['POST'])
def view_vehicle_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {'result': False}
    registration_id = ObjectId(request.form['registration_id'])
    registration = models.Registration(registration_id)
    if registration.db_data != None:
        result['result'] = True
        result['data'] = registration.db_data
    return dumps(result)


@app.route('/api/delete_vehicle', methods=['POST'])
def delete_vehicle_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    registration_id = ObjectId(request.form['registration_id'])
    return dumps(models.Registration(registration_id).delete_registration())


@app.route('/api/add_motor_policy', methods=['POST'])
def add_motor_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    registration_id = ObjectId(request.form.get('registration_id'))
    expiry_date = request.form.get('expiry_date')
    policy_number = request.form.get('policy_number')
    policy_type = request.form.get('policy_type')
    company = request.form.get('company')
    idv = request.form.get('idv')
    ncb = request.form.get('ncb')
    premium = request.form.get('premium')
    own_business = True if 'own_business' in request.form else False
    o_dap = True if 'o_dap' in request.form else False
    return dumps(
        models.Registration(registration_id).add_motor_policy(expiry_date, policy_number, policy_type, company, idv,
                                                              ncb, premium, own_business, o_dap))


@app.route('/api/view_vehicle_policy/<policy_id>')
def view_vehicle_policy_api(policy_id):
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {'result': False}
    policy_id = ObjectId(policy_id)
    policy = models.Policy_motor(policy_id)
    if policy.db_data != None:
        result['result'] = True
        result['data'] = policy.db_data
    return dumps(result)


@app.route('/api/delete_vehicle_policy', methods=['POST'])
def delete_vehicle_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    policy_id = ObjectId(request.form['policy_id'])
    return dumps(models.Policy_motor(policy_id).delete_policy())


@app.route('/api/add_renewal_motor_policy', methods=['POST'])
def add_renewal_motor_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    policy_id = ObjectId(request.form.get('policy_id'))
    remark = request.form.get('remark')
    policy = models.Policy_motor(policy_id)
    registration_id = policy.registration_id
    expiry_date = request.form.get('expiry_date')
    policy_number = request.form.get('policy_number')
    policy_type = request.form.get('policy_type')
    company = request.form.get('company')
    idv = request.form.get('idv')
    ncb = request.form.get('ncb')
    premium = request.form.get('premium')
    own_business = True if 'own_business' in request.form else False
    o_dap = True if 'o_dap' in request.form else False
    insert_new_policy = models.Registration(registration_id).add_motor_policy(expiry_date, policy_number, policy_type,
                                                                              company, idv,
                                                                              ncb, premium, own_business, o_dap)
    if insert_new_policy['result']:
        result['result'] = True
        result['new_id'] = insert_new_policy['new_id']
        # add new policy id & policy status in old policy data
        db.motor_policy_collection.update_one({'_id': policy._id}, {
            '$set': {'policy_status': 'renewed', 'renewal_id': result['new_id']}
        })
        # add followup
        remark = 'Policy renewed!\n' + str.strip(remark)
        models.Policy_motor(policy_id).post_policy_followup(remark)
    return dumps(result)


@app.route('/api/update_vehicle_policy', methods=['POST'])
def update_vehicle_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    policy_id = ObjectId(request.form.get('policy_id'))
    policy = models.Policy_motor(policy_id)
    expiry_date = request.form.get('expiry_date')
    policy_number = request.form.get('policy_number')
    policy_type = request.form.get('policy_type')
    company = request.form.get('company')
    idv = request.form.get('idv')
    ncb = request.form.get('ncb')
    premium = request.form.get('premium')
    own_business = True if 'own_business' in request.form else False
    o_dap = True if 'o_dap' in request.form else False
    result = policy.update_motor_policy(expiry_date, policy_number, policy_type, company, idv, ncb, premium,
                                        own_business, o_dap)
    return dumps(result)


@app.route('/api/update_vehicle', methods=['POST'])
def update_vehicle_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    registration_id = ObjectId(request.form.get('registration_id'))
    registration = models.Registration(registration_id)
    registration_number = request.form.get('registration_number')
    registration_name = request.form.get('registration_name')
    registration_date = request.form.get('registration_date')
    company = request.form.get('company')
    model = request.form.get('model')
    cc = request.form.get('cc')
    fuel = request.form.get('fuel')
    mfg = request.form.get('mfg')
    result = registration.update_registration(registration_number, registration_name, registration_date, company, model,
                                              cc, fuel, mfg)
    return dumps(result)


@app.route('/api/add_health_policy', methods=['POST'])
def add_health_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    person_id = ObjectId(request.form.get('person_id'))
    expiry_date = request.form.get('expiry_date')
    policy_owner = request.form.get('policy_owner')
    policy_number = request.form.get('policy_number')
    policy_type = request.form.get('policy_type')
    company = request.form.get('company')
    idv = request.form.get('idv')
    ncb = request.form.get('ncb')
    premium = request.form.get('premium')
    own_business = True if 'own_business' in request.form else False
    return dumps(
        models.Person(person_id).add_health_policy(expiry_date,policy_owner, policy_number, policy_type, company, idv,
                                                              ncb, premium, own_business))


@app.route('/api/view_health_policy/<policy_id>')
def view_health_policy_api(policy_id):
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {'result': False}
    policy_id = ObjectId(policy_id)
    policy = models.Policy_health(policy_id)
    if policy.db_data != None:
        result['result'] = True
        result['data'] = policy.db_data
    return dumps(result)


@app.route('/api/update_health_policy', methods=['POST'])
def update_health_policy():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    policy_id = ObjectId(request.form.get('policy_id'))
    policy = models.Policy_health(policy_id)
    expiry_date = request.form.get('expiry_date')
    policy_owner = request.form.get('policy_owner')
    policy_number = request.form.get('policy_number')
    policy_type = request.form.get('policy_type')
    company = request.form.get('company')
    idv = request.form.get('idv')
    ncb = request.form.get('ncb')
    premium = request.form.get('premium')
    own_business = True if 'own_business' in request.form else False
    result = policy.update_health_policy(expiry_date,policy_owner, policy_number, policy_type, company, idv, ncb, premium,
                                        own_business)
    return dumps(result)


@app.route('/api/delete_health_policy', methods=['POST'])
def delete_health_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    policy_id = ObjectId(request.form['policy_id'])
    return dumps(models.Policy_health(policy_id).delete_policy())


@app.route('/api/view_health_renewal/<_id>', methods=['POST'])
def view_health_renewal(_id):
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {}
    result['result'] = False
    policy = models.Policy_health(ObjectId(_id))
    if policy.person == None:
        result['msg'] = 'Person ID not found.'
        return result
    data = {}
    data['policy'] = policy.db_data
    data['person'] = policy.person.db_data
    data['renewal_policy'] = policy.renewal_policy.db_data
    data['old_policy'] = policy.old_policy
    data['followup_list'] = policy.get_followup_list()
    result['data'] = data
    result['result'] = True
    return dumps(result)


@app.route('/api/get_health_renewal_list', methods=['POST'])
def get_health_renewal_list():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {'result': False}
    month = request.form.get('month')
    year = request.form.get('year')
    result['data'] = models.Policy_health().get_renewal_list(month, year)
    result['result'] = True
    print(result)
    return dumps(result)


@app.route('/api/add_renewal_health_policy', methods=['POST'])
def add_renewal_health_policy():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    policy_id = ObjectId(request.form.get('policy_id'))
    remark = request.form.get('remark')
    policy = models.Policy_health(policy_id)
    expiry_date = request.form.get('expiry_date')
    policy_owner = policy.policy_owner
    policy_number = request.form.get('policy_number')
    policy_type = request.form.get('policy_type')
    company = request.form.get('company')
    idv = request.form.get('idv')
    ncb = request.form.get('ncb')
    premium = request.form.get('premium')
    own_business = True if 'own_business' in request.form else False
    insert_new_policy = models.Person(policy.person_id).add_health_policy(expiry_date,policy_owner, policy_number, policy_type,
                                                                              company, idv,
                                                                              ncb, premium, own_business)
    if insert_new_policy['result']:
        result['result'] = True
        result['new_id'] = insert_new_policy['new_id']
        # add new policy id & policy status in old policy data
        db.health_policy_collection.update_one({'_id': policy._id}, {
            '$set': {'policy_status': 'renewed', 'renewal_id': result['new_id']}
        })
        # add followup
        remark = 'Policy renewed!\n' + str.strip(remark)
        models.Policy_health(policy_id).post_policy_followup(remark)
    return dumps(result)


@app.route('/api/get_followup_list', methods=['POST'])
def get_followup_list_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {}
    result['result'] = False
    result['msg'] = 'Something went wrong.'
    policy_id = ObjectId(request.form.get('policy_id'))
    type = request.form.get('type')
    policy = None
    if type == 'motor':
        policy = models.Policy_motor(policy_id)
    elif type == 'health':
        policy = models.Policy_health(policy_id)
    result['followup_list'] = []
    for followup in policy.get_followup_list():
        result['followup_list'].append(followup)
    result['result'] = True
    return dumps(result)
