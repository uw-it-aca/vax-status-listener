# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.views import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from vs_listener.models import Envelope
from vs_listener.metrics import (
    notification_counter, notification_invalid_counter,
    notification_status_ignored_counter, notification_status_counter)
import hmac
import hashlib
import json
import base64


@method_decorator(csrf_exempt, name='dispatch')
class ListenerView(View):
    def verify_signature(self, request):
        hash_bytes = hmac.new(
            getattr(settings, 'DOCUSIGN_CONNECT_SECRET', b''),
            msg=request.body,
            digestmod=hashlib.sha256).digest()

        b64hash = base64.b64encode(hash_bytes)

        # https://developers.docusign.com/platform/webhooks/connect/validate/
        for i in range(1, 25):
            try:
                signature_key = 'HTTP_X_DOCUSIGN_SIGNATURE_{}'.format(i)
                signature = request.META[signature_key].encode('utf_8')
                if hmac.compare_digest(signature, b64hash):
                    return True
            except KeyError:
                break

        return False

    def post(self, request, *args, **kwargs):
        notification_counter()

        if not self.verify_signature(request):
            notification_invalid_counter()
            return HttpResponse('Invalid signature', status=403)

        try:
            data = json.loads(request.body)
        except Exception as ex:
            return HttpResponse('{}'.format(ex), status=400)

        envelope = Envelope.objects.add_envelope(data)
        if envelope is not None:
            notification_status_counter(envelope.status)
        else:
            notification_status_ignored_counter(data.get('status'))

        return HttpResponse(status=200)
