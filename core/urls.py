# For creating a generic view to render a template for homepage.
from django.views.generic import TemplateView
from django.urls import path

# URLConf
urlpatterns = [
    # Referencing TemplateView, call as_view, pass in template_name as kwarg. Index is created at index.html module of "templates" folder.
    path('', TemplateView.as_view(template_name='core/index.html')),
]
