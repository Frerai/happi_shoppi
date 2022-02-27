from store.models import Product
from django.contrib import admin
# Name clash for custom defined class, so alias is needed here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin, ProductImageInline
from tags.models import TaggedItem
# Custom defined User class from "models" module in this folder.
from .models import User


@admin.register(User)  # Registering with the "User" model.
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Added email, first name and last name, since no null values are desired. Email is customly set as an unique constraint in the "User" model.
            'fields': ('username', 'password1', 'password2', "email", "first_name", "last_name"),
        }),
    )


class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline, ProductImageInline]  # Multiple inlines may be added.


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
