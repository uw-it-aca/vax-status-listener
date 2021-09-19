# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models


class RecipientManager(models.Manager):
    def process_recipients(self):
        pass


class Recipient(models.Model):
    uwnetid = models.CharField(max_length=32)
    created_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True)
    processed_status_code = models.CharField(max_length=3, null=True)

    objects = RecipientManager()
