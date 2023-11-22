from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from brewers.models import Brewer
from brews.models import Brew
from common.models import CommonInfo


class Rating(CommonInfo):
    rater = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.BooleanField()
    review = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class BrewerRating(Rating):
    brewer = models.ForeignKey(Brewer, on_delete=models.CASCADE, related_name="brewer_ratings")


class BrewRating(Rating):
    brew = models.ForeignKey(Brew, on_delete=models.CASCADE, related_name="brew_ratings")
