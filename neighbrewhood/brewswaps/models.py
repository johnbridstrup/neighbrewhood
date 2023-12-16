from django.db import models

from brews.models import Brew
from common.models import CommonInfo


class BrewSwapStatusChoices(models.TextChoices):
    Live = "Live"
    COMPLETE = "Complete"
    INACTIVE = "Inactive"


class ClaimStatusChoices(models.TextChoices):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

class BrewSwap(CommonInfo):
    MAX_BOTTLES = 100  # This is mostly troll prevention

    brew = models.OneToOneField(Brew, on_delete=models.CASCADE, related_name="swap")
    status = models.TextField(choices=BrewSwapStatusChoices.choices, default=BrewSwapStatusChoices.INACTIVE)
    total_bottles = models.IntegerField()
    max_increment = models.IntegerField(default=6)

    @property
    def bottles_available(self):
        claimed = self.claims.filter(status=ClaimStatusChoices.ACCEPTED).aggregate(models.Sum("num_bottles"))["num_bottles__sum"]
        if not claimed:
            return self.total_bottles
        return self.total_bottles - claimed
    
    def set_live(self):
        if self.status == BrewSwapStatusChoices.Live:
            return "Swap is already live"
        self.status = BrewSwapStatusChoices.LIVE
        self.save()
        return "Swap is now active"
    
    def set_inactive(self):
        if not self.status == BrewSwapStatusChoices.INACTIVE:
            return "Swap is already inactive"
        self.status = BrewSwapStatusChoices.INACTIVE
        self.save()
        return "Swap is now inactive"

    def set_complete(self):
        if not self.status == BrewSwapStatusChoices.COMPLETE:
            return "Swap is already complete"
        self.status = BrewSwapStatusChoices.COMPLETE
        self.save()
        return "Swap is now complete"
    

class SwapClaim(CommonInfo):
    brew = models.OneToOneField(Brew, on_delete=models.CASCADE)
    swap = models.ForeignKey(BrewSwap, on_delete=models.SET_NULL, null=True, blank=True, related_name="claims")
    num_bottles = models.IntegerField()
    status = models.TextField(choices=ClaimStatusChoices.choices, default=ClaimStatusChoices.PENDING)
