import requests

# Send HTTP GET request
url = 'https://999.md/ro/list/transport/motorcycles'  # Example URL
response = requests.get(url)

# Check the response
if response.status_code == 200:
    print("Success:", response.status_code)
else:
    print("Failed:", response.status_code)
