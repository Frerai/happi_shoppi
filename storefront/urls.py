"""storefront URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings  # For redirecting URL to user media and images.
from django.conf.urls.static import static  # Also used for path for images.
from django.contrib import admin
from django.urls import path, include
import debug_toolbar

admin.site.site_header = 'Storefront Admin'
admin.site.index_title = 'Admin'

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('playground/', include('playground.urls')),
    # If the URL starts with "store", it should be handled by the "store.urls" module.
    path('store/', include('store.urls')),
    # For authentication endpoints, all requests are delegated to djoser.urls.
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),  # For JSon Web Tokens.
    path('__debug__/', include(debug_toolbar.urls)),
]

# If it's in development, it's turned on, and use this. In production, it's turned off and then don't use this.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # First argument is the media URL - "settings.MEDIA_URL". Second argument is a keyword argument "document_root" - it must be set to the media root.

    # Only available in development and testing. Add a new path starting with 'silk', include urls from the 'silk' app.
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
