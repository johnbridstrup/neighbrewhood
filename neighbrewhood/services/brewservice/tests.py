from datetime import date
from django.urls import reverse_lazy
from requests.status_codes import codes
from services.testing.ServiceTestBase import ServiceTestBase


class BrewServiceTestCase(ServiceTestBase):
    def setUp(self):
        super().setUp()
        brew_type_strs = ["IPA", "Lager"]
        qlty_strs = ["Hoppy", "Dark"]

        self.qualities = self.create_qualities(qlty_strs)
        self.brew_types = self.create_brew_types(brew_type_strs)

    def test_create_brew(self):
        self.register_user()
        self.obtain_access_token()
        crt_brewer_url = reverse_lazy("api-1.0.0:users_create_brewer")
        self.post(crt_brewer_url, self.brewer_details)
        
        ## User sees available brew types
        qlty_url = reverse_lazy("api-1.0.0:brew_qualities")
        bt_url = reverse_lazy("api-1.0.0:brew_brew_types")

        bt_r = self.get(qlty_url)
        self.assertEqual(bt_r.status_code, codes.ok)
        qlty_r = self.get(bt_url)
        self.assertEqual(qlty_r.status_code, codes.ok)

        # User selects a brew type and a few qualities
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
        self.assertEqual(r.status_code, codes.created)

        my_brews_url = reverse_lazy("api-1.0.0:brew_my_brews")
        r = self.get(my_brews_url)
        self.assertEqual(r.status_code, codes.ok)
        self.assertGreater(len(r.json()['items']), 0)
