import requests
import json
import os
import dotenv

dotenv.load_dotenv()

if __name__ == '__main__':
    endpoint = "/api/meetings/4dtYGMkGnbnlooUQ8Aod/files"
    url = "http://localhost:8000" + endpoint
    response = requests.get(url)
    parsed = response.json()
    print(json.dumps(parsed, indent=4))