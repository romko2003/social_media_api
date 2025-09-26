from rest_framework.permissions import BasePermission


class IsSelfProfile(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return request.user.is_authenticated and obj.user == request.user
