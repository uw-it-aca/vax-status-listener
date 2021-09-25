# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.db.models import Q
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
        if not Envelope.valid_status(data.get('status')):
            return

        for signer in data.get('recipients', {}).get('signers', []):
            if (not Envelope.valid_role(signer.get('roleName', '')) or
                    not User.valid_email(signer.get('email', ''))):
                continue

            user, _ = User.objects.get_or_create(email=signer.get('email'))

            guid = data.get('envelopeId')
            envelope, _ = Envelope.objects.get_or_create(guid=guid, defaults={
                'user': user,
                'status': data.get('status'),
                'form_name': data.get('powerForm', {}).get('name'),
                'status_changed_date': parse(
                    data.get('statusChangedDateTime')),
            })
            return envelope

    def process_envelopes(self):
        """
        PUT/POST? /student/v5/person/{regid}/registrationblocks

        Upon form delivered/completed and decline/voided  (TBD)
        - student identifier (likely uwnetid)
        - "covid block reg status"
        - "document review status"
        - exemption flag [set/unset]
        """
        envelopes = super(EnvelopeManager, self).get_queryset().filter(
            Q(processed_date__isnull=True) | ~Q(processed_status_code=200)
        ).order_by('created_date')

        for envelope in envelopes:
            envelope.update_sws()


class Envelope(models.Model):
    STATUS_CHOICES = (
       ('signed', 'signed'),
       ('completed', 'completed'),
       ('declined', 'declined'),
       ('voided', 'voided')
    )
    VALID_STATUS = [s[0] for s in STATUS_CHOICES]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.SlugField(max_length=12, choices=STATUS_CHOICES)
    form_name = models.CharField(max_length=100)
    status_changed_date = models.DateTimeField()
    guid = models.CharField(max_length=36, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True)
    processed_status_code = models.CharField(max_length=3, null=True)

    objects = EnvelopeManager()

    def __str__(self):
        return 'user: {}, status: {}, form_name: {}'.format(
            self.user, self.status, self.form_name)

    def update_sws(self):
        pass

    @staticmethod
    def valid_status(status):
        return status.lower() in Envelope.VALID_STATUS

    @staticmethod
    def valid_role(role):
        return role.lower() in getattr(settings, 'SIGNER_ROLES', [])
