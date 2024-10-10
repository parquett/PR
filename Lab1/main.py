import requests
from bs4 import BeautifulSoup

# Send HTTP GET request
url = 'https://999.md/ro/list/transport/motorcycles'
response = requests.get(url)

# Check the response
if response.status_code == 200:
    print("Success:", response.status_code)
else:
    print("Failed:", response.status_code)

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

for product in soup.find_all('div', class_='ads-list-photo-item'):
    name = product.find('div', class_='ads-list-photo-item-title').text.strip()
    price = product.find('div', class_='ads-list-photo-item-price').text.strip()
    print(f"Product Name: {name}, Price: {price}")

