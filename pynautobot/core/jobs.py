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

    def get(self, id: str):
        """Get the status of a Job in Nautobot.

        Args:
            id (str): UUID of a Job in Nautobot

        Returns:
            JobResults: JobResult object
        """
        return self.api.extras.job_results.get(id)

    def run(self, class_path: str, data: dict = None, commit: bool = True, schedule: dict = None):
        """Start the Execution of a Job in Nautobot. 

        Args:
            class_path (str): path of the job in nautobot ex: "local/mydir/Myjob"
            data (dict, optional): Additional payload to provide when executing the Job. Defaults to None.
            commit (bool, optional): Flag to indicate if the Job should commit its changes or rollback everything. Defaults to True.
            schedule (dict, optional): Additional information to schedule the Job execution instead of executing it immediately. Defaults to None.

        Raises:
            ValueError: the class_path doesn't correspond to valid job

        Returns:
            JobResults: JobResult object
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

    def run_and_wait(
        self, class_path: str, commit: bool = True, schedule: dict = None, interval: int = 1, timeout: int = 30
    ):
        """_summary_

        Args:
            class_path (_type_): _description_
            commit (bool, optional): _description_. Defaults to True.
            schedule (_type_, optional): _description_. Defaults to None.
            interval (int, optional): _description_. Defaults to 1.
            timeout (int, optional): _description_. Defaults to 30.

        Returns:
            _type_: _description_
        """

        job = self.run(class_path=class_path, commit=commit, schedule=schedule)

        while job.status.value in ["pending", "running"]:
            job = self.get(id=job.id)
            time.sleep(interval)

        return job
