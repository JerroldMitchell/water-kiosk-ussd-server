#!/usr/bin/env python3
"""
Setup MTN Mobile Money API User and API Key
"""
import json
import urllib.request
import urllib.parse
import urllib.error
import uuid
import base64

# Your MTN MoMo Subscription Key
MTN_SUBSCRIPTION_KEY = "366b71ffd4724d5e90b0607182318c91"
MTN_ENDPOINT = "https://sandbox.momodeveloper.mtn.com"
TARGET_ENVIRONMENT = "sandbox"

def create_api_user():
    """
    Step 1: Create an API User
    """
    try:
        # Generate a UUID for the API User
        api_user_id = str(uuid.uuid4())
        print(f"Creating API User with ID: {api_user_id}")
        
        url = f"{MTN_ENDPOINT}/v1_0/apiuser"
        
        payload = {
            "providerCallbackHost": "tusafishe.com"  # Your callback domain
        }
        
        headers = {
            'X-Reference-Id': api_user_id,
            'Ocp-Apim-Subscription-Key': MTN_SUBSCRIPTION_KEY,
            'Content-Type': 'application/json'
        }
        
        data = json.dumps(payload).encode('utf-8')
        request_obj = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        try:
            response = urllib.request.urlopen(request_obj, timeout=10)
            print(f"✅ API User created successfully!")
            print(f"API User ID: {api_user_id}")
            return api_user_id
        except urllib.error.HTTPError as e:
            if e.code == 201:
                print(f"✅ API User created successfully!")
                print(f"API User ID: {api_user_id}")
                return api_user_id
            else:
                error_body = e.read().decode('utf-8')
                print(f"❌ Failed to create API user: {e.code} - {error_body}")
                return None
                
    except Exception as e:
        print(f"❌ Error creating API user: {str(e)}")
        return None

def get_api_user_info(api_user_id):
    """
    Step 2: Get API User Information
    """
    try:
        print(f"\nGetting API User info for: {api_user_id}")
        
        url = f"{MTN_ENDPOINT}/v1_0/apiuser/{api_user_id}"
        
        headers = {
            'Ocp-Apim-Subscription-Key': MTN_SUBSCRIPTION_KEY,
            'X-Target-Environment': TARGET_ENVIRONMENT
        }
        
        request_obj = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"✅ API User Info Retrieved:")
        print(f"   Provider Callback Host: {result.get('providerCallbackHost')}")
        print(f"   Target Environment: {result.get('targetEnvironment')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error getting API user info: {str(e)}")
        return None

def create_api_key(api_user_id):
    """
    Step 3: Create API Key for the user
    """
    try:
        print(f"\nCreating API Key for user: {api_user_id}")
        
        url = f"{MTN_ENDPOINT}/v1_0/apiuser/{api_user_id}/apikey"
        
        headers = {
            'Ocp-Apim-Subscription-Key': MTN_SUBSCRIPTION_KEY,
            'X-Target-Environment': TARGET_ENVIRONMENT
        }
        
        request_obj = urllib.request.Request(url, headers=headers, method='POST')
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        api_key = result.get('apiKey')
        print(f"✅ API Key created successfully!")
        print(f"API Key: {api_key}")
        
        return api_key
        
    except Exception as e:
        print(f"❌ Error creating API key: {str(e)}")
        return None

def test_authentication(api_user_id, api_key):
    """
    Step 4: Test authentication by getting an access token
    """
    try:
        print(f"\nTesting authentication...")
        
        url = f"{MTN_ENDPOINT}/collection/token/"
        
        # Create basic auth header
        credentials = f"{api_user_id}:{api_key}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Ocp-Apim-Subscription-Key': MTN_SUBSCRIPTION_KEY,
            'X-Target-Environment': TARGET_ENVIRONMENT
        }
        
        request_obj = urllib.request.Request(url, headers=headers, method='POST')
        response = urllib.request.urlopen(request_obj, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        access_token = result.get('access_token')
        expires_in = result.get('expires_in')
        token_type = result.get('token_type')
        
        print(f"✅ Authentication successful!")
        print(f"   Token Type: {token_type}")
        print(f"   Expires In: {expires_in} seconds")
        print(f"   Access Token: {access_token[:20]}...")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return None

if __name__ == "__main__":
    print("=== MTN Mobile Money API User Setup ===")
    print(f"Subscription Key: {MTN_SUBSCRIPTION_KEY}")
    print(f"Endpoint: {MTN_ENDPOINT}")
    print(f"Environment: {TARGET_ENVIRONMENT}")
    print()
    
    # Step 1: Create API User
    api_user_id = create_api_user()
    if not api_user_id:
        print("❌ Setup failed at user creation step")
        exit(1)
    
    # Step 2: Get user info (optional verification)
    user_info = get_api_user_info(api_user_id)
    
    # Step 3: Create API Key  
    api_key = create_api_key(api_user_id)
    if not api_key:
        print("❌ Setup failed at API key creation step")
        exit(1)
    
    # Step 4: Test authentication
    access_token = test_authentication(api_user_id, api_key)
    if not access_token:
        print("❌ Setup failed at authentication test")
        exit(1)
    
    print("\n" + "="*50)
    print("🎉 MTN Mobile Money Setup Complete!")
    print("="*50)
    print("Add these to your environment variables:")
    print()
    print(f"export MTN_MOMO_SUBSCRIPTION_KEY='{MTN_SUBSCRIPTION_KEY}'")
    print(f"export MTN_MOMO_API_USER='{api_user_id}'")
    print(f"export MTN_MOMO_API_KEY='{api_key}'")
    print(f"export MTN_MOMO_ENDPOINT='{MTN_ENDPOINT}'")
    print(f"export MTN_MOMO_TARGET_ENVIRONMENT='{TARGET_ENVIRONMENT}'")
    print()
    print("Then restart your server to use real MTN payments!")