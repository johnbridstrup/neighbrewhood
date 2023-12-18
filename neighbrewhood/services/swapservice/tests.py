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

    def test_create_swap_basic(self):
        self.create_brewer()
        r = self.create_brew()
        brew_id = r.json()['id']

        crt_swap_url = reverse_lazy("api-1.0.0:brewswaps_create_swap")
        swap_data = {
            "brew": brew_id,
            "total_bottles": 24,
            "max_increment": 12,
        }

        r = self.post(crt_swap_url, swap_data)
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
        self.create_brewer()
        r = self.create_brew()
        
        brew_id = r.json()["id"]
        crt_swap_url = reverse_lazy("api-1.0.0:brewswaps_create_swap")
        swap_data = {
            "brew": brew_id,
            "total_bottles": 24,
            "max_increment": 12,
        }
        r = self.post(crt_swap_url, swap_data)
        self.assertEqual(r.status_code, codes.created)

        # Check one swap exists for first user
        my_swaps_url = reverse_lazy("api-1.0.0:brewswaps_my_swaps")
        r = self.get(my_swaps_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(len(r.json()), 1)
        
        # Create swap for another user
        self.username = "another_user"
        self.user_details["username"] = self.username
        self.user_details["email"] = "another@user.com"

        self.register_user()
        self.obtain_access_token()
        self.create_brewer()

        r = self.create_brew()
        brew_id = r.json()["id"]
        swap_data = {
            "brew": brew_id,
            "total_bottles": 24,
            "max_increment": 12,
        }
        r = self.post(crt_swap_url, swap_data)
        self.assertEqual(r.status_code, codes.created)

        # Check one swap exists for second user
        my_swaps_url = reverse_lazy("api-1.0.0:brewswaps_my_swaps")
        r = self.get(my_swaps_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertEqual(len(r.json()), 1)

    def test_nearby_basic(self):
        self.create_brewer()
        r = self.create_brew()
        
        brew_id = r.json()["id"]
        crt_swap_url = reverse_lazy("api-1.0.0:brewswaps_create_swap")
        swap_data = {
            "brew": brew_id,
            "total_bottles": 24,
            "max_increment": 12,
        }
        r = self.post(crt_swap_url, swap_data)
        self.assertEqual(r.status_code, codes.created)

        # Set live
        swap = r.json()
        det_url = swap["detail"]["url"]
        r = self.get(det_url)
        setlive_url = r.json()["actions"]["set_live"]["url"]
        self.get(setlive_url)

        # Create swap for another user far away
        self.username = "far_away_user"
        self.user_details["username"] = self.username
        self.user_details["email"] = "another@user.com"

        self.register_user()
        self.obtain_access_token()

        location = Point(80, -60, srid=4326) # Really far away
        self.create_brewer(str(location))
        r = self.create_brew()
        brew_id = r.json()["id"]
        swap_data = {
            "brew": brew_id,
            "total_bottles": 24,
            "max_increment": 12,
        }
        r = self.post(crt_swap_url, swap_data)
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
        self.username = "nearby_user"
        self.user_details["username"] = self.username
        self.user_details["email"] = "another@user.com"

        self.register_user()
        self.obtain_access_token()
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
