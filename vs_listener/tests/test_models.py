# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.test import TestCase, override_settings
from django.conf import settings
from vs_listener.models import User, Envelope
from uw_pws.util import fdao_pws_override
from dateutil.parser import parse


@fdao_pws_override
class UserModelTest(TestCase):
    def test_valid_email(self):
        self.assertTrue(User.valid_email('javerage@uw.edu'))
        self.assertFalse(User.valid_email('javerage@example.edu'))
        self.assertFalse(User.valid_email(''))
        self.assertFalse(User.valid_email(12))

    def test_uwnetid(self):
        user = User(email='javerage@uw.edu')
        self.assertEqual(user.uwnetid, 'javerage')

        user = User()
        self.assertEqual(user.uwnetid, '')

    def test_uwregid(self):
        user = User(email='javerage@uw.edu')
        self.assertEqual(user.uwregid, '9136CCB8F66711D5BE060004AC494FFE')

    def test_str(self):
        user = User(email='javerage@uw.edu')
        self.assertEqual(str(user), 'javerage@uw.edu')


class EnvelopeModelTest(TestCase):
    def test_valid_status(self):
        self.assertTrue(Envelope.valid_status('completed'))
        self.assertTrue(Envelope.valid_status('COMPLETED'))
        self.assertFalse(Envelope.valid_status(''))
        self.assertFalse(Envelope.valid_status('sent'))

    def test_exemption_status_code(self):
        env = Envelope(status='completed')
        self.assertEqual(env.exemption_status_code,
                         settings.REG_STATUS_ALLOWED)

        env = Envelope(status='declined')
        self.assertEqual(env.exemption_status_code,
                         settings.REG_STATUS_BLOCKED)

    def test_local_status_changed_date(self):
        dt = parse('2021-10-20 02:30:00.000+00')
        env = Envelope(status_changed_date=dt)
        self.assertEqual(str(env.local_status_changed_date),
                         '2021-10-19 19:30:00-07:00')

    def test_valid_role(self):
        self.assertTrue(Envelope.valid_role('STUDENT'))
        self.assertTrue(Envelope.valid_role('student'))
        self.assertFalse(Envelope.valid_role(''))
        self.assertFalse(Envelope.valid_role('admin'))

    def test_str(self):
        user = User(email='javerage@uw.edu')
        env = Envelope(user=user, status='completed', form_name='unknown')
        self.assertEqual(
            str(env),
            'user: javerage@uw.edu, status: completed (4), form_name: unknown')
