from typing import Any
from django.db import models
from common.models import CommonInfo


class Quality(CommonInfo):
    value = models.CharField(max_length=31)

    def __str__(self):
        return self.value


class BrewType(CommonInfo):
    value = models.CharField(max_length=31)

    def __str__(self):
        return self.value


class Brew(CommonInfo):
    brew_type = models.ForeignKey(BrewType, on_delete=models.CASCADE)
    qualities = models.ManyToManyField(Quality)
    start_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    @property
    def brewer(self):
        return self.creator  ## TODO: FIX THIS. brewer should be a OneToOne with Brewer. creator and brewer can be different
    
    def is_brewed_by(self, user):
        if self.creator == user:
            return True
        return False
