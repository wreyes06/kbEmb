import requests #for http requests
import json #for json
import openai
import os

# Disable SSL verification
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

openai.api_key = os.getenv("APIKEY") 
openai.api_base = os.getenv("RESOURCEENDPOINT")  
openai.api_type = "azure"
openai.api_version = "2023-05-15"
url = os.getenv("EMBEDDINGSURL")

#Takes string as input & generates embeddings
def get_embeddings(content: str) -> list[float]: 
    payload = json.dumps({
        "input": content
    })
    
    headers = {
        'Content-Type': 'application/json',
        'api-key': os.getenv("APIKEY") 
    }
    
    response = requests.post(url, data=payload, headers=headers, verify=False)
    
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        embeddings = response_data["data"][0].get("embedding", [])
        return embeddings
    else:
        print(f"Error: {response.status_code}")
        return []

def html_to_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    plain_text = soup.get_text(separator=' ')
    return plain_text

def process_html_content(html_content: str) -> list[float]:
    text_content = html_to_text(html_content)
    embeddings = get_embeddings(text_content)
    if not embeddings:
        print("Embeddings not generated successfully.")
    return embeddings
