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
    for i in db.persons_collection.find().sort('_id', -1).limit(20):
        i['_id'] = str(i['_id'])
        persons_list.append(i)
    return render_template('admin/crm.html', persons_list=persons_list)


@app.route('/crm/view_person/<_id>')
def view_person_page(_id):
    person = db.persons_collection.find_one({'_id':ObjectId(_id)})
    person['vehicle_policy'] = db.motor_policy_collection.find({'person_id':person['_id']}, {'policy_number':1})
    person['_id'] = str(person['_id'])
    return render_template('admin/view_person.html', person=person)


@app.route('/insurance')
def view_insurance_page():
    return render_template('admin/insurance.html')

from . import api_views