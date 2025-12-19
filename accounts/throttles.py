from rest_framework.throttling import AnonRateThrottle

class LoginThrottle(AnonRateThrottle):
    """Limit login attempts to prevent brute force"""
    scope = 'sensitive'
    rate = '5/minute'

class RegisterThrottle(AnonRateThrottle):
    """Limit registration to prevent spam"""
    scope = 'sensitive'
    rate = '3/hour'

class PasswordResetThrottle(AnonRateThrottle):
    """Limit password reset requests"""
    scope = 'sensitive'
    rate = '3/hour'