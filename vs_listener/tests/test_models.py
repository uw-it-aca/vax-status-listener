# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from vs_listener.models import User, Envelope
from uw_pws.util import fdao_pws_override


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
                         Envelope.STATUS_CODE_ALLOWED)

        env = Envelope(status='declined')
        self.assertEqual(env.exemption_status_code,
                         Envelope.STATUS_CODE_BLOCKED)

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
            'user: javerage@uw.edu, status: completed, form_name: unknown')
