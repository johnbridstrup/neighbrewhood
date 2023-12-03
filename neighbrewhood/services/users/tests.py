from django.urls import reverse_lazy
from requests.status_codes import codes

from services.testing.ServiceTestBase import ServiceTestBase


class UsersServicetestCase(ServiceTestBase):
    def test_register_view_me(self):
        reg_r = self.register_user()
        self.assertEqual(reg_r.status_code, codes.created)
        
        self.obtain_access_token()

        me_url = reverse_lazy("api-1.0.0:users_me")
        me_r = self.get(me_url)
        self.assertEqual(me_r.status_code, codes.ok)

        self.assertDictContainsSubset(me_r.json(), self.user_details)

    def test_create_brewer(self):
        self.register_user()
        self.obtain_access_token()

        crt_brewer_url = reverse_lazy("api-1.0.0:users_create_brewer")

        r = self.post(crt_brewer_url, self.brewer_details)
        self.assertEqual(r.status_code, codes.created)

        d = r.json()
        self.assertDictContainsSubset(r.json()["user"], self.user_details)
        self.assertDictContainsSubset(self.brewer_details, d)
        self.assertTrue(d["can_claim"])

        prof_url = reverse_lazy("api-1.0.0:users_profile")
        prof_r = self.get(prof_url)
        self.assertEqual(prof_r.status_code, codes.ok)
