# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from prometheus_client import Counter

vax_listener_notification_count = Counter(
    'notification_count',
    'Vax Listener notification received count')

vax_listener_invalid_notification_count = Counter(
    'invalid_notification_count',
    'Vax Listener invalid notification received count')

vax_listener_ignored_notification_count = Counter(
    'ignored_notification_count',
    'Vax Listener invalid notification received count',
    ['status'])

vax_listener_status_notification_count = Counter(
    'status_notification_count',
    'Vax Listener status notification received count',
    ['status'])


def notification_counter():
    vax_listener_notification_count.inc()


def notification_invalid_counter():
    vax_listener_invalid_notification_count.inc()


def notification_status_ignored_counter(status):
    vax_listener_ignored_notification_count.labels(status).inc()


def notification_status_counter(status):
    vax_listener_status_notification_count.labels(status).inc()
