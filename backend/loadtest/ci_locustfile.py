"""Lightweight Locust scenario for CI — avoids mass registration throttling."""

from locust import HttpUser, between, task

TENANT = 'platform-demo'
ADMIN_EMAIL = 'admin@civic-education.ss'
ADMIN_PASSWORD = 'AdminPass123!'


class CiSmokeUser(HttpUser):
    wait_time = between(0.2, 1.0)

    def on_start(self):
        self.token = None
        self.tenant_headers = {'X-Tenant-Slug': TENANT}
        response = self.client.post(
            '/api/auth/login/',
            json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
            name='/api/auth/login/ [ci]',
        )
        if response.status_code == 200:
            self.token = response.json().get('access')

    @property
    def auth_headers(self):
        headers = dict(self.tenant_headers)
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    @task(5)
    def health(self):
        self.client.get('/api/health/', name='/api/health/ [ci]')

    @task(10)
    def articles(self):
        self.client.get('/api/articles/', headers=self.tenant_headers, name='/api/articles/ [ci]')

    @task(5)
    def quizzes(self):
        self.client.get('/api/quizzes/', headers=self.auth_headers, name='/api/quizzes/ [ci]')

    @task(5)
    def topics(self):
        self.client.get('/api/topics/', headers=self.tenant_headers, name='/api/topics/ [ci]')

    @task(3)
    def billing_plans(self):
        self.client.get('/api/billing/plans/', name='/api/billing/plans/ [ci]')

    @task(2)
    def profile(self):
        if self.token:
            self.client.get('/api/users/profile/', headers=self.auth_headers, name='/api/users/profile/ [ci]')
