import socket
import ssl
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime

# Conversion rates
MDL_TO_EUR = 1 / 19  # 1 EUR = 19 MDL


def fetch_data_via_socket(host, port, path):
    """Fetch data from a website using TCP sockets."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap the socket with SSL for HTTPS
    context = ssl.create_default_context()
    with context.wrap_socket(sock, server_hostname=host) as ssock:
        try:
            ssock.connect((host, port))
        except Exception as e:
            print(f"Error connecting to {host}:{port} - {e}")
            return None

        # Prepare and send GET request
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n\r\n"
        )
        ssock.sendall(request.encode())

        # Receive the response
        response = b""
        while True:
            part = ssock.recv(4096)
            if not part:
                break
            response += part

    return response


def extract_body(response):
    """Extract the body from the HTTP response."""
    response_str = response.decode('utf-8')
    header, _, body = response_str.partition("\r\n\r\n")
    return body


def fetch_product_details(product_url):
    """Fetch details of a single product."""
    host = "999.md"
    port = 443  # HTTPS port
    path = product_url

    # Fetch data via socket for product details
    response = fetch_data_via_socket(host, port, path)

    if response is None:
        return None

    body = extract_body(response)
    soup = BeautifulSoup(body, 'html.parser')

    # Extract product data
    product_data = {}

    for feature in soup.find_all('span', class_='adPage__content__features__key'):
        key = feature.text.strip()
        value_tag = feature.find_next('span', class_='adPage__content__features__value')
        value = value_tag.text.strip() if value_tag else "-"
        product_data[key] = value

    # Extract price and currency
    price_value_tag = soup.find('span', class_='adPage__content__price-feature__prices__price__value')
    currency_tag = soup.find('span', class_='adPage__content__price-feature__prices__price__currency')

    if price_value_tag and currency_tag:
        price_value = validate_price_field(price_value_tag.text.strip())
        currency_value = currency_tag.text.strip()

        if price_value is not None:
            product_data["Price"] = price_value
            product_data["Currency"] = currency_value

    return product_data


def validate_price_field(price):
    """Validate price to ensure it's an integer."""
    try:
        return int(''.join(filter(str.isdigit, price)))
    except ValueError:
        return None


def convert_to_eur(price, currency):
    """Convert MDL to EUR, if already EUR return as is."""
    return price * MDL_TO_EUR if currency == "MDL" else price


def filter_products(products):
    """Filter products in a specific price range."""
    filtered_products = [p for p in products if
                         "Price" in p and 100 <= convert_to_eur(p["Price"], p["Currency"]) <= 15000]

    total_price_eur = reduce(lambda acc, p: acc + convert_to_eur(p["Price"], p["Currency"]), filtered_products, 0)

    return filtered_products, total_price_eur


def serialize_to_json(products):
    """Serialize products to JSON format."""
    json_output = "[\n"

    for product in products:
        json_output += "  {\n"
        for key, value in product.items():
            json_output += f'    "{key}": "{value}",\n'
        json_output = json_output.rstrip(",\n") + "\n"  # Remove last comma
        json_output += "  },\n"

    json_output += "]"

    print("JSON Output:")
    print(json_output)


def serialize_to_xml(products):
    """Serialize products to XML format."""
    xml_output = "<products>\n"

    for product in products:
        xml_output += "  <product>\n"
        for key, value in product.items():
            xml_output += f'    <{key}>{value}</{key}>\n'
        xml_output += "  </product>\n"

    xml_output += "</products>"

    print("XML Output:")
    print(xml_output)


def main():
    host = "999.md"
    port = 443  # HTTPS port
    path = "/ro/list/transport/motorcycles"

    response = fetch_data_via_socket(host, port, path)

    if response is None:
        print("Failed to retrieve data.")
        return

    body = extract_body(response)

    # Parse the HTML content
    soup = BeautifulSoup(body, 'html.parser')

    products_list = []

    for product in soup.find_all('li', class_='ads-list-photo-item'):
        link = product.find('a')

        if link and 'href' in link.attrs:
            product_url = f"https://999.md{link['href']}"
            product_details = fetch_product_details(product_url)

            if product_details and "Price" in product_details:
                products_list.append(product_details)

    # Filter products based on price range and calculate total price
    filtered_products, total_price_eur = filter_products(products_list)

    for product in filtered_products:
        print(product)

    serialize_to_json(filtered_products)
    serialize_to_xml(filtered_products)

    print(f"\nTotal Price of Filtered Products (EUR): {total_price_eur:.2f}")
    print(f"UTC Timestamp: {datetime.utcnow()}")

if __name__ == "__main__":
    main()