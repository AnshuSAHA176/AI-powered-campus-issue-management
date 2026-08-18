from django.contrib.auth.base_user import BaseUserManager

class Customemanager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            
            raise ValueError("Users must have a valid email address.")
        user=self.model(
            email=self.normalize_email
            (email)
            ,**kwargs
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**kwargs):
        user=self.create_user(email=email,password=password,**kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user