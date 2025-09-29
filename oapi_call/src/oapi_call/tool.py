import requests
from crewai.tools import tool
import base64, json

@tool("Get Purchase Requisition")
def get_purchase_requisition(api_request: dict) -> dict:
    """
    Executes an API request against an Oracle REST Data Services (ORDS) endpoint.

    Args:
        api_request: A dictionary containing 'method', 'url', and optionally 'payload',
                     'username', and 'password' for Basic Authentication.
                     - 'method': HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
                     - 'url': The full URL of the ORDS endpoint.
                     - 'payload': (Optional) A dictionary representing the JSON body for POST/PUT requests.
                     - 'username': (Optional) Username for Basic Authentication.
                     - 'password': (Optional) Password for Basic Authentication.

    Returns:
        A dictionary containing the JSON response from the API if successful,
        or an error message with details if an error occurs.
    """
    # 1. Input Validation
    if not all(key in api_request for key in ['method', 'url']):
        return {"error": "Invalid request object. 'method' and 'url' are required."}

    # 2. Extract Request Parameters
    method = api_request['method'].upper()
    url = api_request['url']
    payload = api_request.get('payload')

    # Extract username and password for authentication
    username = api_request.get('username')
    password = api_request.get('password')

    # 3. Define Headers
    # Start with Content-Type as it's always relevant for JSON APIs
    headers = {
        'Content-Type': 'application/json'
    }

    # Add Basic Authorization header if username and password are provided
    if username and password:
        # Concatenate username and password with a colon
        credentials = f"{username}:{password}"
        # Encode the credentials string in Base64
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        # Add the Authorization header
        headers['Authorization'] = f"Basic {encoded_credentials}"
        print(f"Adding Basic Authorization header for user: {username}") # For debugging

    # 4. Logging Request Details
    print(f"\n--- Executing API Call ---")
    print(f"Method: {method}")
    print(f"URL: {url}")
    if payload:
        print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"Headers: {headers}") # Show all headers including auth

    # 5. Execute the API Request (Error Handling with Try-Except)
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            json=payload,
            timeout=30  # Set a timeout for the request
        )

        # 6. Check for HTTP Errors
        response.raise_for_status()

        # 7. Process Successful Responses
        if response.text:
            return response.json()
        else:
            return {"status_code": response.status_code, "message": "Success with no content."}

    # 8. Error Handling Blocks
    except requests.exceptions.HTTPError as http_err:
        error_details = str(http_err)
        try:
            if http_err.response and http_err.response.text:
                error_json = http_err.response.json()
                error_details = error_json
        except json.JSONDecodeError:
            pass
        return {"error": "HTTP Error", "status_code": http_err.response.status_code, "details": error_details}
    except requests.exceptions.RequestException as req_err:
        return {"error": "Request Failed", "details": str(req_err)}
    except Exception as e:
        return {"error": "An unexpected error occurred", "details": str(e)}

##--- Example Usage ---
# if __name__ == '__main__':
#
#     # Example with Basic Auth (replace with your actual ORDS endpoint and credentials)
#     # NOTE: Using a placeholder URL as I cannot execute against a real ORDS endpoint.
#     # You would replace "https://your-ords-instance/ords/your_schema/your_resource"
#     # with your actual ORDS URL.
#     authenticated_request = {
#         "method": "GET",
#         "url": "https://fa-etaj-dev18-saasfademo1.ds-fa.oraclepdemos.com/fscmRestApi/resources/11.13.18.05/purchaseRequisitions?q=Requisition='BIR60015'", # This is a test endpoint that requires basic auth (user:passwd)
#         "username": "SCM_IMPL",
#         "password": "Winfo@123",
#         "payload": None
#     }
#
#     print("\n--- Testing GET Request with Basic Authentication ---")
#     auth_result = get_purchase_requisition(authenticated_request)
#     print(json.dumps(auth_result, indent=2))