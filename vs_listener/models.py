# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.utils.timezone import utc
from dateutil.parser import parse
from restclients_core.exceptions import DataFailureException
from uw_sws.dao import SWS_TIMEZONE
from uw_sws.models import RegistrationBlock
from uw_sws.registration import update_registration_block
from uw_pws import PWS, InvalidNetID
from datetime import datetime
from logging import getLogger
import json
import pytz

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
            email = signer.get('email', '').lower()
            if (Envelope.valid_role(signer.get('roleName', '')) and
                    Envelope.valid_status(signer.get('status', '')) and
                    User.valid_email(email)):
                user, _ = User.objects.get_or_create(email=email)
                return user, signer.get('status').lower()
        return None, None

    def add_envelope(self, data):
        requestor, req_status = self._find_requestor(data)

        if requestor:
            guid = data.get('envelopeId')
            form_name = data.get('powerForm', {}).get('name')
            status = data.get('status').lower()
            changed = parse(data.get('statusChangedDateTime'))

            if not Envelope.valid_status(status):
                status = req_status

            logger.info(
                'Envelope received: user: {}, status: {}, guid: {}, '
                'form_name: {}'.format(requestor, status, guid, form_name))

            env, created = Envelope.objects.get_or_create(guid=guid, defaults={
                'user': requestor,
                'form_name': form_name,
                'status': status,
                'status_changed_date': changed,
            })

            if not created and env.status != status:
                env.status = status
                env.status_changed_date = changed
                env.processed_date = None
                env.processed_status_code = None
                env.save()

            return env

    def process_envelopes(self):
        envelopes = super(EnvelopeManager, self).get_queryset().filter(
            processed_date__isnull=True).order_by('status_changed_date')

        for envelope in envelopes:
            envelope.update_sws()


class Envelope(models.Model):
    STATUS_CHOICES = (
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

    @property
    def exemption_status_code(self):
        return settings.REG_STATUS_ALLOWED if (
            self.status == 'completed') else settings.REG_STATUS_BLOCKED

    @property
    def local_status_changed_date(self):
        return self.status_changed_date.replace(
            tzinfo=pytz.utc).astimezone(SWS_TIMEZONE)

    def __str__(self):
        return 'user: {}, status: {} ({}), form_name: {}'.format(
            self.user, self.status, self.exemption_status_code, self.form_name)

    def update_sws(self):
        try:
            block = RegistrationBlock(
                uwregid=self.user.uwregid,
                covid19_status_code=self.exemption_status_code,
                covid19_status_date=self.local_status_changed_date,
            )
            update_registration_block(block)
            self.processed_status_code = 200
            logger.info('Envelope processed: {}'.format(self))
        except DataFailureException as ex:
            self.processed_status_code = ex.status
            logger.info('Envelope processor error: {}, {}'.format(self, ex))

        if self.processed_status_code in settings.OK_PROCESSING_STATUS:
            self.processed_date = datetime.utcnow().replace(tzinfo=utc)
        self.save()

    @staticmethod
    def valid_status(status):
        return status.lower() in Envelope.VALID_STATUS

    @staticmethod
    def valid_role(role):
        return role.lower() in getattr(settings, 'REQUESTOR_ROLES', [])
