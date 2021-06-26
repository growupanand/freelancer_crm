from flask import request, session
from run import app, login_required
from bson import ObjectId
from bson.json_util import dumps
import models
from functions import get_user_id


@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    username = data['username']
    password = data['password']
    full_name = data['full_name']
    result = models.User().create_user(username=username, password=password, full_name=full_name)
    return dumps(result)


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data['username']
    password = data['password']
    result = models.User().login(username=username, password=password)
    return dumps(result)


@app.route('/api/add_contact', methods=['POST'])
@login_required
def api_add_contact():
    data = request.json
    source_type = data['source_type']
    source_name = data['source_name']
    full_name = data['full_name']
    mobile_number = data['mobile_number']
    email = data['email']
    result = models.User(get_user_id()).contact.create_contact(
        source_type=source_type,
        source_name=source_name,
        full_name=full_name,
        mobile_number=mobile_number,
        email=email
    )
    return dumps(result)


@app.route('/api/update_contact_details', methods=['POST'])
@login_required
def api_update_contact_details():
    data = request.json
    contact_id = ObjectId(data['contact_id'])
    source_type = data['source_type']
    source_name = data['source_name']
    full_name = data['full_name']
    email = data['email']
    mobile_numbers = data['mobile_numbers']
    user = models.User(get_user_id())
    user.Contact(contact_id)
    result = user.contact.update_contact_details(
        source_type=source_type,
        source_name=source_name,
        full_name=full_name,
        email=email,
        mobile_numbers=mobile_numbers
    )
    return dumps(result)


@app.route('/api/delete_contact', methods=['POST'])
@login_required
def api_delete_contact():
    data = request.json
    contact_id = ObjectId(data['contact_id'])
    user = models.User(get_user_id())
    user.Contact(contact_id)
    result = user.contact.delete_contact()
    return dumps(result)


@app.route('/api/add_vehicle', methods=['POST'])
@login_required
def api_add_vehicle():
    data = request.json
    contact_id = ObjectId(data['contact_id'])
    registration_number = data['registration_number']
    registration_name = data['registration_name']
    registration_date = data['registration_date']
    vehicle_company = data['vehicle_company']
    other_vehicle_company = data['other_vehicle_company']
    vehicle_model = data['vehicle_model']
    other_vehicle_model = data['other_vehicle_model']
    vehicle_cc = data['vehicle_cc']
    vehicle_mfg = data['vehicle_mfg']
    vehicle_fuel_type = data['vehicle_fuel_type']
    user = models.User(get_user_id())
    user.Contact(contact_id)
    # check if vehicle company is new company
    if vehicle_company == 'other_vehicle_company':
        vehicle_company = other_vehicle_company
        # add new company in database
        user.contact.vehicle.create_vehicle_company(vehicle_company)
    # check if vehicle model is new model
    if vehicle_model == 'other_vehicle_model':
        vehicle_model = other_vehicle_model
        # add new model in database
        user.contact.vehicle.create_vehicle_model(vehicle_company, vehicle_model)
    result = user.contact.vehicle.create_vehicle(
        registration_number=registration_number,
        registration_date=registration_date,
        registration_name=registration_name,
        vehicle_company=vehicle_company,
        vehicle_model=vehicle_model,
        vehicle_cc=vehicle_cc,
        vehicle_mfg=vehicle_mfg,
        vehicle_fuel_type=vehicle_fuel_type
    )
    return dumps(result)


@app.route('/api/get_vehicle_details', methods=['POST'])
@login_required
def api_get_vehicle_details():
    data = request.json
    vehicle_id = ObjectId(data['vehicle_id'])
    user = models.User(get_user_id())
    user.contact.Vehicle(vehicle_id)
    result = user.contact.vehicle.get_vehicle_details()
    return dumps(result)


@app.route('/api/update_vehicle_details', methods=['POST'])
@login_required
def api_update_vehicle_details():
    data = request.json
    vehicle_id = ObjectId(data['vehicle_id'])
    contact_id = ObjectId(data['contact_id'])
    registration_number = data['registration_number']
    registration_name = data['registration_name']
    registration_date = data['registration_date']
    vehicle_company = data['vehicle_company']
    other_vehicle_company = data['other_vehicle_company']
    vehicle_model = data['vehicle_model']
    other_vehicle_model = data['other_vehicle_model']
    vehicle_cc = data['vehicle_cc']
    vehicle_mfg = data['vehicle_mfg']
    vehicle_fuel_type = data['vehicle_fuel_type']
    user = models.User(get_user_id())
    user.Contact(contact_id)
    user.contact.Vehicle(vehicle_id)
    # check if vehicle company is new company
    if vehicle_company == 'other_vehicle_company':
        vehicle_company = other_vehicle_company
        # add new company in database
        user.contact.vehicle.create_vehicle_company(vehicle_company)
    # check if vehicle model is new model
    if vehicle_model == 'other_vehicle_model':
        vehicle_model = other_vehicle_model
        # add new model in database
        user.contact.vehicle.create_vehicle_model(vehicle_company, vehicle_model)
    result = user.contact.vehicle.update_vehicle_details(
        registration_number=registration_number,
        registration_date=registration_date,
        registration_name=registration_name,
        vehicle_company=vehicle_company,
        vehicle_model=vehicle_model,
        vehicle_cc=vehicle_cc,
        vehicle_mfg=vehicle_mfg,
        vehicle_fuel_type=vehicle_fuel_type
    )
    return dumps(result)


@app.route('/api/delete_vehicle', methods=['POST'])
@login_required
def api_delete_vehicle():
    data = request.json
    vehicle_id = ObjectId(data['vehicle_id'])
    user = models.User(get_user_id())
    user.contact.Vehicle(vehicle_id)
    result = user.contact.vehicle.delete_vehicle()
    return dumps(result)


@app.route('/api/add_vehicle_policy', methods=['POST'])
@login_required
def api_add_vehicle_policy():
    data = request.json
    vehicle_id = ObjectId(data['vehicle_id'])
    own_business = data['own_business']
    expiry_date = data['expiry_date']
    policy_number = data['policy_number']
    cover_type = data['cover_type']
    addon_covers = data['addon_covers']
    insurance_company = data['insurance_company']
    other_insurance_company = data['other_insurance_company']
    idv = data['idv']
    ncb = data['ncb']
    premium = data['premium']
    payout = data['payout']
    discount = data['discount']
    user = models.User(get_user_id())
    user.contact.Vehicle(vehicle_id)
    # check if insurance company is new company
    if insurance_company == 'other_insurance_company':
        insurance_company = other_insurance_company
        user.contact.vehicle.policy.create_insurance_company(insurance_company)
    result = user.contact.vehicle.policy.create_policy(expiry_date=expiry_date, own_business=own_business,
                                                       policy_number=policy_number, cover_type=cover_type,
                                                       addon_covers=addon_covers,
                                                       insurance_company=insurance_company, idv=idv, ncb=ncb,
                                                       premium=premium,
                                                       payout=payout, discount=discount)
    return dumps(result)


@app.route('/api/get_vehicle_policy_details', methods=['POST'])
@login_required
def api_get_vehicle_policy_details():
    data = request.json
    policy_id = ObjectId(data['policy_id'])
    user = models.User(get_user_id())
    user.contact.vehicle.Policy(policy_id)
    result = user.contact.vehicle.policy.get_policy_details()
    return dumps(result)


@app.route('/api/update_vehicle_policy_details', methods=['POST'])
@login_required
def api_update_vehicle_policy_details():
    data = request.json
    policy_id = ObjectId(data['policy_id'])
    own_business = data['own_business']
    expiry_date = data['expiry_date']
    policy_number = data['policy_number']
    cover_type = data['cover_type']
    addon_covers = data['addon_covers']
    insurance_company = data['insurance_company']
    other_insurance_company = data['other_insurance_company']
    idv = data['idv']
    ncb = data['ncb']
    premium = data['premium']
    payout = data['payout']
    discount = data['discount']
    user = models.User(get_user_id())
    user.contact.vehicle.Policy(policy_id)
    # check if insurance company is new company
    if insurance_company == 'other_insurance_company':
        insurance_company = other_insurance_company
        user.contact.vehicle.policy.create_insurance_company(insurance_company)
    result = user.contact.vehicle.policy.update_policy(expiry_date=expiry_date, own_business=own_business,
                                                       policy_number=policy_number, cover_type=cover_type,
                                                       addon_covers=addon_covers,
                                                       insurance_company=insurance_company, idv=idv, ncb=ncb,
                                                       premium=premium,
                                                       payout=payout, discount=discount)
    return dumps(result)


@app.route('/api/delete_vehicle_policy', methods=['POST'])
@login_required
def api_delete_vehicle_policy():
    data = request.json
    policy_id = ObjectId(data['policy_id'])
    user = models.User(get_user_id())
    user.contact.vehicle.Policy(policy_id)
    result = user.contact.vehicle.policy.delete_policy()
    return dumps(result)


@app.route('/api/get_renewals', methods=['POST'])
def api_get_renewals():
    data = request.json
    month = data['month']
    year = data['year']
    user = models.User(get_user_id())
    renewals = user.contact.vehicle.policy.get_renewals(month, year)
    return dumps(renewals)


@app.route('/api/get_renewal_details', methods=['POST'])
@login_required
def api_get_renewal_details():
    data = request.json
    policy_id = ObjectId(data['policy_id'])
    user = models.User(get_user_id())
    user.contact.vehicle.Policy(policy_id)
    result = user.contact.vehicle.policy.get_renewal_details()
    return dumps(result)


@app.route('/api/post_policy_followup', methods=['POST'])
@login_required
def api_post_policy_followup():
    data = request.json
    policy_id = ObjectId(data['policy_id'])
    remark = data['remark']
    user = models.User(get_user_id())
    user.contact.vehicle.Policy(policy_id)
    result = user.contact.vehicle.policy.post_followup(remark)
    return dumps(result)


@app.route('/api/add_renewal_policy', methods=['POST'])
@login_required
def api_add_renewal_policy():
    data = request.json
    policy_id = ObjectId(data['policy_id'])
    own_business = data['own_business']
    expiry_date = data['expiry_date']
    policy_number = data['policy_number']
    cover_type = data['cover_type']
    addon_covers = data['addon_covers']
    insurance_company = data['insurance_company']
    other_insurance_company = data['other_insurance_company']
    idv = data['idv']
    ncb = data['ncb']
    premium = data['premium']
    payout = data['payout']
    discount = data['discount']
    user = models.User(get_user_id())
    user.contact.vehicle.Policy(policy_id)
    # check if insurance company is new company
    if insurance_company == 'other_insurance_company':
        insurance_company = other_insurance_company
        user.contact.vehicle.policy.create_insurance_company(insurance_company)
    result = user.contact.vehicle.policy.renew_policy(expiry_date=expiry_date, own_business=own_business,
                                                       policy_number=policy_number, cover_type=cover_type,
                                                       addon_covers=addon_covers,
                                                       insurance_company=insurance_company, idv=idv, ncb=ncb,
                                                       premium=premium,
                                                       payout=payout, discount=discount)
    return dumps(result)


@app.route('/api/add_insurance_company', methods=['POST'])
@login_required
def api_add_insurance_company():
    data = request.json
    company_name = data['company_name']
    user = models.User(get_user_id())
    result = user.contact.vehicle.policy.create_insurance_company(company_name)
    return dumps(result)


@app.route('/api/delete_insurance_company', methods=['POST'])
@login_required
def api_delete_insurance_company():
    data = request.json
    company_id = ObjectId(data['company_id'])
    user = models.User(get_user_id())
    result = user.contact.vehicle.policy.delete_insurance_company(company_id)
    return dumps(result)


@app.route('/api/add_vehicle_company', methods=['POST'])
@login_required
def api_add_vehicle_company():
    data = request.json
    company_name = data['company_name']
    user = models.User(get_user_id())
    result = user.contact.vehicle.create_vehicle_company(company_name)
    return dumps(result)


@app.route('/api/get_vehicle_company_details', methods=['POST'])
@login_required
def api_get_vehicle_company_details():
    data = request.json
    company_id = ObjectId(data['company_id'])
    user = models.User(get_user_id())
    result = user.contact.vehicle.get_vehicle_company_details(company_id)
    return dumps(result)


@app.route('/api/add_vehicle_company_model', methods=['POST'])
@login_required
def api_add_vehicle_company_model():
    data = request.json
    company_name = data['company_name']
    model_name = data['model_name']
    user = models.User(get_user_id())
    result = user.contact.vehicle.create_vehicle_model(company_name, model_name)
    return dumps(result)


@app.route('/api/delete_vehicle_company_model', methods=['POST'])
@login_required
def api_delete_vehicle_company_model():
    data = request.json
    company_id = ObjectId(data['company_id'])
    model_name = data['model_name']
    user = models.User(get_user_id())
    result = user.contact.vehicle.delete_vehicle_company_model(company_id, model_name)
    return dumps(result)


@app.route('/api/delete_vehicle_company', methods=['POST'])
@login_required
def api_delete_vehicle_company():
    data = request.json
    company_id = ObjectId(data['company_id'])
    user = models.User(get_user_id())
    result = user.contact.vehicle.delete_vehicle_company(company_id)
    return dumps(result)