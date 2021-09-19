# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import RequestFactory, TestCase
from vs_listener.views import APIView


class APIViewTest(TestCase):
    def test_missing_secret(self):
        request = RequestFactory().post('/listener')
        response = APIView.as_view()(request)
        self.assertEqual(response.status_code, 403)
