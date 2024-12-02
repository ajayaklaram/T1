from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Load the service account JSON file
credentials = service_account.Credentials.from_service_account_file(
    'C:\\Users\\Ajaya\\Downloads\\vertical-sunset-440402-h4-2a0c8fafed21.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

# Refresh the access token
credentials.refresh(Request())
access_token = credentials.token
print("Access Token:", access_token)
