from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class LoginThrottle(AnonRateThrottle):
    """Limit login attempts to prevent brute force"""
    scope = 'login'

class RegisterThrottle(AnonRateThrottle):
    """Limit registration to prevent spam"""
    scope = 'register'

class PasswordResetThrottle(AnonRateThrottle):
    """Limit password reset requests"""
    scope = 'password_reset'

class CodeCheckThrottle(AnonRateThrottle):
    """Limit 2FA code attempts to prevent brute force"""
    scope = 'code_check'

class RecruiterThrottle(UserRateThrottle):
    """Limit authenticated recruiter requests to search/download endpoints"""
    scope = 'recruiter'

class AdminRateThrottle(UserRateThrottle):
    """Limit admin/staff endpoints"""
    scope = 'admin'
