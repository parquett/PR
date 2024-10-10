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


def validate_string_field(field):
    """ Remove extra spaces from string fields. """
    return field.strip()


def validate_price_field(price):
    """ Validate price to ensure it's an integer. """
    try:
        # Removing any non-digit characters and converting to integer
        return int(''.join(filter(str.isdigit, price)))
    except ValueError:
        return None


# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

for product in soup.find_all('li', class_='ads-list-photo-item'):
    link = product.find('a')

    if link and 'href' in link.attrs:
        product_url = f"https://999.md{link['href']}"
        product_response = requests.get(product_url)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        # Make dictionary
        product_data = {}

        # Extract additional info
        for feature in product_soup.find_all('span', class_='adPage__content__features__key'):
            key = validate_string_field(feature.text.strip())
            value_tag = feature.find_next('span', class_='adPage__content__features__value')

            if value_tag:
                value = validate_string_field(value_tag.text.strip())
            else:
                value = "-"

            product_data[key] = value

        # Extract the price
        price_value_tag = product_soup.find('span', class_='adPage__content__price-feature__prices__price__value')
        currency_tag = product_soup.find('span', class_='adPage__content__price-feature__prices__price__currency')

        if price_value_tag and currency_tag:
            price_value = validate_price_field(price_value_tag.text.strip())  # Convert price to integer
            currency_value = validate_string_field(currency_tag.text.strip())  # Extract currency
        else:
            price_value = "Negociabil"
            currency_value = ""

        combined_price = f"{price_value} {currency_value}"
        product_data["Price"] = combined_price

        print(f"Product Data: {product_data}")
        print(f"Product Link: {product_url}\n")
