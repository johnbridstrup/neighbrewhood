from django.db import models

from brews.models import Brew
from common.models import CommonInfo


class BrewSwapStatusChoices(models.TextChoices):
    LIVE = "Live"
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
    
    @property
    def is_live(self):
        return self.status == BrewSwapStatusChoices.LIVE
    
    def set_live(self):
        if self.status == BrewSwapStatusChoices.LIVE:
            return "Swap is already live"
        self.status = BrewSwapStatusChoices.LIVE
        self.save()
        return "Swap is now active"
    
    @property
    def is_inactive(self):
        return self.status == BrewSwapStatusChoices.INACTIVE
    
    def set_inactive(self):
        if self.status == BrewSwapStatusChoices.INACTIVE:
            return "Swap is already inactive"
        self.status = BrewSwapStatusChoices.INACTIVE
        self.save()
        return "Swap is now inactive"
    
    @property
    def is_complete(self):
        return self.status == BrewSwapStatusChoices.COMPLETE

    def set_complete(self):
        if self.status == BrewSwapStatusChoices.COMPLETE:
            return "Swap is already complete"
        self.status = BrewSwapStatusChoices.COMPLETE
        self.save()
        return "Swap is now complete"
    

class SwapClaim(CommonInfo):
    brew = models.OneToOneField(Brew, on_delete=models.CASCADE)
    swap = models.ForeignKey(BrewSwap, on_delete=models.SET_NULL, null=True, blank=True, related_name="claims")
    num_bottles = models.IntegerField()
    status = models.TextField(choices=ClaimStatusChoices.choices, default=ClaimStatusChoices.PENDING)

    def accept(self):
        if self.status == ClaimStatusChoices.ACCEPTED:
            return "Claim already accepted"
        self.status = ClaimStatusChoices.ACCEPTED
        self.save()
        return "Claim accepted"
    
    def reject(self):
        if self.status == ClaimStatusChoices.REJECTED:
            return "Claim already rejected"
        self.status = ClaimStatusChoices.REJECTED
        self.save()
        return "Claim rejected"
