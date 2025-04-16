import requests

def send_test_message():
    # !!!!!!!!! Replace with your actual Power Automate endpoint URL !!!!!!!!! #
    url = "https://your-powerautomate-endpoint-url"

    payload = {
        "query_text": "Test query text",
        "cveid": "CVE-TEST-0001",
        "description": "This is a test description.",
        "cvss_score": "9.8"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in (200, 201, 202):
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. HTTP status: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    send_test_message()
