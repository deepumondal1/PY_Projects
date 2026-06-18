import requests
import json

base_url = "https://mingle-ionapi.eu1.inforcloudsuite.com"

def get_object_schema(name:str, access_token:str):
    endpoint = f"{base_url}/LDX77VQ6U4GVV6M6_TST/DATAFABRIC/datacatalog/v1/object/{name}"
    
    headers = {'accept': 'application/json', 'Authorization': f"Bearer {access_token}"}
    try:
        resp = requests.get(endpoint, headers=headers)
        
        if resp.status_code != 200:
            raise Exception(resp.status_code, resp.text)
        
        return resp.json()
    
    except Exception as err:
        print('[ERROR get_object_schema]', err.__traceback__.tb_lineno, err)
        return None
    
    
def post_object_schema(table_names:list, access_token:str):
    endpoint = f"{base_url}/LDX77VQ6U4GVV6M6_TST/DATAFABRIC/datacatalog/v1/object/fetch"
    
    headers = {'Content-Type': 'application/json', 'accept': 'application/json', 'Authorization': f"Bearer {access_token}"}
    
    body = json.dumps({
        "names": table_names
    })
    
    try:
        resp = requests.post(endpoint, headers=headers, data=body)
        
        if resp.status_code != 200:
            raise Exception(resp.status_code, resp.text)
        
        data:dict = resp.json()
        obj = data.get('objects', None)

        if not obj:
            return None
        
        return dict(map(lambda x: (x['name'],x),obj))
    
    except Exception as err:
        print('[ERROR get_object_schema]', err.__traceback__.tb_lineno, err)
        return None