# -*- coding: UTF-8 -*-
import requests
import re
import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

def replace_urls(data):
    """
    递归地替换 JSON 数据中所有 https://neodb.social 的 URL 为 https://dou.snsou.cn。
    """
    if isinstance(data, dict):
        return {key: replace_urls(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_urls(item) for item in data]
    elif isinstance(data, str):
        return data.replace('https://neodb.social', 'https://dou.snsou.cn')
    return data

def get_data(neo_type, neo_category):
    if neo_type not in ['wishlist', 'progress', 'complete']:
        raise ValueError('Invalid type parameter. Must be wishlist, progress, or complete')
    if neo_category not in ['book', 'movie', 'tv', 'music', 'game', 'podcast']:
        raise ValueError('Invalid category parameter. Must be book, movie, tv, music, game, or podcast')

    url = f'https://neodb.social/api/me/shelf/{neo_type}?category={neo_category}'
    headers = {'Authorization': 'Bearer ' + os.environ.get('AUTHORIZATION'), 'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    
    # 替换返回的数据中的 URL
    json_data = replace_urls(json_data)
    
    pages_value = json_data['pages']
    
    all_results = []
    for page_num in range(1, pages_value + 1):
        requests_path = f'{url}&page={page_num}'
        r = requests.get(requests_path, headers=headers)
        result = r.json()
        
        # 替换该页数据中的 URL
        result = replace_urls(result)
        
        all_results.extend(result['data'])
    
    return all_results

class Handler(BaseHTTPRequestHandler): 
    def do_GET(self):
        path = self.path
        neo_type = re.findall(r'type=([^&]*)', path)[0]
        neo_category = re.findall(r'category=([^&]*)', path)[0]
        try:    
            data = get_data(neo_type, neo_category) 
        except Exception as e:  
            self.send_error(500, str(e))
            return
        
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        return
    
# def run(server_class=HTTPServer, handler_class=Handler, port=8080):
#     server_address = ('', port)
#     httpd = server_class(server_address, handler_class)
#     print(f'Starting server on port {port}')
#     httpd.serve_forever()

# if __name__ == '__main__':
#     run()
