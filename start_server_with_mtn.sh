#!/bin/bash
# Start server with MTN Mobile Money credentials

echo "🚀 Starting Tusafishe Server with MTN Mobile Money Integration..."

# Set MTN Mobile Money environment variables
export MTN_MOMO_SUBSCRIPTION_KEY='366b71ffd4724d5e90b0607182318c91'
export MTN_MOMO_API_USER='42c1a828-b8aa-4124-a7e3-deb873232439'
export MTN_MOMO_API_KEY='824ec7a3e7bc475caed33fc2ca4a9fdb'
export MTN_MOMO_ENDPOINT='https://sandbox.momodeveloper.mtn.com'
export MTN_MOMO_TARGET_ENVIRONMENT='sandbox'

# Set other environment variables
export APPWRITE_ENDPOINT='http://localhost/v1'
export PORT=5000

echo "✅ MTN Mobile Money: ENABLED"
echo "✅ Server Port: $PORT"
echo "✅ Appwrite: $APPWRITE_ENDPOINT"
echo ""

# Start the server
python3 at_server.py