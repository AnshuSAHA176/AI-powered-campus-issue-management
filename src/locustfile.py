from locust import HttpUser, task, between


ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg4ODc4MTY2LCJpYXQiOjE3ODg4Nzc4NjYsImp0aSI6IjVhMzRmNGFhNDc4MDQ3NzBhYTM2ZDY3NmQ1ZDhkY2Q0IiwidXNlcl9pZCI6ImJjOWNiODYxLTZhNzItNDU4MS05NzU0LWY2ODljZGNiN2JjYSJ9.46xY0vgq67LNwOES7NM2uYpVJoUlraFeo9-632XURbQ"


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