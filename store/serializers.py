# Serializers converts a model instance, like a product object, into a Python dictionary.
# Used for rendering objects for the Products resources - it takes a dictionary object and returns a JSON object, which then is represented.
# from itertools import product
from dataclasses import fields
from pyexpat import model
from django.forms import models
from rest_framework import serializers

# For converting the 1.1 in the tax method from a float to a decimal, before multiplying it with unit_price since unit_price is defined as a decimal.
from decimal import Decimal

# Used for transactions - either entire block of code passes and gets commited, or something fails, nothing gets commited and a rollback will happen.
from django.db import transaction

# Used for "Type annotation" in custom method for SerializerMethodField. When typing "." in the instance, all memembers of the "Product" class is accessable.
from .models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, ProductImage, Review
from .signals import order_created  # Signal.


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):

    # Getting the product id from self.context, as the context method is overwritten in the "ProductImageViewSet" class of the views module.
    def create(self, validated_data):
        product_id = self.context["product_id"]
        # Explicitly creating product image object.
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        # Not returning product_id, as it's already available at the URL like "/products/1/images/1".
        fields = ["id", "image"]


# Decide what fields of the Product class to serialize - what fields to include in a Python dictionary, which then can be accessed through APIs.
# This will be the external representation of the internal resources and data - not all fields needs to be displayed or defined here, as in the "Product" class.
class ProductSerializer(serializers.ModelSerializer):
    # Many must be set to True, since more than one image is allowed per product.
    # Read-only must be set to True, otherwise multiple images must be passed when creating a product. Only properties related to a product-object is wanted to be passed when creating a product.
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:  # ModelSerializer is used to define a new Meta data, which will set the chosen fields much more simple. Custom created fields can also be added.
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory',
                  'unit_price', 'price_with_tax', 'collection', 'images']
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # Takes 2 arguments. If another name instead of "unit_price" is chosen, then a source parameter must be set, and tell Django where to look for this field in the Product class.
    # price = serializers.DecimalField(
    #    max_digits=6, decimal_places=2, source="unit_price")

    # Custom added field of choice. Used to define a custom method of choice below. That method will return a value, which will then be passed in this field.
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    # By doing this, this the relationship is serialized. Each collection will now appear as a string in the fields in the APIs.
#    collection = serializers.StringRelatedField()

    # "Type annotation" is used like this here, since Python doesn't know the type of the Product object. This is how to annotate.
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "date", "name", "description"]

    # Overwritting the create method to automate the product id field.
    # Product_id is read from self.context also overwritten in the views module, to extract "product_id". Then product id is set to this value.
    # Lastly the validated_data dictionary is unpacked. The product object is returned from this overwritten method.
    def create(self, validated_data):
        product_id = self.context["product_id"]
        return Review.objects.create(product_id=product_id, **validated_data)


# For displaying custom chosen fields, rather than every field, when a product object is returned at the CartItem API endpoint.
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    # To return a product object, instead of product ID at the CartItem API endpoint.
    product = SimpleProductSerializer()
    # Accessing methods to return a value of a custom field, like total_price.
    total_price = serializers.SerializerMethodField()

    # Annotate with "CartItem" to access ".quantity" inside cart_item. Is otherwise unaccessable.
    def get_total_price(self, cart_item: CartItem):
        # For the custom made field "total_price" in "CartItem".
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    # Must be declared here for read-only to the endpoint. Otherwise an ID must be provided, when sending a post request to the server.
    id = serializers.UUIDField(read_only=True)
    # How to link items. Ready only, or it will appear when posting a new cart, which this list is not supposed to. Will prevent creation of new carts.
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()  # Defining custom field.

    def get_total_price(self, cart):
        # List comprehension. Syntax is: "[item for item in collection]".
        # "cart.items" returns a manager object, and using ".all()" returns a queryset used to return all the items.
        # ".quantity" * ".unit_price" for each item returns a list of totals for this collection.
        # "sum()" is used in order to add all these totals together and get the sum of totals for the entire cart.
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


# Creating this class to bypass the "product" object that must be passed in, when posting a product to a cart. Only product, without an object, and quantity is needed.
class AddCartItemSerializer(serializers.ModelSerializer):
    # This attribute is generated dynamically at run-time, and must therefore be defined explicitly.
    product_id = serializers.IntegerField()

    # For validating individual fields, rather than entire objects. To prevent app from crashing when posting item of 0 id.
    def validate_product_id(self, value):  # "value" being validated - the id.
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value

    # Overwritting the default save method, since adding the same product to the same cart multiple times will otherwise create multiple cartitem records.
    # Simply updating the quantity of an existing item is desired.
    def save(self, **kwargs):
        # Getting the URL parameter from the overwritten context object, and passed in here.
        cart_id = self.context["cart_id"]
        # When the data gets validated in the serializers, the attribute "validated_data" becomes accessable, which is a dict. Then "product_id" can be read which was received from the client.
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        # If there is no such cart item, throw an exception.
        try:
            # Saving logic. "get" cart item with 2 attributes - custom defined cart id, custom defined product id.
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity  # Update an existing item.
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # May also pass parameters in as "product_id=product=id, quantity=quantity". Or just unpack self.validated_data dictionary as done below.
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)  # Create a new item.

        # "self.instance" must be included in the logic. Either to update a record or to create a record. The object that is updated/created must be stored in this attribute of
        # the "validated_data" dictionary within the save method. Finally, "self.instance" is returned.
        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    # Allows only quantity to be updated, when a patch request is sent.
    class Meta:
        model = CartItem
        fields = ["quantity"]


# For storing customer data for a profile.
class CustomerSerializer(serializers.ModelSerializer):
    # Must be defined, since it doesn't exist in the Customer class. This attribute must be created dynamically at runtime.
    # Field is otherwise updateable, which is not desireable since it can create issues.
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership", ]


class OrderItemSerializer(serializers.ModelSerializer):
    # Allows for nested objects to appear in the Orders endpoint, within each order each orderitem with its details on products will appear. Each product is a nested object.
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "unit_price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    # Establishing a Foreign Key, so items can be accessed.
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


# Creating a new serializer for updating orders with only the desired field to be updatable, rather than hardcoding the unwanted fields as "read_only" in the "OrderSerializer" serializer.
class UpdateOrderSerializer(serializers.ModelSerializer):
    # Will only allow to update, "PATCH" request, the payment_status field, since all the other fields (id, customer, placed at, items) are to be left untouched.
    class Meta:
        model = Order
        fields = ["payment_status"]


# Extending from "Serializers", since a needed field "cart_id" is not a field in the "Order" class. No Meta class is created based on the "Order" model. The base class is simply used here.
class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    # To avoid creating an order regardless if a cart exists or not. Validating the data ensures an order is only created if the cart id exists.
    def validate_cart_id(self, cart_id):  # Two parameters is needed.
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No cart with that ID exists.")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:  # If cart is empty
            raise serializers.ValidationError(
                "The cart is empty. Please add something to your order.")
        return cart_id  # Otherwise return the cart id as a valid value.

    # Overriding the save method, since the logic of saving an order is very specific, and Django can not auto generate it.
    # The logic is, go to shopping cart table, grab all cart items, move to order_items table, delete shopping cart.
    def save(self, **kwargs):
        with transaction.atomic():  # A transaction for rollback purposes in case of failure.
            # Set to an expression here, so to easier access several times in below code.
            cart_id = self.validated_data["cart_id"]

            customer = Customer.objects.get(
                user_id=self.context["user_id"])  # Getting the customer object, so it can be passed in below. "get_or_create" method returns a tuple, and must be unpacked immediately.
            # Creating an order object. Passing in "customer" field only, since the other 2 fields are already set by and auto field and default field.
            order = Order.objects.create(customer=customer)

            #  For creating order items, firstly items must be added to the "cart_id", then for each cart item an order item must be created and saved in the DB.
            cart_items = CartItem.objects.select_related("product").filter(
                cart_id=cart_id)  # Filter where cart_id = validated data of cart id. This returns a list of cart items, which is a queryset.

            # "cart_items" must be converted into "order_items". A list comprehension is used, syntax is "[item for item in collection]".
            order_items = [  # A list of order items is returned.
                OrderItem(  # Using kwargs, this OrderItem object is being initialized.
                    order=order,  # Set to the order object created above at the overwritten "save" method
                    # When retrieving the cart items, eager loadinging with their products must be done; otherwise for each cart item an extra query will be sent to read the product of that item.
                    product=item.product,
                    # Unit price must be set at the time of placing the order.
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items  # Collection is "cart_items"
            ]
            # A method to avoid iterating over each individual order, item, and save them, to avoid sending too many queries to the DB.
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            # Firing the signal. If one of the receivers fails and throws and exception, the other receivers are notified with "send_robust".
            # The class that is sending the signal. Getting it from self.__class__. It's a magic attribute that returns the class of the current instance.
            # Optionally supplying additional data - the order that was created. Set order as a keyword argument. In the store app, everytime an order is created, the signal is fired.
            order_created.send_robust(self.__class__, order=order)

            return order
