from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone

from brewers.models import Brewer
from brews.models import Brew, BrewType, Quality


class ModelTestBase(TestCase):
    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.user = User.objects.create(username="test")

    def create_brewer(self):
        loc = Point(38.518681, -121.498772)
        brewer = Brewer(
            creator = self.user,
            user = self.user,
            location = loc,
            phone_number = "+15405551212",
        )
        brewer.save()
        return brewer  

    def create_brew(self, brewtype="IPA", qualities=("spicy",)):
        btype = BrewType(value=brewtype, creator=self.user)
        btype.save()

        qlty_objs = []
        for quality in qualities:
            q = Quality(value=quality, creator=self.user)
            q.save()
            qlty_objs.append(q)
        
        brew = Brew(
            creator=self.user,
            brew_type=btype,
            start_date=timezone.now() - timezone.timedelta(days=-10),
            completion_date=timezone.now(),
            notes="big hops",
        )
        brew.save()
        brew.qualities.set(qlty_objs)
        return brew
