

import requests

class Services():
    def __init__(self,url,token):
        self.base_url=url
        self.access_token=token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    def complain_list(self):
        response=requests.get( f"{self.base_url}complaints/",
            headers=self._headers(),)
        response.raise_for_status()
        return response.json()

    def compliant_details(self,complaint_id):
        response=requests.get( f"{self.base_url}complaints/{complaint_id}/",
                    headers=self._headers(),)
        response.raise_for_status()
        return response.json()

    def get_similar_complaints(self):
        'similar/<str:compliant_id>/'
        response=requests.get( f"{self.base_url}complaints/{complaint_id}/",
                            headers=self._headers(),)
        response.raise_for_status()
        return response.json()
        

    