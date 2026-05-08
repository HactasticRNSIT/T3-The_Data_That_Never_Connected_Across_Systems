import urllib.request
import json

# Test root endpoint
req = urllib.request.Request('http://localhost:8000/')
res = urllib.request.urlopen(req)
print("Root:", res.read().decode())

# Test login
data = json.dumps({"email": "officer@police.gov", "password": "securepassword123"}).encode()
req = urllib.request.Request('http://localhost:8000/auth/login', data=data, headers={"Content-Type": "application/json"})
res = urllib.request.urlopen(req)
result = json.loads(res.read().decode())
print("Login successful!")
print("Token:", result["access_token"][:50] + "...")
print("User:", json.dumps(result["user"], indent=2))
