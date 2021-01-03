from freelancer import app, request, controllers
import json

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
    return json.dumps(result)


@app.route('/api/login', methods=["POST"])
def login_api():
    username = request.form['username']
    password = request.form['password']
    result = controllers.login(username, password)
    return json.dumps(result)


@app.route('/api/add_person', methods=['POST'])
def add_person_api():
    form_data = request.form
    return json.dumps(controllers.add_person(form_data))


@app.route('/api/get_person_list', methods=['POST'])
def find_person_api():
    return json.dumps(controllers.get_person_list(request.form.get('query')))


@app.route('/api/get_renewal_list', methods=['POST'])
def get_renewal_list_api():
    month = request.form.get('month')
    year = request.form.get('year')
    return json.dumps(controllers.get_renewal_list(month, year))


@app.route('/api/view_renewal', methods=['POST'])
def view_renewal_api():
    _id = request.form.get('_id')
    return json.dumps(controllers.view_renewal(_id))


@app.route('/api/post_policy_followup', methods=['POST'])
def post_policy_followup():
    data = {}
    data['policy_id'] = request.form.get('policy_id')
    data['remark'] = request.form.get('remark')
    data['policy_status'] = request.form.get('policy_status')
    return json.dumps(controllers.post_policy_followup(data))


@app.route('/api/add_contact_number', methods=['POST'])
def add_contact_number_api():
    _id = request.form.get('_id')
    number = request.form.get('number')
    return json.dumps(controllers.add_contact_number(_id, number))


@app.route('/api/remove_contact_number', methods=['POST'])
def remove_contact_number_api():
    _id = request.form.get('_id')
    number = request.form.get('number')
    return json.dumps(controllers.remove_contact_number(_id, number))


@app.route('/api/add_contact_email', methods=['POST'])
def add_contact_email_api():
    _id = request.form.get('_id')
    email = request.form.get('email')
    return json.dumps(controllers.add_contact_email(_id, email))


@app.route('/api/remove_email', methods=['POST'])
def remove_email_api():
    _id = request.form.get('_id')
    email = request.form.get('email')
    return json.dumps(controllers.remove_email(_id, email))


@app.route('/api/delete_person', methods=['POST'])
def delete_person_api():
    person_id = request.form.get('person_id')
    return json.dumps(controllers.delete_person(person_id))


@app.route('/api/add_vehicle', methods=['POST'])
def add_vehicle_api():
    data = request.form
    return json.dumps(controllers.add_vehicle(data))


@app.route('/api/view_vehicle', methods=['POST'])
def view_vehicle_api():
    return json.dumps(controllers.view_vehicle(request.form['registration_number']))


@app.route('/api/delete_vehicle', methods=['POST'])
def delete_vehicle_api():
    return json.dumps(controllers.delete_vehicle(request.form['registration_id']))

@app.route('/api/update_vehicle', methods=['POST'])
def update_vehicle_api():
    data = request.form
    return json.dumps(controllers.update_vehicle(data))


@app.route('/api/add_motor_policy', methods=['POST'])
def add_motor_policy_api():
    data = request.form
    return json.dumps(controllers.add_motor_policy(data))


@app.route('/api/view_vehicle_policy', methods=['POST'])
def view_vehicle_policy_api():
    return json.dumps(controllers.view_vehicle_policy(request.form['policy_id']))


@app.route('/api/delete_vehicle_policy', methods=['POST'])
def delete_vehicle_policy_api():
    return json.dumps(controllers.delete_vehicle_policy(request.form['policy_id']))


@app.route('/api/update_vehicle_policy', methods=['POST'])
def update_vehicle_policy_api():
    data = request.form
    return json.dumps(controllers.update_vehicle_policy(data))

@app.route('/api/add_renewal_motor_policy', methods=['POST'])
def add_renewal_motor_policy_api():
    data = request.form
    return json.dumps(controllers.add_renewal_motor_policy(data))