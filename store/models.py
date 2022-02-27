from django.contrib import admin
# "FileExtensionValidator" is for when using "FileField", and allows control of what kind of files may be uploaded, like pdf, xml etc.
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.db import models
from uuid import uuid4  # For use of unique ids for carts.
# For use of "User" settings in Customer, as to avoid dependencies to other apps by not importing directly from .core module.
from django.conf import settings

# Custom validator for validating file sizes.
from .validators import validate_file_size


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+', blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


# For enabling a one-to-many (1 - *) relationship between "Product" and this new class which are basically images of those products.
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images")  # This attribute is a foreign key to the "Product" model. Related names makes queries easier to read.
    # The path. This stores the images to the file system rather than DB, for performance reasons. Path is relative to "MEDIA_ROOT" route, which is directed to "media" folder.
    image = models.ImageField(upload_to="store/images",
                              validators=[validate_file_size])  # Custom defined validator. Multiple validators may be passed in.
    # "FileField()" is also an option, which is used for any other types of files, like documents and PDFs. ImageField is for images only, and validates the image to ensure it's valid.


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)

    # Changed the default setting from the "User" setting in django, to customized "User" model in the "core" app.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # From variable "user" above.
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    # Decorator enables sorting of the name fields.
    @admin.display(ordering="user__first_name")
    def first_name(self):  # For use in list_display in admin module.
        return self.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self):  # For use in list_display in admin module.
        return self.user.last_name

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        permissions = [  # Custom permissions for Customer model. All codenames can be viewed at rest_framework.permissions under DjangoModelPermissions, perms_map.
            # First value, codename for the permission. Second value, description for the permission.
            ("view_history", "Can view history")
        ]


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:  # For adding custom permissions.
        permissions = [  # A list of tuples.
            # Each tuple is a permission. First value is the codename, second value is a description.
            ("cancel_order", "Can cancel order"),
        ]


class OrderItem(models.Model):
    # Set related name, so it can be referenced as and accessed as a field in the OrderSerializer model.
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orderitems")
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    # Creates unique 32 char long ids for carts to prevent attacks. "uuid4" function is not being called, it's simply being referenced to.
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items")  # Name can now be accessed in CarSerializers.
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )  # Ensures that only a minimum of 1 item can be added to the cart, or it'll show an error message. Can be set to whatever minimum amount desired.

    # To make sure a new cart isn't created whenever the quantity of the same product is increased. This prevents creating multiple records.
    class Meta:
        # A unique constraint on "cart" and "product". More unique constraints on 2 or 3 other fields may be added together, if desired.
        unique_together = [["cart", "product"]]


class Review(models.Model):
    # The product which this is a review for, which is a Foreign Key to the Product model. The related name is included, so the Product class
    # will have an attribute called "reviews". On delete is cascade, so the review is also deleted, if the related product is deleted.
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=255)  # Name of the reviewer.
    description = models.TextField()  # No limitation when using TextField.
    date = models.DateField(auto_now_add=True)  # Will automatially populate.
