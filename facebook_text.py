import os
from dotenv import load_dotenv
import requests
load_dotenv()

page_id=os.getenv('FACEBOOK_PAGE_ID')
page_access_token=os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')

print('Page id: ',page_id)
if not page_id:
    print('Access token is missing')
    exit()

url=f"https://graph.facebook.com/{page_id}/feed"

data = {
    "message": "Hello from my AI Social Media Agent 🚀",
    "access_token": page_access_token
}

response=requests.post(
    url,
    data,
    timeout=10
)

print("Status Code: ",response.status_code)
print("response")
print(response.text)