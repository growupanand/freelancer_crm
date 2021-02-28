from freelancer import app, render_template, session, db, functions, models, redirect, url_for
from bson import ObjectId


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/logout')
def logout_page():
    session.clear()
    return render_template('login.html')


@app.route('/admin')
def admin_index_page():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if session['user']['type'] == 'admin':
                return render_template('admin/index.html')
    return render_template('login.html')


@app.route('/contacts')
def admin_contacts_page():
    if not session.get('logged_in'):
        return login_page()
    recent_added = models.Person().get().limit(10).sort('_id', -1)
    return render_template('admin/contacts.html', recent_added=recent_added)


@app.route('/crm/view_person/<_id>')
def view_person_page(_id):
    if not session.get('logged_in'):
        return login_page()
    person_id = ObjectId(_id)
    person = models.Person(person_id)
    person.get_registration_list()
    for registration in person.registration_list:
        registration.get_motor_policy_list()
    person.get_health_policy_list()
    return render_template('admin/view_person.html', person=person, functions=functions)


@app.route('/motor_insurance')
@app.route('/view_motor_policy/<policy_id>')
def view_motor_insurance_page(policy_id = None):
    if not session.get('logged_in'):
        return login_page()
    current_policy_id = policy_id
    current_policy_type = 'motor'
    return render_template('admin/insurance_renewal.html', current_policy_id=current_policy_id, current_policy_type=current_policy_type)


@app.route('/health_insurance')
@app.route('/view_health_policy/<policy_id>')
def view_health_insurance_page(policy_id = None):
    if not session.get('logged_in'):
        return login_page()
    current_policy_id = policy_id
    current_policy_type = 'health'
    return render_template('admin/insurance_renewal.html', current_policy_id=current_policy_id, current_policy_type=current_policy_type)
