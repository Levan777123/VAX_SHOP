from rest_framework import permissions


class IsManager(permissions.BasePermission):
    message = 'Only VAX shop managers can do this.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'manager')


class IsProductOwnerOrReadOnly(permissions.BasePermission):
    message = 'Only the manager who created this product can change it.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and obj.created_by_id == request.user.id)


class IsOrderOwnerOrManager(permissions.BasePermission):
    message = 'You can access only your own orders.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id or request.user.role == 'manager'


class IsReviewOwnerOrManager(permissions.BasePermission):
    message = 'You can edit only your own review.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id or request.user.role == 'manager'


class HasPurchasedProduct(permissions.BasePermission):
    message = 'You must buy this product before reviewing it.'

    def has_permission(self, request, view):
        if getattr(view, 'action', None) != 'create':
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        product_pk = view.kwargs.get('product_pk')
        from .models import Order, OrderItem
        return OrderItem.objects.filter(
            product_id=product_pk,
            order__user=request.user,
            order__status__in=[Order.Status.PAID, Order.Status.SHIPPED],
        ).exists()
