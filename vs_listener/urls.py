# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.urls import re_path
from vs_listener.views import ListenerView

urlpatterns = [
    re_path(r'^listener$', ListenerView.as_view()),
]
