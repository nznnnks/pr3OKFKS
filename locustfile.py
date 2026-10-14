from faker import Faker
from locust import HttpUser, task, TaskSet, SequentialTaskSet, between
import random

fake = Faker("ru_RU")


class CustomerFlow(SequentialTaskSet):
    def on_start(self):
        self.client.post(
            "/login",
            data={
                "login_username": "violent",
                "login_password": "deck123",
            },
            name="POST /login (customer)",
        )

    @task
    def open_shop(self):
        self.client.get("/shop", name="GET /shop")

    @task
    def open_category(self):
        slug = random.choice(["skateboards", "clothing", "accessories"])
        self.client.get(f"/shop/category/{slug}", name="GET /shop/category")

    @task
    def add_to_cart(self):
        self.client.post(
            "/cart/add",
            data={
                "product_id": random.randint(1, 20),
                "quantity": random.randint(1, 3),
            },
            name="POST /cart/add",
        )


class AdminActions(TaskSet):
    def on_start(self):
        self.client.post(
            "/login",
            data={
                "login_username": "admin",
                "login_password": "admin123",
            },
            name="POST /login (admin)",
        )

    @task(10)
    def admin_dashboard(self):
        self.client.get("/admin", name="GET /admin")

    @task(10)
    def admin_products(self):
        self.client.get("/admin/products", name="GET /admin/products")

    @task(2)
    def create_product(self):
        data = {
            "category_slug": random.choice(["skateboards", "clothing", "accessories"]),
            "name": fake.catch_phrase()[:50],
            "description": fake.text(max_nb_chars=150),
            "image_url": "images/skate.png",
            "price": f"{random.uniform(500, 12000):.2f}",
        }
        self.client.post(
            "/admin/products/create",
            data=data,
            name="POST /admin/products/create",
        )


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    tasks = {
        CustomerFlow: 7,
        AdminActions: 3,
    }