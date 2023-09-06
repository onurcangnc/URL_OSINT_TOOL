import requests
from bs4 import BeautifulSoup
import ssl
import datetime
from urllib.parse import urlparse
import certifi
import socket
from colorama import init, Fore
# Initialize colorama
init()

# Define the target URL
target_url = "https://www.ctis.bilkent.edu.tr"  # Replace with your target website

# Suppress SSL certificate verification warnings
ssl._create_default_https_context = ssl._create_unverified_context

# Send an HTTP GET request to the target URL
response = requests.get(target_url, verify=certifi.where())

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract and print the page title
    page_title = soup.title.string
    print(f"Page Title: {page_title}")

    # Extract and print meta description (if available)
    meta_description = soup.find("meta", {"name": "description"})
    if meta_description:
        print(f"Meta Description: {meta_description['content']}")

    # Extract and print all the links on the page
    links = soup.find_all("a")
    if links:
        print("Links on the Page:")
        for link in links:
            href = link.get("href")
            if href:
                print(href)

    # Extract and print HTTP headers
    headers = response.headers
    print("HTTP Headers:")
    for key, value in headers.items():
        print(f"{key}: {value}")

    # Save image URLs to a text file
    images = soup.find_all("img")
    if images:
        print("Image URLs:")
        with open("image_urls.txt", "w") as file:
            for img in images:
                src = img.get("src")
                if src:
                    print(src)
                    file.write(src + "\n")

    # Extract and print text content of the page (excluding HTML tags)
    text_content = soup.get_text()
    print("Text Content:")
    print(text_content)

    # Identify and print HTML forms on the page
    forms = soup.find_all("form")
    if forms:
        print("HTML Forms:")
        for form in forms:
            form_fields = form.find_all("input")
            if form_fields:
                print("Form Fields:")
                for field in form_fields:
                    field_name = field.get("name")
                    if field_name:
                        print(f"Field Name: {field_name}")

    # Get and print IP address of the target server
    try:
        target_ip = socket.gethostbyname(urlparse(target_url).hostname)
        print(f"\nTarget Server IP Address: {target_ip}")
    except socket.gaierror as e:
        print(f"Failed to retrieve target server IP address: {str(e)}")

    # Get and print HTTPS certificate information
    try:
        cert_info = ssl.get_server_certificate((target_url, 443), ca_certs=certifi.where())
        x509 = ssl.PEM_cert_to_DER_cert(cert_info)
        cert_subject = dict(x[0] for x in ssl._ssl._test_decode_x509(x509).get("subject"))
        cert_issuer = dict(x[0] for x in ssl._ssl._test_decode_x509(x509).get("issuer"))
        cert_start_date = datetime.datetime.strptime(cert_subject['notBefore'], "%Y%m%d%H%M%SZ")
        cert_end_date = datetime.datetime.strptime(cert_subject['notAfter'], "%Y%m%d%H%M%SZ")
        print("\nHTTPS Certificate Information:")
        print(f"Issued To: {cert_subject['commonName']}")
        print(f"Issued By: {cert_issuer['commonName']}")
        print(f"Valid From: {cert_start_date}")
        print(f"Valid Until: {cert_end_date}")
    except Exception as e:
        print(f"Failed to retrieve HTTPS certificate information: {str(e)}")

    # Extract and print domain information
    parsed_url = urlparse(target_url)
    domain_info = parsed_url.netloc.split(":")[0]
    print("\nDomain Information:")
    print(f"Domain: {domain_info}")
