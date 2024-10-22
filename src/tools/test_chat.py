import requests

access_token = ''
url = '/chat'
headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/x-www-form-urlencoded'}

data = {'mess': '你好'}
response = requests.post(url, headers=headers, data=data)

print(response.status_code)
print(response.json())
