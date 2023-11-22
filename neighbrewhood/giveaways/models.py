from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from brewers.models import Brewer
from brews.models import Brew
from common.models import CommonInfo


class Giveaway(CommonInfo):
    class StatusChoices(models.TextChoices):
        PENDING = "pending"
        OPEN = "open"
        CLOSED = "closed"
    
    brewer = models.ForeignKey(Brewer, on_delete=models.CASCADE)
    brew = models.ForeignKey(Brew, on_delete=models.CASCADE)

    bottles_available = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    max_increment = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    bottled = models.BooleanField(default=False)

    location = models.PointField()  ## For searching. Will not be displayed to drinkers
    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.PENDING)

    @property
    def bottles_claimed(self):
        num = self.claim_set.aggregate(s=models.Sum("num_bottles"))["s"]
        if num is None:
            num = 0
        return num

    @property
    def remaining_bottles(self):
        return self.bottles_available - self.bottles_claimed

    def _validate_max_increment(self):
        if self.max_increment > self.bottles_available:
            raise ValidationError("Max increment cannot be larger than available bottles")
        
    def save(self, *args, **kwargs):
        self._validate_max_increment()
        return super().save(*args, **kwargs)


class Claim(CommonInfo):
    claimer = models.ForeignKey(Brewer, on_delete=models.CASCADE)
    giveaway = models.ForeignKey(Giveaway, on_delete=models.CASCADE)
    num_bottles = models.IntegerField()

    def _validate_num_bottles(self):
        if self.num_bottles > self.giveaway.max_increment:
            raise ValidationError(f"Claim {self.num_bottles} larger than allowed max {self.giveaway.max_increment}")
        
    def _validate_enough_remaining(self):
        if self.num_bottles > self.giveaway.remaining_bottles:
            raise ValidationError("Not nough remaining bottles")
        
    def save(self, *args, **kwargs):
        self._validate_num_bottles()
        self._validate_enough_remaining()
        return super().save(*args, **kwargs)
