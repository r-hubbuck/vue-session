from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import hashlib

from .models import UsedToken


class OneTimeTokenMixin:
    """Mixin to add one-time use functionality to token generators"""
    
    def check_token(self, user, token):
        # First check if token is valid using parent logic
        if not super().check_token(user, token):
            return False
        
        # Check if token has already been used
        from .models import UsedToken
        token_hash = hashlib.sha256(f"{user.pk}-{token}".encode()).hexdigest()
        
        if UsedToken.objects.filter(
            user=user, 
            token_hash=token_hash, 
            token_type=self.token_type
        ).exists():
            return False
        
        return True
    
    def mark_token_used(self, user, token):
        """Mark a token as used"""
        token_hash = hashlib.sha256(f"{user.pk}-{token}".encode()).hexdigest()
        
        UsedToken.objects.get_or_create(
            user=user,
            token_hash=token_hash,
            token_type=self.token_type,
        )

class AccountActivationTokenGenerator(OneTimeTokenMixin, PasswordResetTokenGenerator):
    token_type = 'activation'
    
    def _make_hash_value(self, user: AbstractBaseUser, timestamp: int) -> str:
        return str(user.pk) + str(timestamp) + str(user.is_active)

class PasswordResetTokenGenerator(OneTimeTokenMixin, PasswordResetTokenGenerator):
    token_type = 'password_reset'
    
    def _make_hash_value(self, user: AbstractBaseUser, timestamp: int) -> str:
        return str(user.pk) + str(timestamp) + str(user.is_active)

account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()