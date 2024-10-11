import requests
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime

# conversion rates
MDL_TO_EUR = 1 / 19  # 1 EUR = 19 MDL
EUR_TO_MDL = 19      # 1 EUR = 19 MDL

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
        return int(''.join(filter(str.isdigit, price)))
    except ValueError:
        return None


def convert_to_eur(price, currency):
    """ Convert MDL to EUR, if already EUR return as is. """
    if currency == "MDL":
        return price * MDL_TO_EUR
    return price

def convert_to_mdl(price, currency):
    """ Convert EUR to MDL, if already MDL return as is. """
    if currency == "EUR":
        return price * EUR_TO_MDL
    return price


# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# to store all products
products = []

for product in soup.find_all('li', class_='ads-list-photo-item'):
    link = product.find('a')

    if link and 'href' in link.attrs:
        product_url = f"https://999.md{link['href']}"
        product_response = requests.get(product_url)
        product_soup = BeautifulSoup(product_response.content, 'html.parser')

        # Dictionary to store product data
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
            price_value = None
            currency_value = ""

        if price_value:
            product_data["Price"] = price_value
            product_data["Currency"] = currency_value
            products.append(product_data)

# convert MDL to EUR
mapped_products = list(map(lambda p: {
    **p,
    "Price": convert_to_eur(p["Price"], p["Currency"])
}, products))

# filter products in a price range
filtered_products = list(filter(lambda p: 100 <= p["Price"] <= 15000, mapped_products))

# reduce to sum up the prices of filtered products
total_price = reduce(lambda acc, p: acc + p["Price"], filtered_products, 0)

timestamp = datetime.utcnow()

print("Filtered Products:")
for product in filtered_products:
    print(product,"\n")
print(f"Total Price of Filtered Products (EUR): {total_price}")
print(f"UTC Timestamp: {timestamp}")
