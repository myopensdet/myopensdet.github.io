# Template from myOpenSDET: https://myopensdet.github.io/
import time

import requests


class ApiClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def get(self, path):
        answer = requests.get(self.base_url + path, headers=self.headers, timeout=10)
        if answer.status_code == 503:
            time.sleep(5)  # the old staging server needed a retry
            answer = requests.get(self.base_url + path, headers=self.headers, timeout=10)
        return answer
