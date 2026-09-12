from locust import HttpUser, task, between


ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg5MjE5NTY1LCJpYXQiOjE3ODkyMTkyNjUsImp0aSI6IjU4MGM5YWQ1NjkwOTQzMmY5ZTdiMTFiOGVlYjNlYzYwIiwidXNlcl9pZCI6ImJjOWNiODYxLTZhNzItNDU4MS05NzU0LWY2ODljZGNiN2JjYSJ9.IzjpIGlwE5JFSCtZcLz1O_ZjEYIRjBZ_SaMsXIgQRvs"


class CivicAIUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def dashboard(self):
        self.client.get(
            "/dashbord/",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}"
            },
            name="Dashboard",
        )