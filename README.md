# Freelancer CRM
This an open source CRM for freelancer agent to manage contacts and insurance policies.

Try Working Demo [https://freelancer-crm.herokuapp.com/](https://freelancer-crm.herokuapp.com/)

---

## Features

* ### Contacts
  ![Contacts](Docs/Screenshots/Contacts.png?raw=true "Optional Title")

* ### Manage Contact and Policy
  ![View_Contact](Docs/Screenshots/View Contact.png?raw=true "Optional Title")

* ### Insurance Renewals
  ![Insruance_Renewals](Docs/Screenshots/Insurance Renewals.png?raw=true "Optional Title")



## Requirements

* Python3
* Chrome Browser (or you can try any modern browser)
* MongoDB


## Setup Freelancer CRM

1. Open project folder in Terminal
    ```commandline
   cd /project path
   ```

1. Install required python packages in requirements.txt
    ```commandline
   pip install -r requirements.txt
    ```

1. Setup Database
    * Install [MongoDB server](https://www.mongodb.com/try/download/community) on local machine
    * Write MongoDB server address in ```/freelancer/db.py```
   ```python
   client = pymongo.MongoClient("mongodb://localhost",27017)
   ```

1. Run server
    ```commandline
   python3 run.py
   ```

1. Open [http://localhost:5000/](http://localhost:5000/) in Chrome Browser

---

# Software Used
[PyCharm](https://www.jetbrains.com/pycharm/)

# Support
If you like this project please support by giving star or give feedback
