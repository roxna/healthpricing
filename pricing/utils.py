from django.conf import settings
from pricing.forms import *
from pricing.models import *


# Used for method decorator @user_passes_test
def is_user(user):
    return user.user_profile

def is_doctor(user):
    return user.doctor_profile    