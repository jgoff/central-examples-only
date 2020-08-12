# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import getpass
import requests
import yaml
import pprint

# Replace with your secret variables. DO NOT SHARE! THIS IS UNSAFE & FOR EDUCATIONAL PURPOSES ONLY!
client_id = "your-client-id-here"
client_secret = "your-client-secret-here"
customer_id = "your-customer-id-here"
username = "your-username-here"
# Example URL "https://eu-apigw.central.arubanetworks.com"
base_url = "https://your-central-url-here.com"

# Login - Password Input Required
login_url = base_url + "/oauth2/authorize/central/api/login"
login_params = {"client_id": client_id}
payload = {"username": username, "password": getpass.getpass()}
resp = requests.post(login_url, params=login_params, json=payload)
if resp.json()["status"] == True:
    print("Login Successful")
else:
    print("Login Failed")
    exit()

# If login is successful, variables for tokens created
codes = {"csrf": resp.cookies["csrftoken"], "ses": resp.cookies["session"]}

# Authorize API call using login generated tokens
authcode_url = base_url + "/oauth2/authorize/central/api"
ses = "session=" + codes["ses"]
headers = {
    "X-CSRF-TOKEN": codes["csrf"],
    "Content-type": "application/json",
    "Cookie": ses,
}
payload = {"customer_id": customer_id}
params = {"client_id": client_id, "response_type": "code", "scope": "all"}
resp = requests.post(authcode_url, params=params, json=payload, headers=headers)
auth_code = resp.json()["auth_code"]

# Access and Refresh Token API call
token_url = base_url + "/oauth2/token"
token_data = {
    "grant_type": "authorization_code",
    "code": auth_code
}
resp = requests.post(token_url, data=token_data, auth=(client_id, client_secret))

# Extract tokens from the JSON response
refresh_token = resp.json()["refresh_token"]
access_token = resp.json()["access_token"]
# Print tokens to screen - delete if preferred
print("Refresh Token:{} Auth Token:{}".format(refresh_token, access_token))
refresh_token_data = {"refresh_token": refresh_token}

# Write refresh token to local yaml file for future reference
with open("refresh_token.yaml", "w") as write_file:
    yaml.dump(refresh_token_data, write_file)

# Sample API call to GET Central APs and print JSON to screen
get_ap_url = base_url + "/monitoring/v1/aps"
header = {"authorization": f"Bearer {access_token}"}
get_ap_call = requests.get(get_ap_url, headers=header)
pprint.pprint(get_ap_call.json())
