from freelancer import app, request, controllers, models, session
import json
from bson import ObjectId
from bson.json_util import dumps


@app.route('/ajax/submit_query', methods=['POST'])
def submit_query_api():
    result = {}
    result['result'] = False
    data = {}
    data['query_name'] = request.form.get('query_name')
    data['query_contact'] = request.form.get('query_contact')
    data['query_content'] = request.form.get('query_content')
    if controllers.submit_query(data).acknowledged:
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
    form_data = request.form
    numbers = []
    for number in form_data.getlist('number[]'):
        numbers.append(number)
    result = models.Person().add_person(
        name=form_data['name'],
        numbers=numbers,
        source_type=form_data['source_type'],
        source_data=form_data['source_data']
    )
    return dumps(result)


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


@app.route('/api/get_renewal_list', methods=['POST'])
def get_renewal_list_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    month = request.form.get('month')
    year = request.form.get('year')
    return dumps(models.Policy().get_renewal_list(month, year))


@app.route('/api/view_renewal/<_id>', methods=['POST'])
def view_renewal_api(_id):
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    result = {}
    result['result'] = False
    policy = models.Policy(ObjectId(_id))
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
    data = {}
    data['policy_id'] = request.form.get('policy_id')
    data['remark'] = request.form.get('remark')
    data['policy_status'] = request.form.get('policy_status')
    return json.dumps(controllers.post_policy_followup(data))


@app.route('/api/add_contact_number', methods=['POST'])
def add_contact_number_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    _id = request.form.get('_id')
    number = request.form.get('number')
    return json.dumps(controllers.add_contact_number(_id, number))


@app.route('/api/remove_contact_number', methods=['POST'])
def remove_contact_number_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    _id = request.form.get('_id')
    number = request.form.get('number')
    return json.dumps(controllers.remove_contact_number(_id, number))


@app.route('/api/add_contact_email', methods=['POST'])
def add_contact_email_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    _id = request.form.get('_id')
    email = request.form.get('email')
    return json.dumps(controllers.add_contact_email(_id, email))


@app.route('/api/remove_email', methods=['POST'])
def remove_email_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    _id = request.form.get('_id')
    email = request.form.get('email')
    return json.dumps(controllers.remove_email(_id, email))


@app.route('/api/delete_person', methods=['POST'])
def delete_person_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    person_id = request.form.get('person_id')
    return json.dumps(controllers.delete_person(person_id))


@app.route('/api/add_vehicle', methods=['POST'])
def add_vehicle_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    data = request.form
    return json.dumps(controllers.add_vehicle(data))


@app.route('/api/view_vehicle', methods=['POST'])
def view_vehicle_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    return json.dumps(controllers.view_vehicle(request.form['registration_id']))


@app.route('/api/delete_vehicle', methods=['POST'])
def delete_vehicle_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    return json.dumps(controllers.delete_vehicle(request.form['registration_id']))


@app.route('/api/update_vehicle', methods=['POST'])
def update_vehicle_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    data = request.form
    return json.dumps(controllers.update_vehicle(data))


@app.route('/api/add_motor_policy', methods=['POST'])
def add_motor_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    data = request.form
    return json.dumps(controllers.add_motor_policy(data))


@app.route('/api/view_vehicle_policy', methods=['POST'])
def view_vehicle_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    return json.dumps(controllers.view_vehicle_policy(request.form['policy_id']))


@app.route('/api/delete_vehicle_policy', methods=['POST'])
def delete_vehicle_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    return json.dumps(controllers.delete_vehicle_policy(request.form['policy_id']))


@app.route('/api/update_vehicle_policy', methods=['POST'])
def update_vehicle_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    data = request.form
    return json.dumps(controllers.update_vehicle_policy(data))


@app.route('/api/add_renewal_motor_policy', methods=['POST'])
def add_renewal_motor_policy_api():
    if not session.get('logged_in'):
        return json.dumps({'result': False, 'msg': 'Login required.'})
    data = request.form
    return json.dumps(controllers.add_renewal_motor_policy(data))
