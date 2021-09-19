# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.views import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from vs_listener.models import Recipient
import hmac
import hashlib
import json


@method_decorator(csrf_exempt, name='dispatch')
class ListenerView(View):
    def verify_signature(self, request):
        h = hmac.new(getattr(settings, 'DOCUSIGN_CONNECT_SECRET', b''),
                     msg=request.body,
                     digestmod=hashlib.sha256)

        digest = 'sha256={}'.format(h.hexdigest())

        # https://developers.docusign.com/platform/webhooks/connect/validate/
        # TODO: might need to compare against multiple headers, _1, _2, etc
        signature = request.META.get('HTTP_X_DOCUSIGN_SIGNATURE_1', '')

        return hmac.compare_digest(digest, signature)

    def post(self, request, *args, **kwargs):
        # Verify message signature
        if not self.verify_signature(request):
            return HttpResponse('Invalid signature', status=403)

        try:
            data = json.loads(request.body)
        except Exception as ex:
            return HttpResponse('{}'.format(ex), status=400)

        return HttpResponse(status=200)
