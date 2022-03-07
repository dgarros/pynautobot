import time
from re import U
from urllib.parse import quote

from pynautobot.models.extras import JobResults

class JobsApp:
    def __init__(self, api):
        """Initialization of class.

        Args:
            api (pynautobot.api): pynatutobot Api class to make calls to the Nautobot API endpoints.
        """
        self.api = api
        # # Add on top of the base_url the endpoint /graphql/ which will be the url used
        # self.url = self.api.base_url + "/graphql/"
    
    def get(self, id):
        return self.api.extras.job_results.get(id)

    def run(self, class_path, data=None, commit=True, schedule=None):
        
        """
        #         {
        #   "data": "string",
        #   "commit": true,
        #   "schedule": {
        #     "name": "string",
        #     "start_time": "2022-03-07T11:40:58.930Z",
        #     "interval": "immediately"
        #   }
        # }
        {
        "url": "https://demo.nautobot.com/api/extras/jobs/local/data_quality/VerifyHasRack/",
        "id": "local/data_quality/VerifyHasRack",
        "name": "Verify Device Rack",
        "description": "Verify a device is inside a rack",
        "test_methods": [],
        "vars": {
            "site": "MultiObjectVar",
            "device_role": "MultiObjectVar",
            "device_type": "MultiObjectVar"
        },
        "result": {
            "id": "e8d896ec-2a0b-40df-802e-c198bbe8a116",
            "url": "https://demo.nautobot.com/api/extras/job-results/e8d896ec-2a0b-40df-802e-c198bbe8a116/",
            "created": "2022-03-07T11:49:07.604209Z",
            "completed": null,
            "name": "local/data_quality/VerifyHasRack",
            "obj_type": "extras.job",
            "status": {
            "value": "pending",
            "label": "Pending"
            },
            "user": {
            "id": "b0802181-4fd5-4043-a89a-0e7b69536df3",
            "url": "https://demo.nautobot.com/api/users/users/b0802181-4fd5-4043-a89a-0e7b69536df3/",
            "username": "demo",
            "display": "demo"
            },
            "data": null,
            "job_id": "ff70427b-2131-428f-8dff-c18a42b14ae1",
            "schedule": null
        }
        }
        """
        safe_class_path = quote(class_path, safe="")
        url = f"{self.api.base_url}/extras/jobs/{safe_class_path}/run/"
        print(url)
        payload = {"commit": commit}
        if schedule:
           payload["schedule"] = schedule 
        
        if data:
            payload["data"] = data 

        response = self.api.http_session.post(url, json=payload, headers=self.api.headers)

        # Don't create an object with an error, raise an exception
        try:
            response.raise_for_status()
        except Exception as err:
            if response.status_code == 404:
                raise ValueError(f"Unable to find the Job associated with the class_path : {class_path} at {url}")
            else:
                raise err
        
        return JobResults(response.json()["result"], self.api, url)

    def run_and_wait(self, class_path, commit=True, schedule=None, interval=1, timeout=30):
        
        job = self.run(class_path=class_path, commit=commit,schedule=schedule)

        while job.status.value in ["pending", "running"]:
            job = self.get(id=job.id)
            time.sleep(interval)
            
        return job
        