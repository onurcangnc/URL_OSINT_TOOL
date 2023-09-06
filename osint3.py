import argparse
import requests
import ssl
import datetime
from urllib.parse import urlparse
import certifi
import socket
import re
from colorama import init, Fore
import whois

# Initialize colorama
init()

# Create a command-line interface
parser = argparse.ArgumentParser(description="OSINT Tool")
parser.add_argument("--target-url", required=True, help="Target URL for OSINT")
args = parser.parse_args()

# Check if "http://" or "https://" is missing, and prepend it if necessary
target_url = args.target_url
if not target_url.startswith("http://") and not target_url.startswith("https://"):
    target_url = "http://" + target_url

# Suppress SSL certificate verification warnings
ssl._create_default_https_context = ssl._create_unverified_context

# Send an HTTP GET request to the target URL
response = requests.get(target_url, verify=certifi.where())

# Function to colorize links based on accessibility
def colorize_link(link, color):
    return f"{color}{link}{Fore.RESET}"

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Extract and print the page title
    page_title = re.search(r'<title>(.*?)</title>', response.text)
    if page_title:
        print(f"Page Title: {page_title.group(1)}")

    # Extract and print meta description (if available)
    meta_description = re.search(r'<meta name="description" content="(.*?)"', response.text)
    if meta_description:
        print(f"Meta Description: {meta_description.group(1)}")

    # Extract and print all the links on the page
    links = re.findall(r'href=["\'](https?://(?:www\.)?[^"\']+)["\']', response.text)
    if links:
        print("Links on the Page:")
        for link in links:
            try:
                link_response = requests.get(link, verify=certifi.where())
                if link_response.status_code == 200:
                    print(colorize_link(link, Fore.GREEN))
                else:
                    print(colorize_link(link, Fore.RED))
            except Exception as e:
                print(colorize_link(link, Fore.RED))
                continue

    # Extract and print HTTP headers
    headers = response.headers
    print("HTTP Headers:")
    for key, value in headers.items():
        print(f"{key}: {value}")

    # Save image URLs to a text file
    images = re.findall(r'src=["\'](https?://[^"\']+\.(?:jpg|png|gif))["\']', response.text)
    if images:
        print("Image URLs:")
        with open("image_urls.txt", "w") as file:
            for img in images:
                print(img)
                file.write(img + "\n")

    # Identify and print HTML forms on the page
    forms = re.findall(r'<form.*?</form>', response.text, re.DOTALL)
    if forms:
        print("HTML Forms:")
        for form in forms:
            form_fields = re.findall(r'<input.*?name=["\'](.*?)["\']', form)
            if form_fields:
                print("Form Fields:")
                for field_name in form_fields:
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
    except ConnectionRefusedError as e:
        print(f"Failed to establish a connection to the HTTPS port (443): {str(e)}")
    except Exception as e:
        print(f"Failed to retrieve HTTPS certificate information: {str(e)}")

    # Extract and print domain information
    parsed_url = urlparse(target_url)
    domain_info = parsed_url.netloc.split(":")[0]
    print("\nDomain Information:")
    print(f"Domain: {domain_info}")

    # Perform a Whois lookup for domain registration information
    try:
        domain_info = whois.whois(domain_info)
        print("\nWhois Information:")
        print(f"Domain Name: {domain_info.domain_name}")
        print(f"Registrar: {domain_info.registrar}")
        print(f"Registrant Name: {domain_info.name}")
        print(f"Registrant Email: {domain_info.email}")
        print(f"Registration Date: {domain_info.creation_date}")
    except Exception as e:
        print(f"Failed to retrieve Whois information: {str(e)}")

    # Extract and print social media links using regular expressions
    social_media_links = re.findall(r'href=["\'](https?://(?:www\.)?(facebook|twitter|linkedin)\.[a-z]+)/?["\']', response.text, re.IGNORECASE)
    if social_media_links:
        print("Social Media Links:")
        for link, platform in social_media_links:
            print(f"{platform.capitalize()}: {link}")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")