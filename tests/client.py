import requests

url = "http://localhost:8080"
try:
    response = requests.get(url)
    print(response.text)
except requests.exceptions.RequestException as e:
    print(str(e))
