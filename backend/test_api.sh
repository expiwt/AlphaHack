#!/bin/bash

API_URL="http://localhost:8000/api/v1"
EMAIL="test@alfabank.ru"
PASSWORD="test123"

echo "🔧 Testing Alfa-Bank API"
echo "========================"

# 1. Health check
echo ""
echo "1️⃣ Health check..."
curl -s $API_URL/health | jq .

# 2. Register user
echo ""
echo "2️⃣ Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"full_name\": \"Test User\"
  }")

echo $REGISTER_RESPONSE | jq .
TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')

# 3. Login
echo ""
echo "3️⃣ Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

echo $LOGIN_RESPONSE | jq .
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "✓ Token: $TOKEN"

# 4. Seed test data
echo ""
echo "4️⃣ Creating test data..."
curl -s -X POST $API_URL/clients/seed/data \
  -H "Authorization: Bearer $TOKEN" | jq .

# 5. Get clients list
echo ""
echo "5️⃣ Getting clients list..."
curl -s -X GET "$API_URL/clients?sort=income_predicted&order=desc&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 6. Get specific client
echo ""
echo "6️⃣ Getting specific client..."
curl -s -X GET $API_URL/clients/cli_test_001 \
  -H "Authorization: Bearer $TOKEN" | jq .

# 7. Get dashboard
echo ""
echo "7️⃣ Getting dashboard..."
curl -s -X GET $API_URL/dashboard \
  -H "Authorization: Bearer $TOKEN" | jq .

echo ""
echo "✅ API Testing completed!"
