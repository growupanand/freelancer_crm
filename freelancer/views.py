from freelancer import app, render_template, session, db, functions
from bson import ObjectId
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

@app.route('/crm')
def admin_crm_page():
    persons_list = []
    for i in db.persons_collection.find().sort('_id', -1).limit(10):
        i['_id'] = str(i['_id'])
        persons_list.append(i)
    return render_template('admin/crm.html', persons_list=persons_list)


@app.route('/crm/view_person/<_id>')
def view_person_page(_id):
    person = db.persons_collection.find_one({'_id':ObjectId(_id)})
    person['vehicles'] = []
    q = db.motor_registration_collection.find({'person_id':person['_id']})
    for i in q:
        d = i['registration_date']
        if not d == None:
            i['registration_date'] = functions.format_timestamp(d, '%d-%m-%Y')
        i['policy_list'] = []
        q1 = db.motor_policy_collection.find({'registration_id':i['_id']})
        for i1 in q1:
            d = i1['expiry_date']
            i1['expiry_date'] = functions.format_timestamp(d, '%d-%m-%Y')
            i['policy_list'].append(i1)
        person['vehicles'].append(i)
    person['_id'] = str(person['_id'])
    return render_template('admin/view_person.html', person=person)


@app.route('/motor_insurance')
@app.route('/view_policy/<policy_id>')
def view_insurance_page(policy_id = None):
    return render_template('admin/motor_insurance.html', policy_id=policy_id)

from . import api_views