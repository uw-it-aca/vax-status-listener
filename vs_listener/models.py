# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models


class EnvelopeManager(models.Manager):
    def process_envelopes(self):
        """
        PUT/POST? /student/v5/person/{regid}/registrationblocks

        Upon form delivered/completed and decline/voided  (TBD)
        - student identifier (likely uwnetid)
        - "covid block reg status"
        - "document review status"
        - exemption flag [set/unset] (need reason?)
        """
        pass


class Envelope(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True)
    processed_status_code = models.CharField(max_length=3, null=True)

    objects = EnvelopeManager()
