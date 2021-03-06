# Freelancer CRM

This an open source CRM web app for freelancer insurance agent to manage contacts, insurance policies and insurance
renewals.

[Live Demo](https://freelancer-crm.herokuapp.com/)

## Screeshots

* ### Login
  ![Login](Screenshots/Login.png?raw=true "Login")

* ### Contacts
  ![Contacts](Screenshots/Contacts.png?raw=true "Contacts")

* ### Manage Contact and Policy
  ![View_Contact](Screenshots/Contact_Profile.png?raw=true "View_Contact")

* ### Insurance Renewals
  ![Insruance_Renewals](Screenshots/Insurance_Renewals.png?raw=true "Insruance_Renewals")

## Requirements

Please install below requirements before installation

* [Python3](https://www.python.org/downloads/)
* [Google Chrome](https://www.google.com/chrome/) (OR Any Modern Browser)
* [MongoDB](https://www.mongodb.com/try/download/community)

## Installation

1. Open project folder in Terminal
    ```commandline
   cd /project path
   ```

1. Install required python packages in `requirements.txt` (pymongo, Flask, bcrypt, gunicorn, dnspython)

    ```commandline
   pip install -r requirements.txt
    ```

1. By default, MongoDB address is set to `mongodb://localhost` , To change address set environment variable `db_address`

1. Run Server
    ```commandline
   python3 run.py
   ```

1. Open [http://localhost:5000/](http://localhost:5000/) in Browser

## Developed using

* [PyCharm](https://www.jetbrains.com/pycharm/)

## Support Developer

If you like this project please support by giving star or give feedback

<a href="https://www.buymeacoffee.com/growupanand" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
