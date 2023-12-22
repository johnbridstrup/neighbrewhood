# TestBase class for service tests
from django.contrib.gis.geos import Point
from django.test import Client
from django.urls import reverse_lazy
from requests.status_codes import codes

from common.tests import ModelTestBase


class ServiceTestBase(ModelTestBase):
    CONTENT_TYPE = "application/json"

    def setUp(self):
        super().setUp()
        self.username = "service_tester"
        self.password = "Testing123!"
        self.email = "testing@test.com"
        self.first_name = "Test"
        self.last_name = "Er"
        self.user_details = {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }
        self.loc = Point(38.518681, -121.498772, srid=4326)
        self.brewer_details = {
            "location_str": str(self.loc),
            "phone_number": "+15402725555",
        }
        self.access = None
        self.refresh = None
        self.headers = {}
        self._client = Client()

    def post(self, url, data, xtra_headers=None, auth=False):
        if xtra_headers is not None:
            self.headers.update(xtra_headers)
        if auth:
            self.headers.update(self.access_header)
        return self._client.post(url, data=data, headers=self.headers, content_type=self.CONTENT_TYPE)
    
    def get(self, url, xtra_headers=None):
        if xtra_headers is not None:
            self.headers.update(xtra_headers)
        return self._client.get(url, headers=self.headers)
    
    @property
    def token_pair_url(self):
        return "/api/token/pair"
    
    @property
    def token_verify_url(self):
        return "/api/token/verify"
    
    @property
    def token_refresh_url(self):
        return "/api/token/refresh"
    
    @property
    def access_header(self):
        return {"Authorization": f"bearer {self.access}"}
    
    def request_token_pair(self, username, password):
        d = {
            "username": username or self.username,
            "password": password or self.password,
        }
        r = self.post(self.token_pair_url, data=d)
        self.assertEqual(r.status_code, codes.ok, r.json())
        return r
    
    def _set_access_header(self, token_pair):
        self.access = token_pair.get("access")
        self.refresh = token_pair.get("refresh")
        assert self.access, "No access token"
        assert self.refresh, "No refresh token"

        verify_data = {"token": self.access}
        r = self.post(self.token_verify_url, data=verify_data)
        self.assertEqual(r.status_code, codes.ok, "Token Invalid")

        self.headers.update({
            "Authorization": f"bearer {self.access}",
        })

    def refresh_access_header(self, token_pair):
        assert self.refresh, "No refresh token"

        refresh_data = {"refresh": self.access}
        r = self.post(self.token_refresh_url, data=refresh_data)
        self.assertEqual(r.status_code, codes.ok, "Refresh Token Invalid")

        self._set_access_header(r.json())

    def register_user(self, username=None, password=None, email=None, first=None, last=None):
        user_details = {
            "username": username or self.username,
            "password": password or self.password,
            "email": email or self.email,
            "first_name": first or self.first_name,
            "last_name": last or self.last_name,
        }
        reg_url = reverse_lazy("api-1.0.0:users_register")
        r = self.client.post(reg_url, data= user_details, content_type="application/json")
        self.assertEqual(r.status_code, codes.created)
        
        return r
    
    def obtain_access_token(self, username=None, password=None):
        token_r = self.request_token_pair(username, password)
        self.assertEqual(token_r.status_code, codes.ok, token_r.json())

        self._set_access_header(token_r.json())
    
    
