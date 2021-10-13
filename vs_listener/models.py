# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.functional import cached_property
from django.utils.timezone import utc
from dateutil.parser import parse
from restclients_core.exceptions import DataFailureException
from uw_sws.models import RegistrationBlock
from uw_sws.registration import update_registration_block
from uw_pws import PWS, InvalidNetID
from datetime import datetime
from logging import getLogger

logger = getLogger(__name__)


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
    def _find_requestor(self, data):
        for signer in data.get('recipients', {}).get('signers', []):
            if (Envelope.valid_role(signer.get('roleName', '')) and
                    User.valid_email(signer.get('email', ''))):
                user, _ = User.objects.get_or_create(signer.get('email'))
                return user

    def add_envelope(self, data):
        if not Envelope.valid_status(data.get('status')):
            return

        requestor = self._find_requestor(data)

        if requestor:
            guid = data.get('envelopeId')
            envelope, _ = Envelope.objects.get_or_create(guid=guid, defaults={
                'user': requestor,
                'status': data.get('status').lower(),
                'form_name': data.get('powerForm', {}).get('name'),
                'status_changed_date': parse(
                    data.get('statusChangedDateTime')),
            })
            return envelope

    def process_envelopes(self):
        envelopes = super(EnvelopeManager, self).get_queryset().filter(
            Q(processed_date__isnull=True) | ~Q(processed_status_code=200)
        ).order_by('created_date')

        for envelope in envelopes:
            envelope.update_sws()


class Envelope(models.Model):
    STATUS_CHOICES = (
       ('completed', 'completed'),
       ('declined', 'declined'),
       ('voided', 'voided')
    )
    STATUS_CODE_ALLOWED = 1
    STATUS_CODE_BLOCKED = 4
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

    @property
    def exemption_status_code(self):
        return self.STATUS_CODE_ALLOWED if (
            self.status == 'completed') else self.STATUS_CODE_BLOCKED

    def __str__(self):
        return 'user: {}, status: {}, form_name: {}'.format(
            self.user, self.status, self.form_name)

    def update_sws(self):
        try:
            block = RegistrationBlock(
                uwregid=user.uwregid,
                covid19_status_code=self.exemption_status_code,
                covid19_status_date=self.status_changed_date,
            )
            update_registration_block(block)
            self.processed_status_code = 200
            logger.info('Envelope processed: {}'.format(self))
        except DataFailureException as ex:
            self.processed_status_code = ex.status
            logger.info('Envelope processor error: {}, {}'.format(self, ex))

        self.processed_date = datetime.utcnow().replace(tzinfo=utc)
        self.save()

    @staticmethod
    def valid_status(status):
        return status.lower() in Envelope.VALID_STATUS

    @staticmethod
    def valid_role(role):
        return role.lower() in getattr(settings, 'REQUESTOR_ROLES', [])
