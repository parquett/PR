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

for product in soup.find_all('li', class_='ads-list-photo-item'):
    link = product.find('a')

    if link and 'href' in link.attrs:
        product_url = f"https://999.md{link['href']}"
        product_response = requests.get(product_url)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        # Extract additional info
        for feature in product_soup.find_all('span', class_='adPage__content__features__key'):
            key = feature.text.strip()
            value_tag = feature.find_next('span', class_='adPage__content__features__value')

            if value_tag:
                value = value_tag.text.strip()
            else:
                value = "['href'-"
            print(f"{key}: {value}")

        print(f"Product Link: {product_url}\n")


