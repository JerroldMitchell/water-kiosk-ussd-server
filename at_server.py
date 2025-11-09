import os
import json
import urllib.request
import urllib.parse
import urllib.error
from flask import Flask, request
from datetime import datetime
import time
import uuid
import base64

app = Flask(__name__)

# Appwrite Configuration
APPWRITE_PROJECT_ID = os.environ.get('APPWRITE_PROJECT_ID', '689107c288885e90c039')
APPWRITE_DATABASE_ID = os.environ.get('APPWRITE_DATABASE_ID', '6864aed388d20c69a461')
APPWRITE_API_KEY = os.environ.get('APPWRITE_API_KEY', '0f3a08c2c4fc98480980cbe59cd2db6b8522734081f42db3480ab2e7a8ffd7c46e8476a62257e429ff11c1d6616e814ae8753fb07e7058d1b669c641012941092ddcd585df802eb2313bfba49bf3ec3f776f529c09a7f5efef2988e4b4821244bbd25b3cd16669885c173ac023b5b8a90e4801f3584eef607506362c6ae01c94')
CUSTOMERS_COLLECTION_ID = os.environ.get('CUSTOMERS_COLLECTION_ID', 'customers')
APPWRITE_ENDPOINT = os.environ.get('APPWRITE_ENDPOINT', 'http://localhost/v1')

# Africa's Talking Configuration
AFRICAS_TALKING_API_KEY = os.environ.get('AFRICAS_TALKING_API_KEY', '')
AFRICAS_TALKING_USERNAME = os.environ.get('AFRICAS_TALKING_USERNAME', 'sandbox')

# MTN Mobile Money Configuration
MTN_MOMO_SUBSCRIPTION_KEY = os.environ.get('MTN_MOMO_SUBSCRIPTION_KEY', '')
MTN_MOMO_API_USER = os.environ.get('MTN_MOMO_API_USER', '')
MTN_MOMO_API_KEY = os.environ.get('MTN_MOMO_API_KEY', '')
MTN_MOMO_ENDPOINT = os.environ.get('MTN_MOMO_ENDPOINT', 'https://sandbox.momodeveloper.mtn.com')
MTN_MOMO_TARGET_ENVIRONMENT = os.environ.get('MTN_MOMO_TARGET_ENVIRONMENT', 'sandbox')

# Airtel Money Configuration
AIRTEL_CLIENT_ID = os.environ.get('AIRTEL_CLIENT_ID', '')
AIRTEL_CLIENT_SECRET = os.environ.get('AIRTEL_CLIENT_SECRET', '')
AIRTEL_PUBLIC_KEY = os.environ.get('AIRTEL_PUBLIC_KEY', '')
AIRTEL_ENDPOINT = os.environ.get('AIRTEL_ENDPOINT', 'https://openapiuat.airtel.africa')
AIRTEL_COUNTRY_CODE = os.environ.get('AIRTEL_COUNTRY_CODE', 'UG')
AIRTEL_CURRENCY_CODE = os.environ.get('AIRTEL_CURRENCY_CODE', 'UGX')

# Semester Configuration
SEMESTER_END_DATE = os.environ.get('SEMESTER_END_DATE', '2025-12-20')

# Session management for USSD
user_sessions = {}

# =============================================================================
# SHARED DATABASE FUNCTIONS
# =============================================================================

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

def send_sms(phone_number, message):
    try:
        if not AFRICAS_TALKING_API_KEY:
            print(f"TEST MODE: Would send to {phone_number}: {message}")
            return {'success': True, 'test_mode': True}

        if not phone_number.startswith('+'):
            if phone_number.startswith('0'):
                phone_number = '+254' + phone_number[1:]
            else:
                phone_number = '+254' + phone_number

        url = "https://api.africastalking.com/version1/messaging"
        data = urllib.parse.urlencode({
            'username': AFRICAS_TALKING_USERNAME,
            'to': phone_number,
            'message': message
        }).encode('utf-8')

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'apikey': AFRICAS_TALKING_API_KEY
        }

        request_obj = urllib.request.Request(url, data=data, headers=headers)
        response = urllib.request.urlopen(request_obj, timeout=15)
        result = json.loads(response.read().decode('utf-8'))

        print(f"✅ SMS sent to {phone_number}")
        return {'success': True, 'sms_result': result}

    except Exception as e:
        print(f"SMS failed: {str(e)}")
        return {'success': False, 'error': str(e)}

# =============================================================================
# MTN MOBILE MONEY PAYMENT FUNCTIONS
# =============================================================================

def get_mtn_access_token():
    """
    Generate MTN Mobile Money access token for API authentication
    
    Returns:
        str: Bearer token or None if failed
    """
    try:
        if not MTN_MOMO_API_USER or not MTN_MOMO_API_KEY:
            print("MTN MoMo credentials not configured")
            return None
            
        url = f"{MTN_MOMO_ENDPOINT}/collection/token/"
        
        # Create basic auth header
        credentials = f"{MTN_MOMO_API_USER}:{MTN_MOMO_API_KEY}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Ocp-Apim-Subscription-Key': MTN_MOMO_SUBSCRIPTION_KEY,
            'X-Target-Environment': MTN_MOMO_TARGET_ENVIRONMENT
        }
        
        request_obj = urllib.request.Request(url, headers=headers, method='POST')
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        return result.get('access_token')
        
    except Exception as e:
        print(f"Failed to get MTN access token: {str(e)}")
        return None

def initiate_mtn_payment(phone_number, amount, currency_code='EUR', metadata=None):
    """
    Initiate a payment request using MTN Mobile Money RequestToPay API
    
    Args:
        phone_number: Customer phone number (format: 256XXXXXXXXX for Uganda)
        amount: Payment amount (string)
        currency_code: Currency (EUR for sandbox, UGX for production)
        metadata: Additional payment data (customer_id, etc.)
    
    Returns:
        dict: Payment response with transaction_id or error
    """
    try:
        if not MTN_MOMO_SUBSCRIPTION_KEY:
            print(f"TEST MODE: Would initiate ${amount} MTN payment from {phone_number}")
            return {
                'success': True,
                'test_mode': True,
                'transaction_id': f'TEST_MTN_{phone_number[-4:]}_{amount}',
                'status': 'PENDING'
            }

        # Get access token
        access_token = get_mtn_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to authenticate with MTN'}

        # Normalize phone number for MTN (Uganda format: 256XXXXXXXXX)
        if phone_number.startswith('+256'):
            phone_number = phone_number[1:]  # Remove +
        elif phone_number.startswith('0'):
            phone_number = '256' + phone_number[1:]  # Convert 0XXXXXXXXX to 256XXXXXXXXX
        elif not phone_number.startswith('256'):
            phone_number = '256' + phone_number  # Add country code

        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        url = f"{MTN_MOMO_ENDPOINT}/collection/v1_0/requesttopay"
        
        payload = {
            'amount': str(amount),
            'currency': currency_code,
            'externalId': transaction_id,
            'payer': {
                'partyIdType': 'MSISDN',
                'partyId': phone_number
            },
            'payerMessage': 'Tusafishe Water Kiosk Semester Payment',
            'payeeNote': f'Water access payment for {phone_number}'
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Reference-Id': transaction_id,
            'X-Target-Environment': MTN_MOMO_TARGET_ENVIRONMENT,
            'Ocp-Apim-Subscription-Key': MTN_MOMO_SUBSCRIPTION_KEY,
            'Content-Type': 'application/json'
        }

        data = json.dumps(payload).encode('utf-8')
        request_obj = urllib.request.Request(url, data=data, headers=headers, method='POST')
        response = urllib.request.urlopen(request_obj, timeout=30)
        
        print(f"✅ MTN payment request sent for {phone_number}: ${amount}")
        return {
            'success': True,
            'transaction_id': transaction_id,
            'status': 'PENDING',
            'phone_number': phone_number
        }

    except Exception as e:
        print(f"MTN payment initiation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def check_mtn_payment_status(transaction_id):
    """
    Check the status of an MTN Mobile Money payment
    
    Args:
        transaction_id: The transaction ID from initiate_mtn_payment
    
    Returns:
        dict: Payment status information
    """
    try:
        access_token = get_mtn_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to authenticate with MTN'}
            
        url = f"{MTN_MOMO_ENDPOINT}/collection/v1_0/requesttopay/{transaction_id}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Target-Environment': MTN_MOMO_TARGET_ENVIRONMENT,
            'Ocp-Apim-Subscription-Key': MTN_MOMO_SUBSCRIPTION_KEY
        }
        
        request_obj = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        return {
            'success': True,
            'status': result.get('status'),
            'amount': result.get('amount'),
            'currency': result.get('currency'),
            'financial_transaction_id': result.get('financialTransactionId'),
            'external_id': result.get('externalId')
        }
        
    except Exception as e:
        print(f"Failed to check MTN payment status: {str(e)}")
        return {'success': False, 'error': str(e)}

def activate_semester_access(customer_id, transaction_id):
    """
    Activate semester access after successful payment
    
    Args:
        customer_id: Customer document ID
        transaction_id: Payment transaction ID
        
    Returns:
        bool: Success status
    """
    try:
        updates = {
            'active': True,
            'payment_date': str(int(time.time()))
        }
        
        result = update_customer(customer_id, updates)
        if result:
            print(f"✅ Semester access activated for customer {customer_id}")
            return True
        else:
            print(f"❌ Failed to activate access for customer {customer_id}")
            return False
            
    except Exception as e:
        print(f"Error activating semester access: {str(e)}")
        return False

# =============================================================================
# AIRTEL MONEY PAYMENT FUNCTIONS  
# =============================================================================

def get_airtel_access_token():
    """
    Generate Airtel Money access token for API authentication
    
    Returns:
        str: Bearer token or None if failed
    """
    try:
        if not AIRTEL_CLIENT_ID or not AIRTEL_CLIENT_SECRET:
            print("Airtel Money credentials not configured")
            return None
            
        url = f"{AIRTEL_ENDPOINT}/auth/oauth2/token"
        
        payload = {
            'client_id': AIRTEL_CLIENT_ID,
            'client_secret': AIRTEL_CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*'
        }
        
        data = json.dumps(payload).encode('utf-8')
        request_obj = urllib.request.Request(url, data=data, headers=headers, method='POST')
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        return result.get('access_token')
        
    except Exception as e:
        print(f"Failed to get Airtel access token: {str(e)}")
        return None

def initiate_airtel_payment(phone_number, amount, currency_code='UGX', metadata=None):
    """
    Initiate a payment request using Airtel Money API
    
    Args:
        phone_number: Customer phone number (format: 07XXXXXXXX or 7XXXXXXXX for Uganda)
        amount: Payment amount (string)
        currency_code: Currency (UGX for Uganda)
        metadata: Additional payment data (customer_id, etc.)
    
    Returns:
        dict: Payment response with transaction_id or error
    """
    try:
        if not AIRTEL_CLIENT_ID:
            print(f"TEST MODE: Would initiate ${amount} Airtel payment from {phone_number}")
            return {
                'success': True,
                'test_mode': True,
                'transaction_id': f'TEST_AIRTEL_{phone_number[-4:]}_{amount}',
                'status': 'PENDING'
            }

        # Get access token
        access_token = get_airtel_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to authenticate with Airtel'}

        # Normalize phone number for Airtel (Uganda format: 07XXXXXXXX without country code)
        if phone_number.startswith('+256'):
            phone_number = '0' + phone_number[4:]  # +256781234567 -> 0781234567
        elif phone_number.startswith('256'):
            phone_number = '0' + phone_number[3:]  # 256781234567 -> 0781234567
        elif not phone_number.startswith('0'):
            phone_number = '0' + phone_number  # 781234567 -> 0781234567

        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        url = f"{AIRTEL_ENDPOINT}/openapi/moneytransfer/v2/validate"
        
        payload = {
            "reference": transaction_id,
            "subscriber": {
                "country": AIRTEL_COUNTRY_CODE,
                "currency": currency_code,
                "msisdn": phone_number
            },
            "transaction": {
                "amount": str(amount),
                "country": AIRTEL_COUNTRY_CODE,
                "currency": currency_code,
                "id": transaction_id
            }
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'X-Country': AIRTEL_COUNTRY_CODE,
            'X-Currency': currency_code
        }

        data = json.dumps(payload).encode('utf-8')
        request_obj = urllib.request.Request(url, data=data, headers=headers, method='POST')
        response = urllib.request.urlopen(request_obj, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"✅ Airtel payment request sent for {phone_number}: ${amount}")
        return {
            'success': True,
            'transaction_id': transaction_id,
            'status': 'PENDING',
            'phone_number': phone_number,
            'airtel_response': result
        }

    except Exception as e:
        print(f"Airtel payment initiation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def check_airtel_payment_status(transaction_id):
    """
    Check the status of an Airtel Money payment
    
    Args:
        transaction_id: The transaction ID from initiate_airtel_payment
    
    Returns:
        dict: Payment status information
    """
    try:
        access_token = get_airtel_access_token()
        if not access_token:
            return {'success': False, 'error': 'Failed to authenticate with Airtel'}
            
        url = f"{AIRTEL_ENDPOINT}/openapi/moneytransfer/v2/checkstatus"
        
        payload = {
            "transaction": {
                "id": transaction_id
            }
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'X-Country': AIRTEL_COUNTRY_CODE,
            'X-Currency': AIRTEL_CURRENCY_CODE
        }
        
        data = json.dumps(payload).encode('utf-8')
        request_obj = urllib.request.Request(url, data=data, headers=headers, method='POST')
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        return {
            'success': True,
            'status': result.get('status', {}).get('result_code'),
            'message': result.get('status', {}).get('message'),
            'transaction_id': transaction_id,
            'airtel_response': result
        }
        
    except Exception as e:
        print(f"Failed to check Airtel payment status: {str(e)}")
        return {'success': False, 'error': str(e)}

# =============================================================================
# MULTI-PROVIDER PAYMENT ROUTING
# =============================================================================

def detect_mobile_provider(phone_number):
    """
    Detect which mobile money provider to use based on phone number
    
    Args:
        phone_number: Customer phone number
        
    Returns:
        str: 'mtn', 'airtel', or 'unknown'
    """
    # Normalize phone number to Uganda format
    if phone_number.startswith('+256'):
        normalized = phone_number[4:]  # Remove +256
    elif phone_number.startswith('256'):
        normalized = phone_number[3:]  # Remove 256
    elif phone_number.startswith('0'):
        normalized = phone_number[1:]  # Remove 0
    else:
        normalized = phone_number
    
    # MTN Uganda prefixes: 77, 78, 76, 39
    if normalized.startswith(('77', '78', '76', '39')):
        return 'mtn'
    
    # Airtel Uganda prefixes: 70, 75, 74, 20
    elif normalized.startswith(('70', '75', '74', '20')):
        return 'airtel'
    
    # Default to MTN if unknown (since MTN has larger market share)
    else:
        print(f"Unknown provider for {phone_number}, defaulting to MTN")
        return 'mtn'

def initiate_smart_payment(phone_number, amount, metadata=None):
    """
    Smart payment function that routes to appropriate provider
    
    Args:
        phone_number: Customer phone number
        amount: Payment amount (string)
        metadata: Additional payment data
        
    Returns:
        dict: Payment response with provider info
    """
    try:
        provider = detect_mobile_provider(phone_number)
        print(f"Detected provider: {provider.upper()} for {phone_number}")
        
        if provider == 'mtn':
            result = initiate_mtn_payment(phone_number, amount, 'EUR', metadata)
            result['provider'] = 'MTN'
            return result
        
        elif provider == 'airtel':
            result = initiate_airtel_payment(phone_number, amount, 'UGX', metadata)  
            result['provider'] = 'Airtel'
            return result
        
        else:
            return {
                'success': False,
                'error': f'Unsupported provider: {provider}',
                'provider': 'Unknown'
            }
            
    except Exception as e:
        print(f"Smart payment initiation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'provider': 'Unknown'
        }

def check_smart_payment_status(transaction_id, provider):
    """
    Check payment status using the appropriate provider
    
    Args:
        transaction_id: Transaction ID
        provider: Provider name ('MTN' or 'Airtel')
        
    Returns:
        dict: Payment status information
    """
    try:
        if provider.upper() == 'MTN':
            return check_mtn_payment_status(transaction_id)
        elif provider.upper() == 'AIRTEL':
            return check_airtel_payment_status(transaction_id)
        else:
            return {
                'success': False,
                'error': f'Unknown provider: {provider}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# =============================================================================
# USSD ENDPOINT
# =============================================================================

@app.route('/', methods=['POST', 'GET'])
@app.route('/ussd', methods=['POST', 'GET'])
def main_callback():
    # Check request type based on parameters
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    from_number = request.values.get("from", None)
    text = request.values.get("text", "")
    message_id = request.values.get("id", None)
    
    print(f"Request params: sessionId={session_id}, serviceCode={service_code}, phoneNumber={phone_number}, from={from_number}, text='{text}', id={message_id}")
    
    # SMS Request - has 'from' parameter and usually 'id'
    if from_number and not session_id and not service_code:
        print(f"SMS: {from_number} -> '{text}' (ID: {message_id})")
        response_message = process_sms_command(from_number, text)
        
        if response_message:
            sms_result = send_sms(from_number, response_message)
            print(f"SMS Response sent: {response_message}")
        
        return "OK"
    
    # USSD Request - has sessionId, serviceCode, phoneNumber
    elif session_id or service_code or phone_number:
        return ussd_callback(session_id, service_code, phone_number, text)
    
    # Regular GET request - return status page
    elif request.method == 'GET':
        return {
            'service': 'Tusafishe Africa\'s Talking Server',
            'version': '1.0',
            'endpoints': {
                '/': 'Main callback (auto-detects SMS/USSD)',
                '/ussd': 'USSD callback endpoint',
                '/sms': 'SMS webhook endpoint'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    # Unknown request type
    else:
        print(f"Unknown request type: {dict(request.values)}")
        return "OK"

def ussd_callback(session_id, service_code, phone_number, text):
    print(f"USSD: {phone_number} - Session: {session_id} - Text: '{text}'")

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
        return "CON Welcome to Tusafishe!\n1. Register\n2. Status\n3. Purchase"
    
    if state == 'main_menu':
        if text == '1':
            if customer and customer.get('is_registered'):
                return "END You already have a registered account!"
            session['state'] = 'register_pin'
            return "CON Registration Started!\nCreate a 4-digit PIN:"
        elif text == '2':
            if not customer:
                return "END No account found for this number."
            if not customer.get('is_registered'):
                status = "Not Registered"
            elif customer.get('active'):
                status = "Active - Access Granted"
            else:
                status = "Inactive - No Access"
            return (f"END Account Status:\n"
                    f"Phone: {phone_number}\n"
                    f"Status: {status}\n"
                    f"Access expires: {SEMESTER_END_DATE}")
        elif text == '3':
            if not customer or not customer.get('is_registered'):
                return "END Please register first (option 1)."
            session['state'] = 'purchase_semester_confirm'
            return ("CON Purchase Semester Access\n"
                    "Cost: $1 per semester\n"
                    "Unlimited water access\n"
                    "1. Confirm Purchase\n2. Cancel")
        else:
            return "CON Invalid option. Please try again:\n1. Register\n2. Status\n3. Purchase"
    
    # Registration flow
    elif state == 'register_pin':
        pin = text.split('*')[-1]
        if len(pin) == 4 and pin.isdigit():
            # Create customer if doesn't exist
            if not customer:
                customer = create_customer(phone_number)
            if customer:
                session['state'] = 'register_confirm'
                session['data']['pin'] = pin
                return ("CON Confirm registration:\n"
                        f"Phone: {phone_number}\n"
                        f"PIN: {pin}\n"
                        "1. Confirm\n2. Cancel")
            else:
                return "END Error creating account. Please try again later."
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
                    'active': False,
                    'registration_state': 'completed'
                }
                if update_customer(customer['$id'], updates):
                    return (f"END Registration Complete!\n"
                            f"Phone: {phone_number}\n"
                            f"Status: Registered")
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
            # Reactivation just confirms account - doesn't change active status
            if customer.get('active'):
                status = "Active - Access Granted"
            else:
                status = "Inactive - No Access"
            return (f"END Account Confirmed!\n"
                    f"Phone: {phone_number}\n"
                    f"Status: {status}\n"
                    f"Access expires: {SEMESTER_END_DATE}")
        else:
            return "END Invalid PIN."
    
    # Semester purchase flow
    elif state == 'purchase_semester_confirm':
        choice = text.split('*')[-1]
        if choice == '1':
            if customer.get('active'):
                return f"END Already have access until {SEMESTER_END_DATE}"
            
            # Initiate Smart Payment (MTN or Airtel)
            payment_result = initiate_smart_payment(phone_number, '1')
            
            if payment_result.get('success'):
                if payment_result.get('test_mode'):
                    # In test mode, immediately activate
                    updates = {
                        'active': True,
                        'payment_date': str(int(time.time()))
                    }
                    if update_customer(customer['$id'], updates):
                        return (f"END TEST MODE: Access Activated!\n"
                                f"Cost: $1 per semester\n"
                                f"Access until: {SEMESTER_END_DATE}")
                    else:
                        return "END Activation failed. Please try again."
                else:
                    # Real MTN payment initiated, waiting for confirmation
                    return (f"END Payment request sent to MTN.\n"
                            f"Amount: $1\n"
                            f"Check your phone for PIN prompt.\n"
                            f"ID: {payment_result['transaction_id'][:8]}")
            else:
                return f"END Payment failed: {payment_result.get('error', 'Unknown error')}"
        elif choice == '2':
            return "END Purchase cancelled."
        else:
            return "CON Invalid choice:\n1. Confirm Purchase\n2. Cancel"
    
    return "END Invalid input. Please try again."

# =============================================================================
# SMS ENDPOINT
# =============================================================================

@app.route('/sms', methods=['POST'])
def sms_callback():
    # Get SMS data from Africa's Talking webhook
    from_number = request.values.get("from", "")
    text = request.values.get("text", "").strip()
    to_number = request.values.get("to", "")
    message_id = request.values.get("id", "")
    date = request.values.get("date", "")
    
    print(f"SMS: {from_number} -> {to_number}: '{text}' (ID: {message_id})")
    
    response_message = process_sms_command(from_number, text)
    
    if response_message:
        sms_result = send_sms(from_number, response_message)
        print(f"SMS Response sent: {response_message}")
    
    return "OK"

def process_sms_command(phone_number, message):
    customer = get_customer(phone_number)
    if not customer:
        customer = create_customer(phone_number)
    
    if not customer:
        return "Welcome to Tusafishe! 💧 Registration failed. Please try again."
    
    # Parse SMS commands
    msg = message.upper().strip()
    
    if msg in ['MENU', 'HELP', 'START']:
        if customer.get('is_registered'):
            if customer.get('active'):
                status = "Active - Access Granted"
            else:
                status = "Inactive - No Access"
            return (f"Tusafishe Water Kiosk\n"
                    f"Phone: {phone_number}\n"
                    f"Status: {status}\n"
                    f"Access expires: {SEMESTER_END_DATE}\n\n"
                    f"Commands:\n"
                    f"STATUS - Check account\n"
                    f"BUY - Purchase semester access")
        else:
            return ("Welcome to Tusafishe!\n"
                    "Reply REGISTER to create account")
    
    elif msg == 'REGISTER':
        if customer.get('is_registered'):
            return "Already registered! Reply MENU for options."
        else:
            return ("Let's register! Please use USSD:\n"
                    f"Dial *{os.environ.get('USSD_CODE', '123')}# to complete registration")
    
    elif msg in ['STATUS', 'BALANCE']:
        if not customer.get('is_registered'):
            return "Please register first. Reply REGISTER"
        
        if customer.get('active'):
            status = "Active - Access Granted"
        else:
            status = "Inactive - No Access"
        return f"Phone: {phone_number}\nStatus: {status}\nAccess expires: {SEMESTER_END_DATE}"
    
    elif msg == 'BUY':
        if not customer.get('is_registered'):
            return "Please register first. Reply REGISTER"
        
        if customer.get('active'):
            return f"Already have access until {SEMESTER_END_DATE}"
        
        # Initiate Smart Payment (MTN or Airtel)
        payment_result = initiate_smart_payment(phone_number, '1')
        
        if payment_result.get('success'):
            if payment_result.get('test_mode'):
                # In test mode, immediately activate
                updates = {
                    'active': True,
                    'payment_date': str(int(time.time()))
                }
                if update_customer(customer['$id'], updates):
                    return (f"TEST MODE: Access Activated!\n"
                            f"Cost: $1 per semester\n" 
                            f"Access until: {SEMESTER_END_DATE}")
                else:
                    return "Activation failed. Please try again."
            else:
                # Real MTN payment initiated, waiting for confirmation
                return (f"Payment request sent to MTN Mobile Money.\n"
                        f"Amount: $1\n"
                        f"Check your phone and enter PIN to confirm.\n"
                        f"Transaction ID: {payment_result['transaction_id'][:8]}")
        else:
            return f"Payment failed: {payment_result.get('error', 'Unknown error')}"
    
    else:
        return ("Commands: MENU, REGISTER, STATUS\nBUY - Purchase semester access")

# =============================================================================
# PAYMENT WEBHOOK ENDPOINT
# =============================================================================

@app.route('/payments/mtn/status/<transaction_id>', methods=['GET'])
def check_payment_status_endpoint(transaction_id):
    """
    Check MTN payment status via API endpoint
    """
    try:
        status_result = check_mtn_payment_status(transaction_id)
        return status_result
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@app.route('/payments/mtn/test', methods=['POST'])
def test_mtn_payment():
    """
    Test MTN Mobile Money payment integration
    """
    try:
        data = request.get_json() or {}
        phone = data.get('phone', '256781234567')  # MTN number
        amount = data.get('amount', '1')
        
        result = initiate_mtn_payment(phone, amount)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@app.route('/payments/airtel/test', methods=['POST'])
def test_airtel_payment():
    """
    Test Airtel Money payment integration
    """
    try:
        data = request.get_json() or {}
        phone = data.get('phone', '256701234567')  # Airtel number
        amount = data.get('amount', '1')
        
        result = initiate_airtel_payment(phone, amount)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@app.route('/payments/smart/test', methods=['POST'])
def test_smart_payment():
    """
    Test Smart Payment routing (auto-detects MTN vs Airtel)
    """
    try:
        data = request.get_json() or {}
        phone = data.get('phone', '256781234567')  # Defaults to MTN
        amount = data.get('amount', '1')
        
        result = initiate_smart_payment(phone, amount)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

# =============================================================================
# MAIN APPLICATION
# =============================================================================

if __name__ == '__main__':
    print("🚀 Starting Tusafishe Africa's Talking Server...")
    print(f"📱 USSD endpoint: http://localhost:5000/ussd")
    print(f"💬 SMS endpoint: http://localhost:5000/sms") 
    print(f"💰 Payment webhook: http://localhost:5000/payments/webhook")
    app.run(host="0.0.0.0", port=os.environ.get('PORT', 5000), debug=True)