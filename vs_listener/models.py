# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from dateutil.parser import parse
from uw_pws import PWS, InvalidNetID


class User(models.Model):
    email = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.email

    @property
    def uwnetid(self):
        return self.email.split('@')[0]

    @cached_property
    def uwregid(self):
        return PWS().get_person_by_netid(self.uwnetid).uwregid

    @staticmethod
    def valid_email(email):
        try:
            (username, domain) = email.split('@')
            if (PWS().valid_uwnetid(username) and
                    domain in getattr(settings, 'EMAIL_DOMAINS', [])):
                return True
        except (AttributeError, ValueError):
            pass
        return False


class EnvelopeManager(models.Manager):
    def add_envelope(self, data):
        for signer in data.get('recipients', {}).get('signers', []):
            role = signer.get('roleName', '').lower()
            email = signer.get('email', '')
            if (role == Envelope.VALID_ROLE and User.valid_email(email)):
                user, _ = User.objects.get_or_create(email=email)
                envelope = Envelope(user=user, status=data.get('status'))
                envelope.reason = 'hmm'
                envelope.guid = data.get('envelopeId')
                envelope.status_changed_date = parse(
                    data.get('statusChangedDateTime'))
                # envelope.save()
                return envelope

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
    STATUS_CHOICES = (
       ('signed', 'signed'),
       ('completed', 'completed'),
       ('declined', 'declined'),
       ('voided', 'voided')
    )
    VALID_STATUS = [s[0] for s in STATUS_CHOICES]
    VALID_ROLE = 'student'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.SlugField(max_length=12, choices=STATUS_CHOICES)
    reason = models.CharField(max_length=64)
    status_changed_date = models.DateTimeField()
    guid = models.CharField(max_length=64, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True)
    processed_status_code = models.CharField(max_length=3, null=True)

    objects = EnvelopeManager()

    def __str__(self):
        return '{}, {}, {}'.format(self.user, self.status, self.reason)
