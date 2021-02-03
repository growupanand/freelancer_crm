from freelancer import app, render_template, session, db, functions, models, redirect, url_for
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services_page():
    return render_template('services.html')

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

# <CRM VIEWS

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
    person = db.persons_collection.find_one({'_id':ObjectId(_id)})
    person['vehicles'] = []
    q = db.motor_registration_collection.find({'person_id':person['_id']})
    for i in q:
        d = i['registration_date']
        if not d in (None, ''):
            i['registration_date'] = functions.format_timestamp(d, '%d-%m-%Y')
        i['policy_list'] = []
        q1 = db.motor_policy_collection.find({'registration_id':i['_id']})
        for i1 in q1:
            d = i1['expiry_date']
            i1['expiry_date'] = functions.format_timestamp(d, '%d-%m-%Y')
            i['policy_list'].append(i1)
        person['vehicles'].append(i)
    person['_id'] = str(person['_id'])
    for field in ('source_type', 'source_data'):
        person[field] = None if not field in person else person[field]
    return render_template('admin/view_person.html', person=person)


@app.route('/motor_insurance')
@app.route('/view_policy/<policy_id>')
def view_insurance_page(policy_id = None):
    if not session.get('logged_in'):
        return login_page()
    return render_template('admin/motor_insurance.html', policy_id=policy_id)

from . import api_views