from django.core.exceptions import ValidationError
from math import ceil

from common.tests import ModelTestBase
from ..models import Claim, Giveaway


class GiveawaysTestCase(ModelTestBase):
    def setUp(self):
        super().setUp()
        self.brewer = self.create_brewer()
        self.brew = self.create_brew(self.brewer)

    def create_basic_giveaway(self, bottles_avail=10, max_incr=2):
        giveaway = Giveaway(
            creator=self.user,
            brewer=self.brewer,
            brew=self.brew,
            bottles_available=bottles_avail,
            max_increment=max_incr,
            location=self.brewer.location,
        )
        return giveaway
    
    def create_claim(self, giveaway, claim_num=2):
        claim = Claim(
            creator=self.user,
            claimer=self.brewer,
            giveaway=giveaway,
            num_bottles=claim_num,
        )
        return claim
    
    def test_basic(self):
        giveaway = self.create_basic_giveaway()
        giveaway.save()

        self.assertEqual(giveaway.status, Giveaway.StatusChoices.PENDING)

    def test_validators(self):
        with self.assertRaises(ValidationError):
            giveaway = self.create_basic_giveaway(bottles_avail=1000)
            giveaway.full_clean()

        with self.assertRaises(ValidationError):
            giveaway = self.create_basic_giveaway(bottles_avail=0)
            giveaway.full_clean()

        with self.assertRaises(ValidationError):
            giveaway = self.create_basic_giveaway(bottles_avail=10, max_incr=20)
            giveaway.full_clean()
            giveaway.save() # This one triggers on save

    def test_claim(self):
        bottles = 10
        claim_num = 2
        giveaway = self.create_basic_giveaway(bottles_avail=bottles, max_incr=2)
        giveaway.save()

        claim = self.create_claim(giveaway, claim_num=claim_num)
        claim.save()
        giveaway.refresh_from_db()
        self.assertEqual(giveaway.remaining_bottles, bottles-claim_num)

    def test_claim_more_than_avail(self):
        bottles = 10
        claim_num = 12
        giveaway = self.create_basic_giveaway(bottles_avail=bottles, max_incr=2)
        giveaway.save()

        with self.assertRaises(ValidationError):
            claim = self.create_claim(giveaway, claim_num=claim_num)
            claim.save()
    
    def test_claim_more_than_remaining(self):
        bottles = 10
        claim_num = ceil(bottles/2) + 1
        giveaway = self.create_basic_giveaway(bottles_avail=bottles, max_incr=claim_num)
        giveaway.save()

        with self.assertRaises(ValidationError):
            claim1 = self.create_claim(giveaway, claim_num=claim_num)
            claim1.save()
            claim2 = self.create_claim(giveaway, claim_num=claim_num)
            claim2.save()
