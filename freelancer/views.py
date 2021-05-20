from freelancer import app, render_template, session, db, functions, models, redirect, url_for
from bson import ObjectId
from datetime import datetime

active_page = {
    'contacts': None,
    'motor_renewal' : None
}

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
            user_id = ObjectId(session['user']['_id'])
            if session['user']['type'] == 'admin':
                today = datetime.today()
                day = today.day
                month = today.month
                year = today.year
                motor_renewal_list = models.Policy_motor().get_renewal_list(month, year)
                policy_list_expiry_today = []
                for policy in motor_renewal_list:
                    if policy['day'] == day:
                        policy['type'] = 'motor'
                        policy_list_expiry_today.append(policy)
                motor_renewal_count = {'total':0, 'not_touch':0, 'followup':0, 'won':0, 'lost':0}
                for policy in motor_renewal_list:
                    motor_renewal_count['total'] += 1
                    if 'policy_status' in policy:
                        motor_renewal_count[policy['policy_status']] += 1
                    else:
                        motor_renewal_count['not_touch'] +=1
                health_renewal_list = models.Policy_health().get_renewal_list(month, year)
                for policy in health_renewal_list:
                    if policy['day'] == day:
                        policy['type'] = 'health'
                        policy_list_expiry_today.append(policy)
                health_renewal_count = {'total': 0, 'not_touch': 0, 'followup': 0, 'won': 0, 'lost': 0}
                for policy in health_renewal_list:
                    health_renewal_count['total'] += 1
                    if 'policy_status' in policy:
                        health_renewal_count[policy['policy_status']] += 1
                    else:
                        health_renewal_count['not_touch'] += 1
                return render_template('admin/index.html', motor_renewal_count=motor_renewal_count, health_renewal_count=health_renewal_count, policy_list_expiry_today=policy_list_expiry_today)
    return render_template('login.html')


@app.route('/contacts')
def admin_contacts_page():
    if not session.get('logged_in'):
        return login_page()
    recent_added = models.Person().get().limit(10).sort('_id', -1)
    active_page['contacts'] = 'active'
    return render_template('admin/contacts.html', recent_added=recent_added, functions=functions)


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
def view_motor_insurance_page():
    if not session.get('logged_in'):
        return login_page()
    today = datetime.today()
    day = today.day
    month = today.month
    current_period = today.strftime("%B %Y")
    year = today.year
    renewal_list = models.Policy_motor().get_renewal_list(month, year)
    policy_list_expiry_today = []
    for policy in renewal_list:
        if policy['day'] == day:
            policy_list_expiry_today.append(policy)
    renewal_count = {'total': 0, 'not_touch': 0, 'followup': 0, 'won': 0, 'lost': 0}
    for policy in renewal_list:
        renewal_count['total'] += 1
        if 'policy_status' in policy:
            if policy['policy_status'] is not None:
                renewal_count[policy['policy_status']] += 1
        else:
            renewal_count['not_touch'] += 1
    return render_template('admin/motor_insurance.html', policy_list_expiry_today=policy_list_expiry_today, renewal_count=renewal_count, current_period=current_period)


@app.route('/manage_motor_insurance_companies')
def view_manage_motor_insurance_companies_page():
    if not session.get('logged_in'):
        return login_page()
    user_id = ObjectId(session['user']['_id'])
    company_list = models.user(user_id).get_motor_insurance_company_list()
    return render_template('admin/manage_motor_insurance_companies.html', company_list=company_list)

@app.route('/motor_insurance_renewals')
@app.route('/view_motor_policy/<policy_id>')
def view_motor_insurance_policy_page(policy_id = None):
    if not session.get('logged_in'):
        return login_page()
    current_policy_id = policy_id
    return render_template('admin/view_motor_renewals.html', current_policy_id=current_policy_id)


@app.route('/health_insurance')
@app.route('/view_health_policy/<policy_id>')
def view_health_insurance_page(policy_id = None):
    if not session.get('logged_in'):
        return login_page()
    current_policy_id = policy_id
    current_policy_type = 'health'
    return render_template('admin/insurance_renewal.html', current_policy_id=current_policy_id, current_policy_type=current_policy_type)


@app.route('/manage_vehicles')
def view_manage_vehicles_page():
    if not session.get('logged_in'):
        return login_page()
    return render_template('admin/manage_vehicles.html')


@app.route('/manage_vehicle/<vehicle_id>')
def view_manage_vehicles_models_page(vehicle_id):
    if not session.get('logged_in'):
        return login_page()
    user_id = ObjectId(session['user']['_id'])
    vehicle = models.vehicle(ObjectId(vehicle_id))
    return render_template('admin/manage_vehicle_models.html', vehicle=vehicle)

