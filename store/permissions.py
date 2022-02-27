# For creation of custom authentication class. All permission classes should inherit from the BasePermission class.
from rest_framework import permissions
from rest_framework.permissions import BasePermission, DjangoModelPermissions


class IsAdminOrReadOnly(BasePermission):
    # Overriding this method, to allow or deny access to modifications.
    def has_permission(self, request, view):
        # Checking if this method is in the list of safe request methods.
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can access the target view for view purposes.
        # Only return True, if both conditions are True - the "bool()" function is used here for the double conditional purpose.
        return bool(request.user and request.user.is_staff)


# For preventing anyone outside of this permission group to view data.
class FullDjangoModelPermissions(DjangoModelPermissions):
    # Defining a constructor.
    def __init__(self) -> None:
        # To send a GET request, the user should have the "view" permission.
        self.perms_map["GET"] = ['%(app_label)s.view_%(model_name)s']


class ViewCustomerHistoryPermission(BasePermission):
    # Overriding the has_permission method, to see what codenames are permitted to this class.
    def has_permission(self, request, view):
        # This "user" objects has a method "has_perm". The codename for the permission must be passed in here like "appname.permission_name".
        return request.user.has_perm("store.view_history")
