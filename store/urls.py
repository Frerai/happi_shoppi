from django.urls import path
# Router will register URL patterns when using ViewSets.
# Used to register nested URLs.
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()
# First argument is name of the endpoint i.e. "products", "collections" without "/". Second is the name of the viewset i.e. "views.ProductViewSet".
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)
router.register("carts", views.CartViewSet)
router.register("customers", views.CustomerViewSet)
# Basename must be set for generating the name of views, like "orders-list" and "orders-detail". But only the prefix, the first part of the name, needs to be specified.
router.register("orders", views.OrderViewSet, basename="orders")

# The parent router. The parent prefix. The lookup parameter.
products_router = routers.NestedDefaultRouter(
    router, "products", lookup="product")
# Registering the child resource. Prefix ("reviews"), the view set, prefix used for generating the name of URL patterns ("product-review").
products_router.register("reviews", views.ReviewViewSet,
                         basename="product-reviews")
products_router.register(
    "images", views.ProductImageViewSet, basename="product-images")  # Nested route for product images. Products is already registered as a parent URL, so only nested url must be registered here.


carts_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
carts_router.register("items", views.CartItemViewset, basename="cart-items")


# Both types of URLs can be combined and included here.
urlpatterns = router.urls + products_router.urls + carts_router.urls

# Original URLConf
# urlpatterns = [
#     path('products/', views.ProductList.as_view()),
#     # Makes sure only integers may be applied as product ID as resource request.
#     path('products/<int:pk>/', views.ProductDetail.as_view()),
#     path('collections/', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.CollectionDetail.as_view(),
#          name='collection-detail'),

# ]
