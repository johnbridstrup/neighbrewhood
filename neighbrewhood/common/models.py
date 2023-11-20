from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class CommonInfo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="%(class)s_creator")
    updated = models.DateTimeField(auto_now=True)
    updater = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="%(class)s_updater")

    class Meta:
        abstract = True
