import jsonschema

from datetime import date
from django.contrib.gis.geos import Point
from django.urls import reverse_lazy
from requests.status_codes import codes
from brewswaps.models import BrewSwapStatusChoices, ClaimStatusChoices
from services.testing.ServiceTestBase import ServiceTestBase


class BrewSwapServiceTestCase(ServiceTestBase):
    def setUp(self):
        super().setUp()
        brew_type_strs = ["IPA", "Lager"]
        qlty_strs = ["Hoppy", "Dark"]

        self.qualities = self.create_qualities(qlty_strs)
        self.brew_types = self.create_brew_types(brew_type_strs)

        self.register_user()
        self.obtain_access_token()
        self.create_brewer()
    
    def create_brewer(self, location=None):
        if location is not None:
            self.brewer_details["location_str"] = location
        crt_brewer_url = reverse_lazy("api-1.0.0:users_create_brewer")
        return self.post(crt_brewer_url, self.brewer_details)

    def create_brew(self):
        qlty_url = reverse_lazy("api-1.0.0:brew_qualities")
        bt_url = reverse_lazy("api-1.0.0:brew_brew_types")
        bt_r = self.get(qlty_url)
        qlty_r = self.get(bt_url)
        bt = bt_r.json()['items'][0]['id']
        qts = [q["id"] for q in qlty_r.json()['items']]

        today = date.today()
        brew_data = {
            "brew_type": bt,
            "qualities": qts,
            "start_date": str(today),
            "notes": "Some notes about the brew"
        }

        create_brew_url = reverse_lazy("api-1.0.0:brew_create_brew")
        r = self.post(create_brew_url, brew_data)
        return r
    
    def create_swap(self, brew_id, total_bottles=24, max_increment=12):
        crt_swap_url = reverse_lazy("api-1.0.0:brewswaps_create_swap")
        swap_data = {
            "brew": brew_id,
            "total_bottles": total_bottles,
            "max_increment": max_increment,
        }

        r = self.post(crt_swap_url, swap_data)
        return r

    def test_create_swap_basic(self):
        r = self.create_brew()
        brew_id = r.json()['id']

        r = self.create_swap(brew_id)
        self.assertEqual(r.status_code, codes.created)

        my_swaps_url = reverse_lazy("api-1.0.0:brewswaps_my_swaps")
        r = self.get(my_swaps_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(len(r.json()), 1)

        # SET ACTIVE
        swap = r.json()

        # Select a swap
        det_url = swap[0]["detail"]["url"]

        # View the swap 
        r = self.get(det_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(r.json()["status"], BrewSwapStatusChoices.INACTIVE)

        # Set live
        setlive_url = r.json()["actions"]["set_live"]["url"]
        r = self.get(setlive_url)
        self.assertEqual(r.status_code, codes.ok)

        # Verify
        r = self.get(det_url)
        self.assertEqual(r.json()["status"], BrewSwapStatusChoices.LIVE)

    
    def test_my_swaps(self):
        # Create swap for one user
        r = self.create_brew()
        
        brew_id = r.json()["id"]
        r = self.create_swap(brew_id)
        self.assertEqual(r.status_code, codes.created)

        # Check one swap exists for first user
        my_swaps_url = reverse_lazy("api-1.0.0:brewswaps_my_swaps")
        r = self.get(my_swaps_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(len(r.json()), 1)
        
        # Create swap for another user
        username_2 = "another_user"
        email_2 = "another@user.com"

        self.register_user(username=username_2, email=email_2)
        self.obtain_access_token(username=username_2)
        self.create_brewer()

        r = self.create_brew()
        brew_id = r.json()["id"]
        r = self.create_swap(brew_id)
        self.assertEqual(r.status_code, codes.created)

        # Check one swap exists for second user
        my_swaps_url = reverse_lazy("api-1.0.0:brewswaps_my_swaps")
        r = self.get(my_swaps_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(len(r.json()), 1)

    def test_basic_swap_flow(self):
        r = self.create_brew()
        
        brew_id = r.json()["id"]
        r = self.create_swap(brew_id)
        self.assertEqual(r.status_code, codes.created)

        # Set live
        swap = r.json()
        det_url = swap["detail"]["url"]
        r = self.get(det_url)
        setlive_url = r.json()["actions"]["set_live"]["url"]
        self.get(setlive_url)

        # Create swap for another user far away
        far_username = "far_away_user"
        far_email = "another@user.com"

        self.register_user(username=far_username, email=far_email)
        self.obtain_access_token(username=far_username)

        location = Point(80, -60, srid=4326) # Really far away
        self.create_brewer(str(location))
        r = self.create_brew()
        brew_id = r.json()["id"]
        r = self.create_swap(brew_id)
        self.assertEqual(r.status_code, codes.created)

        # Set live
        swap = r.json()
        det_url = swap["detail"]["url"]
        r = self.get(det_url)
        setlive_url = r.json()["actions"]["set_live"]["url"]
        self.get(setlive_url)

        # Check total number of swaps
        swp_url = reverse_lazy("api-1.0.0:brewswaps_swaps")
        r = self.get(swp_url)
        total = len(r.json())

        # Create user near user 1
        near_username = "nearby_user"
        near_email = "another@user.com"

        self.register_user(username=near_username, email=near_email)
        self.obtain_access_token(username=near_username)
        self.create_brewer(str(self.loc))

        nearby_url = reverse_lazy("api-1.0.0:brewswaps_nearby_swaps")
        r = self.get(nearby_url)
        self.assertEqual(r.status_code, codes.ok)
        nearby = len(r.json())

        self.assertLess(nearby, total)
        self.assertGreater(nearby, 0)

        # Make a claim 0: Choose a swap
        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        claim_url = r.json()["actions"]["make_claim"]["url"]
        claim_schema = r.json()["actions"]["make_claim"]["schema"]

        # Make a claim 1: create brew
        r = self.create_brew()
        brew_id = r.json()["id"]
        
        # Make a claim 2: submit claim on swap
        claim_data = {
            "brew": brew_id,
            "num_bottles": 6,
        }
        try:
            jsonschema.validate(claim_data, claim_schema)
        except jsonschema.ValidationError as e:
            assert False, str(e)
        
        r = self.post(claim_url, claim_data)

        self.assertEqual(r.status_code, codes.created)
        self.assertEqual(r.json()["status"], ClaimStatusChoices.PENDING)

        # See my claims
        myclaims_url = reverse_lazy("api-1.0.0:claims_my_claims")
        r = self.get(myclaims_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(len(r.json()["items"]), 1)

        # Orig user views and accepts swap
        self.obtain_access_token()

        # View my swaps
        my_swaps_url = reverse_lazy("api-1.0.0:brewswaps_my_swaps")
        r = self.get(my_swaps_url)
        self.assertEqual(r.json()[0]["claims"], 1)

        # Get detail for one of them
        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        
        # See claims
        get_claims_url = r.json()["actions"]["get_claims"]["url"]
        r = self.get(get_claims_url)
        self.assertEqual(r.status_code, codes.ok)

        # Accept claim
        accept_url = r.json()[0]["actions"]["accept"]["url"]
        r = self.get(accept_url)
        self.assertEqual(r.status_code, codes.ok)

        # Verify accepted
        r = self.get(get_claims_url)
        claim = r.json()[0]
        self.assertEqual(claim["status"], ClaimStatusChoices.ACCEPTED)

    def test_not_enough_bottles(self):
        # create and set live
        r = self.create_brew()
        brew_id = r.json()["id"]
        total_bottles = 8
        max_inc = 5
        self.assertGreater(2*max_inc, total_bottles) # Just in case I forget...

        r = self.create_swap(brew_id, total_bottles=total_bottles, max_increment=max_inc)
        self.assertEqual(r.status_code, codes.created)

        swap = r.json()
        det_url = swap["detail"]["url"]
        r = self.get(det_url)
        setlive_url = r.json()["actions"]["set_live"]["url"]
        self.get(setlive_url)

        ## User 1 claims
        user1 = "user1"
        user1_email = "another@user.com"

        self.register_user(username=user1, email=user1_email)
        self.obtain_access_token(username=user1)
        self.create_brewer(str(self.loc))

        # get nearby
        nearby_url = reverse_lazy("api-1.0.0:brewswaps_nearby_swaps")
        r = self.get(nearby_url)
        self.assertEqual(r.status_code, codes.ok)

        # Choose and claim
        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        claim_url = r.json()["actions"]["make_claim"]["url"]

        r = self.create_brew()
        brew_id = r.json()["id"]
        
        claim_data = {
            "brew": brew_id,
            "num_bottles": max_inc,
        }
        r = self.post(claim_url, claim_data)
        self.assertEqual(r.status_code, codes.created)

        # Claim accepted
        self.obtain_access_token()
        my_swaps_url = reverse_lazy("api-1.0.0:brewswaps_my_swaps")
        r = self.get(my_swaps_url)
        self.assertEqual(r.json()[0]["claims"], 1)

        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        
        get_claims_url = r.json()["actions"]["get_claims"]["url"]
        r = self.get(get_claims_url)
        self.assertEqual(r.status_code, codes.ok)

        accept_url = r.json()[0]["actions"]["accept"]["url"]
        r = self.get(accept_url)
        self.assertEqual(r.status_code, codes.ok)

        # User 2 tries to claim more than remaining
        user2 = "user2"
        user2_email = "another@user.com"

        self.register_user(username=user2, email=user2_email)
        self.obtain_access_token(username=user2)
        self.create_brewer(str(self.loc))

        # get nearby
        nearby_url = reverse_lazy("api-1.0.0:brewswaps_nearby_swaps")
        r = self.get(nearby_url)
        self.assertEqual(r.status_code, codes.ok)

        # Choose and claim
        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        claim_url = r.json()["actions"]["make_claim"]["url"]

        r = self.create_brew()
        brew_id = r.json()["id"]
        
        claim_data = {
            "brew": brew_id,
            "num_bottles": max_inc, # there should not be 5 remaining
        }
        r = self.post(claim_url, claim_data)
        self.assertEqual(r.status_code, codes.bad)
        self.assertEqual(r.json()["detail"], f"Only {total_bottles-max_inc} left")

    def test_cant_accept_over_max(self):
        r = self.create_brew()
        total_bottles = 8
        max_inc = 5
        self.assertGreater(2*max_inc, total_bottles) # Just in case I forget...
        
        brew_id = r.json()["id"]
        r = self.create_swap(brew_id, total_bottles, max_inc)
        self.assertEqual(r.status_code, codes.created)

        # Set live
        swap = r.json()
        det_url = swap["detail"]["url"]
        r = self.get(det_url)
        setlive_url = r.json()["actions"]["set_live"]["url"]
        self.get(setlive_url)

        ## User 1 claims
        user1 = "user1"
        user1_email = "another@user.com"

        self.register_user(username=user1, email=user1_email)
        self.obtain_access_token(username=user1)
        self.create_brewer(str(self.loc))

        # get nearby
        nearby_url = reverse_lazy("api-1.0.0:brewswaps_nearby_swaps")
        r = self.get(nearby_url)
        self.assertEqual(r.status_code, codes.ok)

        # Choose and claim
        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        claim_url = r.json()["actions"]["make_claim"]["url"]

        r = self.create_brew()
        brew_id = r.json()["id"]
        
        claim_data = {
            "brew": brew_id,
            "num_bottles": max_inc,
        }
        r = self.post(claim_url, claim_data)
        self.assertEqual(r.status_code, codes.created)

        # User 2 tries to claim more than remaining
        user2 = "user2"
        user2_email = "another@user.com"

        self.register_user(username=user2, email=user2_email)
        self.obtain_access_token(username=user2)
        self.create_brewer(str(self.loc))

        # get nearby
        nearby_url = reverse_lazy("api-1.0.0:brewswaps_nearby_swaps")
        r = self.get(nearby_url)
        self.assertEqual(r.status_code, codes.ok)

        # Choose and claim
        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        claim_url = r.json()["actions"]["make_claim"]["url"]

        r = self.create_brew()
        brew_id = r.json()["id"]
        
        claim_data = {
            "brew": brew_id,
            "num_bottles": max_inc,
        }
        r = self.post(claim_url, claim_data)

        # Try to accept both
        self.obtain_access_token()
        my_swaps_url = reverse_lazy("api-1.0.0:brewswaps_my_swaps")
        r = self.get(my_swaps_url)
        self.assertEqual(r.json()[0]["claims"], 2)

        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        get_claims_url = r.json()["actions"]["get_claims"]["url"]
        r = self.get(get_claims_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(len(r.json()), 2)

        # First claim should work
        accept_url_1 = r.json()[0]["actions"]["accept"]["url"]
        acc_r_1 = self.get(accept_url_1)
        self.assertEqual(acc_r_1.status_code, codes.ok) # works

        # Second claim should not
        accept_url_2 = r.json()[1]["actions"]["accept"]["url"]
        acc_r_2 = self.get(accept_url_2)
        self.assertEqual(acc_r_2.status_code, codes.bad)
        self.assertEqual(acc_r_2.json()["detail"], "Not enough bottles available")

    def test_cancel_claim(self):
        r = self.create_brew()
        brew_id = r.json()["id"]
        r = self.create_swap(brew_id)
        self.assertEqual(r.status_code, codes.created)

        # Set live
        swap = r.json()
        det_url = swap["detail"]["url"]
        r = self.get(det_url)
        setlive_url = r.json()["actions"]["set_live"]["url"]
        self.get(setlive_url)

        ## User 1 claims
        user1 = "user1"
        user1_email = "another@user.com"

        self.register_user(username=user1, email=user1_email)
        self.obtain_access_token(username=user1)
        self.create_brewer(str(self.loc))

        # get nearby
        nearby_url = reverse_lazy("api-1.0.0:brewswaps_nearby_swaps")
        r = self.get(nearby_url)
        self.assertEqual(r.status_code, codes.ok)

        # Choose and claim
        det_url = r.json()[0]["detail"]["url"]
        r = self.get(det_url)
        claim_url = r.json()["actions"]["make_claim"]["url"]

        r = self.create_brew()
        brew_id = r.json()["id"]
        
        claim_data = {
            "brew": brew_id,
            "num_bottles": 5,
        }
        r = self.post(claim_url, claim_data)
        self.assertEqual(r.status_code, codes.created)

        # Cancel the claim
        cancel_url = r.json()["actions"]["cancel"]["url"]
        r = self.get(cancel_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(r.json()["message"], "Claim canceled")
