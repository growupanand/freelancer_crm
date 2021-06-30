from flask import render_template, session, redirect
from freelancer import app, login_required, models
from bson import ObjectId
from freelancer.functions import get_user_id
from datetime import datetime



@app.route('/login')
def login():
    if 'logged_in' in session:
        return redirect('/')
    return render_template("login.html")


@app.route('/logout')
def logout():
    models.User().logout()
    return redirect('/')


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/')
@login_required
def index():
    return render_template('crm/home.html', session=session)


@app.route('/contacts')
@login_required
def contacts():
    contacts = models.User(get_user_id()).contact.get_contacts()['data']
    return render_template('crm/contacts.html', session=session, contacts=contacts)


@app.route('/contacts/<contact_id>')
@login_required
def view_contact(contact_id):
    user = models.User(get_user_id())
    user.Contact(ObjectId(contact_id))
    contact = user.contact.get_contact_details()
    if contact['result']:
        contact_data = user.contact.data
        vehicle_companies = list(user.contact.vehicle.get_vehicle_companies()['data'])
        vehicle_company_list = {}
        for company in vehicle_companies:
            if 'models' in company:
                vehicle_company_list[company['company_name']] = company['models']
        insurance_companies = list(user.contact.vehicle.policy.get_insurance_companies()['data'])
        vehicles = list(user.contact.vehicle.get_vehicles()['data'].sort('created', -1))
        # add vehicle insurance policies
        for i in range(len(vehicles)):
            user.contact.Vehicle(vehicles[i]['_id'])
            policies = list(user.contact.vehicle.policy.get_policies()['data'].sort('expiry_date', -1))
            vehicles[i]['policies'] = policies
        return render_template('crm/view_contact.html', session=session, contact=contact_data,
                               vehicle_companies=vehicle_companies, vehicle_company_list=vehicle_company_list,
                               vehicles=vehicles, insurance_companies=insurance_companies)
    return contact['msg']


@app.route('/insurance_renewals')
@app.route('/insurance_renewals/<policy_id>')
@login_required
def insurance_renewals(policy_id=None):
    current_policy_id = '' if policy_id is None else policy_id
    user = models.User(get_user_id())
    today = datetime.utcnow()
    policy_list = []
    for policy in user.contact.vehicle.policy.get_renewals(today.month, today.year)['data']:
        policy_list.append(policy)
    insurance_companies = list(user.contact.vehicle.policy.get_insurance_companies()['data'])
    return render_template('crm/insurance_renewals.html', current_policy_id=current_policy_id, policy_list=policy_list, today=today,
                           insurance_companies=insurance_companies)


@app.route('/manage_insurance_companies')
@login_required
def manage_insurance_companies_page():
    user = models.User(get_user_id())
    company_list = list(user.contact.vehicle.policy.get_insurance_companies()['data'])
    return render_template('crm/manage_insurance_companies.html', company_list=company_list)

@app.route('/manage_vehicle_companies')
@login_required
def manage_vehicle_companies_page():
    user = models.User(get_user_id())
    company_list = list(user.contact.vehicle.get_vehicle_companies()['data'])
    return render_template('crm/manage_vehicle_companies.html', company_list=company_list)
