from rest_framework.throttling import UserRateThrottle


class OrderBurstThrottle(UserRateThrottle):
    scope = 'order_burst'
