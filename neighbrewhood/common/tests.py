from collections import Iterable
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
    
    def create_brew_types(self, brew_types=("IPA",)):
        if not isinstance(brew_types, Iterable):
            brew_types = [brew_types]
        brtype_objs = []
        for bt in brew_types:
            btype = BrewType(value=bt, creator=self.user)
            btype.save()
            brtype_objs.append(btype)
        return brtype_objs

    def create_qualities(self, qualities=("spicy",)):
        if not isinstance(qualities, Iterable):
            qualities = [qualities]
        qlty_objs = []
        for quality in qualities:
            q = Quality(value=quality, creator=self.user)
            q.save()
            qlty_objs.append(q)
        return qlty_objs

    def create_brew(self, brewtype="IPA", qualities=("spicy",)):
        btype = self.create_brew_types(brewtype)[0]

        qlty_objs = self.create_qualities(qualities)
        
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
