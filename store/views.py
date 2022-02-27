# Handles error messages, and allows to avoid repeated "try/exception" blocks.
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, response
# For implementing annotations, "Count" function is needed.
from django.db.models.aggregates import Count

# For generic filtering.
from django_filters.rest_framework import DjangoFilterBackend

# This is used to access "django rest frameworks" Request and Response, which are more powerful HTTP methods than Djangos built-ins. These are action decorators.
from rest_framework.decorators import api_view, action
# For filtering by search. For sorting.
from rest_framework.filters import SearchFilter, OrderingFilter
# These modules are used to simplify the process of creating querysets, serializations and validating data with built-in functions.
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
# For supplying permission classes used for authentication, to allow or deny access to chosen views.
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
# This is to replace Djangos "HttpResponse" class, with a simpler and more powerful class.
from rest_framework.response import Response
# ModelViewSet is for combining the logic for multiple related views inside 1 class, to avoid repeating the querysets, serializers etc. various places.
from rest_framework.viewsets import ModelViewSet, GenericViewSet
# Used for constants, for various HTTP status codes. Used e.g. for returning error messages.
from rest_framework import status
# Used to paginate data using a pagenumber.
from rest_framework.pagination import PageNumberPagination
# These modules are for creating generic views, which have many built-in functions for serializing, retrieving and posting data.
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
# The base class for all class-based views. This is to go away from regular views and to using class-views.
from rest_framework.views import APIView


# From the "models" module, in the current folder, import the "Product" class.
from .models import Cart, CartItem, Collection, Customer, Order, Product, OrderItem, ProductImage, Review
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer
from .filters import ProductFilter  # Custom created filters.
from .pagination import DefaultPagination  # Custom created pagination.
# Custom created permission for authenticated access to modify or only read objects.
from .permissions import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerHistoryPermission


# Generic API view, used to combine the logic of multiple related views together.
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").all()  # Eager load.
    # Just the class is returned, and not creating an object "()"
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Custom created fields are being imported here. Allows for prices to be filtered using comparison logic.
    filterset_class = ProductFilter
    # Line can be removed if a global pagination setting have been defined in settings.py.
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["title", "description"]
    ordering_fields = ["unit_price", "last_update"]  # Fields to sort by.

    # ALL OF THIS LOGIC IS MADE OBSELETE WITH THE IMPLEMENTATION OF DJANGOFILTERBACKENDS LIBRARY, AND QUERYSET ATTRIBUTE IS BROUGHT BACK.
    # # Overwritting since filtering is not possible with the "all()" function.
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     # Trying to read collection id from querystring if it's there, go to query_params. "get()" is used here, since it returns None if no key by this name is found.
    #     collection_id = self.request.query_params.get("collection_id")
    #     if collection_id is not None:  # Apply a filter.
    #         # New queryset is received, and used to reset the previous one.
    #         queryset = queryset.filter(collection_id=collection_id)

    #     return queryset

    # Overwritting this method by returning the request object.

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    # Overwritting the queryset method, otherwise all reviews will appear on all products, if the ".all()" function was used. self.kwargs must
    # be accessed if each product is to be linked to reviews unique to itself only.
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    # Overwritting the context object, to pass to the serializer, so manually entering id on reviews are bypassed, and automated.
    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


# This inherits from other classes, since only the quantity of items needs to be updated, and the cart id MUST NOT be sent to the API endpoint.
# "ModelViewSet" has Update and List models, that are not needed in this view. So a custom viewset is needed.
class CartViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    # "prefetch_related" is called to enable eager loading. When retrieving a cart, its items and products are loaded with it simultaneously. Otherwise additional queries are sent to the DB.
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


class CartItemViewset(ModelViewSet):
    # To prevent any "PUT" requests. Listing all allowed requests here.
    http_method_names = ["get", "post", "patch", "delete"]

    # To avoid hardcoded serializer. This dynamically returns a serializer class depending on the request method.
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    # To get the cart id from the URL, since its not available in the request.
    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}

    # Overwritting method and filtering by cart id, instead of returning a queryset. Queryset will return all cart items.
    def get_queryset(self):
        # ".select_related" is for eager loading. It loads relevant queries alongside "products", rather than doing extra seperate query loads afterwards.
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related("product")


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # This view is only allowed with this permission. This attribute is set to a list of permission classes by not calling the ().
    # Only admin is allowed to retrieve, update, delete. A workaround using ModelViewSet, which allows all requests, intead of using several Mixins for creating, retrieving, updating and deleting.
    permission_classes = [IsAdminUser]

    # Used for overriding the default set permission above, and customize them. Method is inherited from the viewset.
    # So i.e. authenticated users can retrieve customer objects, but only authenticated users, like an admin, can update/delete customer objects.
    def get_permissions(self):
        if self.request.method == "GET":
            # This returns a list of permission objects by calling the ().
            return [AllowAny()]
        # For any POST or PUT requests, the user must be authenticated.
        return [IsAuthenticated()]

    # New (action) method for retrieving current users profile (at store/customers/me).
    # False will make the action available on the list view (at customers/me) since "customers" is a list.
    # True will make the action available on the detail view (at customers/1/me), meaning it's available when going to a specific customer, and then accessing the "me" endpoint.
    # Methods to be supported. Overriding permission for this particullar action only. So only authenticated users, like personal, may modify at the "customers" endpoint.
    @action(detail=False, methods=["GET", "PUT"], permission_classes=IsAuthenticated)
    def me(self, request):
        # Getting a customer object by retrieving a customer with the user id. Since this is a tuple with 2 values, first a customer object and second a boolean of whether this object was created,
        # the tuple needs to be unpacked immediately by wrapping () around, to get this customer object. Otherwise the endpoint will throw an AttributeError ('tuple' object has no attribute 'user_id').
        customer = Customer.objects.get(
            user_id=request.user.id)
        if request.method == "GET":
            # Give the customer object to this serializer.
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    # A custom action for viewing the history of a particular customer. Detail is set to True since this is for a particular customer. Additionally decorated with a custom permission class.
    @action(detail=True, permission_classes=ViewCustomerHistoryPermission)
    def history(self, request, pk):  # pk is because this is for a particular customer
        return Response("yes")


class OrderViewSet(ModelViewSet):
    # queryset = Order.objects.all()

    http_method_names = ["get", "post", "patch", "delete",
                         "head", "options"]  # Restricting the http methods.

    # Instead of hardcoding permission classes, the permissions will be overwritten and customized.
    def get_permissions(self):
        # To prevent a long if statement, this syntax can be used. If the method is in this list.
        if self.request.method in ["PATCH", "DELETE"]:
            # Returning a list of objects, not permission classes.
            return [IsAdminUser()]
        return [IsAuthenticated()]  # Returning a list of objects.

    # Must be overwritten, since a different serializer must be created - the serializer has only "cart_id" field which is also the one returned, but an "Order" object is what we want returned, and not "cart_id".
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(  # Getting the data and de-serializing it.
            data=request.data,  # Giving the serializer the request data.
            context={"user_id": self.request.user.id})  # Getting the user_id here from a context object, since request objects can't be accessed inside serializers,
        # so it can't be retrieved from the "CreateOrderSerializer"'s overwritten save method. Giving the serializer the context object, so it access the user id.
        serializer.is_valid(raise_exception=True)  # Validating the data.
        order = serializer.save()  # Saving the changes.
        # Creating a new serializer, and resetting the above serializer. Giving this serializer the "order" object which was returned from the "save()" method above.
        # The save method was overwritten, customized, in the "CreateOrderSerializer" class, in the serializers module.
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    # Overriding the serializer method, depending whether it's a POST request or a simple view.
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    # Overriding the queryset method, so that only orders specific to the user only is shown. Admin can access everything.
    def get_queryset(self):
        user = self.request.user  # For making code cleaner.
        if user.is_staff:  # Meaning admin.
            return Order.objects.all()

        # Customer ID is not included in the JWT, so from user ID the customer ID is calculated. "only()" is used to retrieve the id field, since "get()" function will return a complete customer object.
        customer_id = Customer.objects.only(
            "id").get(user_id=user.id)

        # Only orders for a specific customer.
        return Order.objects.filter(customer_id=customer_id)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    # Extracting product_pk from the context object to feed it to the serializer, so no null values as image id may be passed in, when uploading images as raw data at the endpoint.
    # In the serializer that pk is getting grabbed from the context, and use it to create a product image object.
    # Basically removes the field of "{
#                                    "image": null
#                                     }" when posting raw data at images endpoint, and autopopulates it from the URL by grabbing it from the context below.
    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}

    # Instead of returning all product images or all images in the DB, the queryset method is overwritten. Only images of a particular product must be returned.
    def get_queryset(self):
        # Getting product_id from the URL (from self.kwargs of "name_of_url_parameter").
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])
