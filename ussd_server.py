import os
import json
import urllib.request
import urllib.parse
import urllib.error
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

APPWRITE_PROJECT_ID = os.environ.get('APPWRITE_PROJECT_ID', '689107c288885e90c039')
APPWRITE_DATABASE_ID = os.environ.get('APPWRITE_DATABASE_ID', '6864aed388d20c69a461')
APPWRITE_API_KEY = os.environ.get('APPWRITE_API_KEY', '0f3a08c2c4fc98480980cbe59cd2db6b8522734081f42db3480ab2e7a8ffd7c46e8476a62257e429ff11c1d6616e814ae8753fb07e7058d1b669c641012941092ddcd585df802eb2313bfba49bf3ec3f776f529c09a7f5efef2988e4b4821244bbd25b3cd16669885c173ac023b5b8a90e4801f3584eef607506362c6ae01c94')
CUSTOMERS_COLLECTION_ID = os.environ.get('CUSTOMERS_COLLECTION_ID', 'customers')
APPWRITE_ENDPOINT = os.environ.get('APPWRITE_ENDPOINT', 'http://localhost/v1')

user_sessions = {}

def get_customer(phone_number):
    try:
        clean_phone = phone_number.replace('+254', '0') if phone_number.startswith('+254') else phone_number
        
        query = f'equal("phone_number","{phone_number}")'
        url = f'{APPWRITE_ENDPOINT}/databases/{APPWRITE_DATABASE_ID}/collections/{CUSTOMERS_COLLECTION_ID}/documents?queries[]={urllib.parse.quote(query)}'
        
        headers = {
            'X-Appwrite-Project': APPWRITE_PROJECT_ID,
            'X-Appwrite-Key': APPWRITE_API_KEY
        }
        
        request_obj = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request_obj, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if data.get('documents'):
            return data['documents'][0]
        
        return None
        
    except Exception as e:
        print(f"Error getting customer: {str(e)}")
        return None

def create_customer(phone_number):
    try:
        url = f'{APPWRITE_ENDPOINT}/databases/{APPWRITE_DATABASE_ID}/collections/{CUSTOMERS_COLLECTION_ID}/documents'
        
        customer_data = {
            'documentId': 'unique()',
            'data': {
                'phone_number': phone_number,
                'created_at': datetime.now().isoformat(),
                'registration_state': 'new',
                'is_registered': False,
                'credits': 0,
                'active': False
            }
        }
        
        headers = {
            'X-Appwrite-Project': APPWRITE_PROJECT_ID,
            'X-Appwrite-Key': APPWRITE_API_KEY,
            'Content-Type': 'application/json'
        }
        
        data = json.dumps(customer_data).encode('utf-8')
        request_obj = urllib.request.Request(url, data=data, headers=headers, method='POST')
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"Created customer: {phone_number}")
        return result
        
    except Exception as e:
        print(f"Error creating customer: {str(e)}")
        return None

def update_customer(customer_id, updates):
    try:
        url = f'{APPWRITE_ENDPOINT}/databases/{APPWRITE_DATABASE_ID}/collections/{CUSTOMERS_COLLECTION_ID}/documents/{customer_id}'
        
        payload = {'data': updates}
        headers = {
            'X-Appwrite-Project': APPWRITE_PROJECT_ID,
            'X-Appwrite-Key': APPWRITE_API_KEY,
            'Content-Type': 'application/json'
        }
        
        data = json.dumps(payload).encode('utf-8')
        request_obj = urllib.request.Request(url, data=data, headers=headers, method='PATCH')
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"Updated customer: {customer_id}")
        return result
        
    except Exception as e:
        print(f"Error updating customer: {str(e)}")
        return None

@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "")

    if session_id not in user_sessions:
        user_sessions[session_id] = {'state': 'main_menu', 'data': {}}
    
    session = user_sessions[session_id]
    customer = get_customer(phone_number)
    
    response = process_ussd_input(text, session, customer, phone_number)
    
    if response.startswith("END"):
        if session_id in user_sessions:
            del user_sessions[session_id]
    
    return response

def process_ussd_input(text, session, customer, phone_number):
    state = session['state']
    
    if text == '':
        return ("CON Welcome to Tusafishe Water Kiosk! 💧\n"
                "1. Register New Account\n"
                "2. Reactivate Account\n"
                "3. Check Account Status")
    
    if state == 'main_menu':
        if text == '1':
            if customer and customer.get('is_registered'):
                return "END You already have a registered account! Use option 2 to reactivate if needed."
            session['state'] = 'register_id'
            return "CON Registration Started!\nEnter your ID number:"
        elif text == '2':
            if not customer:
                return "END No account found for this number. Use option 1 to register."
            session['state'] = 'reactivate_pin'
            return "CON Account found! Enter your 4-digit PIN:"
        elif text == '3':
            if not customer:
                return "END No account found for this number."
            status = "Active" if customer.get('active') else "Inactive"
            registered = "Yes" if customer.get('is_registered') else "No"
            credits = customer.get('credits', 0)
            account_id = customer.get('account_id', 'N/A')
            return (f"END Account Status:\n"
                    f"ID: {account_id}\n"
                    f"Registered: {registered}\n"
                    f"Status: {status}\n"
                    f"Credits: {credits} KES")
        else:
            return "CON Invalid option. Please try again:\n1. Register\n2. Reactivate\n3. Check Status"
    
    elif state == 'register_id':
        if len(text.split('*')[-1]) >= 6:
            if not customer:
                customer = create_customer(phone_number)
            if customer:
                session['state'] = 'register_pin'
                session['data']['id_number'] = text.split('*')[-1]
                return "CON ID saved! ✅\nCreate a 4-digit PIN:"
            else:
                return "END Error creating account. Please try again later."
        else:
            return "CON Please enter a valid ID number (minimum 6 digits):"
    
    elif state == 'register_pin':
        pin = text.split('*')[-1]
        if len(pin) == 4 and pin.isdigit():
            session['state'] = 'register_confirm'
            session['data']['pin'] = pin
            return ("CON Confirm registration:\n"
                    f"ID: {session['data']['id_number']}\n"
                    f"PIN: {pin}\n"
                    "1. Confirm\n2. Cancel")
        else:
            return "CON Please enter exactly 4 digits for your PIN:"
    
    elif state == 'register_confirm':
        choice = text.split('*')[-1]
        if choice == '1':
            if customer:
                account_id = f"TSF{customer['$id'][-6:].upper()}"
                updates = {
                    'pin': session['data']['pin'],
                    'account_id': account_id,
                    'is_registered': True,
                    'active': True,
                    'registration_state': 'completed'
                }
                if update_customer(customer['$id'], updates):
                    return (f"END 🎉 Registration Complete!\n"
                            f"Account ID: {account_id}\n"
                            f"Your account is now active!")
                else:
                    return "END Registration failed. Please try again later."
            else:
                return "END Error completing registration. Please try again."
        elif choice == '2':
            return "END Registration cancelled."
        else:
            return "CON Invalid choice:\n1. Confirm registration\n2. Cancel"
    
    elif state == 'reactivate_pin':
        pin = text.split('*')[-1]
        if customer and customer.get('pin') == pin:
            if update_customer(customer['$id'], {'active': True}):
                account_id = customer.get('account_id', 'N/A')
                credits = customer.get('credits', 0)
                return (f"END ✅ Account Reactivated!\n"
                        f"Account ID: {account_id}\n"
                        f"Credits: {credits} KES\n"
                        f"Welcome back!")
            else:
                return "END Error reactivating account. Please try again."
        else:
            return "END Invalid PIN. Account reactivation failed."
    
    return "END Invalid input. Please try again."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))


