from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from phonenumber_field.modelfields import PhoneNumberField
from common.models import CommonInfo


User = get_user_model()


class Brewer(CommonInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.PointField()  ## Will not be displayed to other users
    phone_number = PhoneNumberField()
    can_claim = models.BooleanField(default=True)  ## Brewer makes claim, cant again until review
