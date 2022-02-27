from locust import HttpUser, task, between  # Used for testing performance.

# For generating random entries at endpoints to simulate a user going from one collection to another.
from random import randint


'''
Commands for running locust:
"locust -f locustfiles/browse_products.py" for specifying the locust file, add path.
Access locus via: http://localhost:8089/ 
Add host for locus interface: http://localhost:8000 
'''

# Locust will create an instance of this class for each user, when running performance tests, and execute the tasks defined in this class.


class WebsiteUser(HttpUser):
    # Possible tasks included: viewing products, viewing product details, add product to cart.
    """For testing performance purposes. Each defined method will be executed during performance testing.
    """
    # Attribute for adding delay time between execution of tasks. Otherwise tasks will be executed immediately after another.
    # Randomly waits between values, between each task.
    wait_time = between(30, 180)

    @task(35)  # Decorator needed to make this method a task.
    def view_products(self):
        # Sending a GET request to the Products endpoint.
        collection_id = randint(3, 6)  # Collections with products in them.
        # To access collection id, add it as a querystring parameter with "?". Added "name=" argument so all these URLs are added to a particular group to simplify the reports.
        self.client.get(
            f'/store/products/?collection_id={collection_id}',
            name='/store/products')

    @task(45)  # Weight for setting priority for tasks.
    def view_product(self):  # Viewing a particular product.
        product_id = randint(1, 1000)

        self.client.get(
            f'/store/products/{product_id}',
            name='/store/products/:id')  # Grouping these URLs under a particular group.

    @task(10)
    def add_to_cart(self):  # Adding a product to a cart.
        # Limiting the range so duplicate products in cart can occur, and allows for testing performance of updating  product quantities in cart.
        product_id = randint(1, 150)

        # Post request, since items are added.
        self.client.post(
            # Getting cart id from the "on_start" method. Cart is is generated at run-time when a user enters the website.
            f'/store/carts/{self.cart_id}/items/',  # POST at "items" endpoint.
            name='/store/carts/items',  # Grouping the URLs.
            # For sending data to the server a json object is created and sent as a dict.
            json={'product_id': product_id, 'quantity': 1}
        )

    @task
    # Simulating a slow respnse from service by hitting endpoint defined at "say_hello" - for benchmark purposes.
    def say_hello(self):
        self.client.get("/playground/hello/")

    # For generating a cart id, which should be generated at run-time when a user browses the website.
    def on_start(self):  # This is a special method in this class.
        # Sending post request. Getting a response.
        response = self.client.post('/store/carts/')
        result = response.json()  # Getting a json object in the response.
        # This is a dictionairy, so the id property can be accessed.
        self.cart_id = result['id']
