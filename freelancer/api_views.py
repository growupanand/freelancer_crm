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
    return json.dumps(controllers.get_renewal_list(month))


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

@app.route('/api/add_contact_email', methods=['POST'])
def add_contact_email_api():
    _id = request.form.get('_id')
    email = request.form.get('email')
    return json.dumps(controllers.add_contact_email(_id, email))