from rest_framework.permissions import BasePermission, SAFE_METHODS

from tenders.models import Subscriber, SubscriberBalance

SAFE_HTTP_METHODS = ['GET', 'HEAD']
ACTION_HTTP_METHODS = ['GET', 'PUT']


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.is_staff:
            return True
        if request.method in SAFE_HTTP_METHODS:
            return True

        return False


class DKNumbersIsSubscriberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        subscriber = Subscriber.objects.get(user=request.user)
        for s in subscriber.dk_numbers.all():
            for d in obj.dk_numbers.all():
                if s == d and request.method in SAFE_HTTP_METHODS:
                    return True

        return False


class BalanceIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        subscriber = Subscriber.objects.get(user=request.user)
        subscriber_balance = SubscriberBalance.objects.get(subscriber=subscriber)
        if subscriber_balance == obj:
            return True

        return False


class IsAdminOrReadAndPutOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.is_staff:
            return True

        return request.method in SAFE_METHODS or request.method == 'PUT'
