# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand, CommandError
from vs_listener.models import Recipient


class Command(BaseCommand):
    help = "Process recipient notifications"

    def handle(self, *args, **options):
        Recipient.objects.process()
