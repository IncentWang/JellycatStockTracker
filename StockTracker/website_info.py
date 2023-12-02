import requests
from bs4 import BeautifulSoup
import json

agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'} #using agent to solve the blocking issue

class Website_info:
    def __init__(self, url, sku):
        self.url = url
        self.sku = sku
    
    def get_info_from_url(self):
        r = requests.get(self.url, headers=agent)
        
        bs = BeautifulSoup(r.text, 'html.parser')
        js_str = bs.find_all('script')[17].text
        variants = js_str.split('settings = ')[0].split('variants = ')[1]
        variants = variants.replace("'", "\"")

        self.variants_obj = json.loads(variants)
    
    def check_stock(self):
        return self.variants_obj[self.sku]["sell"] == "true"

    def get_name(self):
        return self.variants_obj[self.sku]["name"]