# accounts/utils.py

def is_admin_clerk(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin_clerk'

def is_nurse(user):
    return hasattr(user, 'profile') and user.profile.role == 'nurse'

def is_doctor(user):
    return hasattr(user, 'profile') and user.profile.role == 'doctor'

def is_admin_clerk_or_superuser(user):
    return user.is_superuser or is_admin_clerk(user)

def is_nurse_or_superuser(user):
    return user.is_superuser or is_nurse(user)

def is_doctor_or_superuser(user):
    return user.is_superuser or is_doctor(user)
