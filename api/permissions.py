from rest_framework import permissions
from django.core.exceptions import PermissionDenied


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == 1:
            if request.method in ['POST', 'PUT', 'DELETE']:
                return True
            elif request.method == 'GET':
                if request.user and request.user.role == 2 and request.path == '/api/users':
                    return False
                return True
        return False

class StudentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 2
