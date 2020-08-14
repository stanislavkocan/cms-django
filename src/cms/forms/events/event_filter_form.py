"""
Form for submitting filter requests
"""
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from ...constants import status as status_constants

logger = logging.getLogger(__name__)

RECURRING = "r"
NOT_RECURRING = "nr"
ALL_DAY = "ad"
NOT_ALL_DAY = "nad"
BOTH = "b"

ALL_DAY_CHOICES = (
    (BOTH, _("All events")),
    (ALL_DAY, _("Only all day events")),
    (NOT_ALL_DAY, _("Only part day events")),
)

RECURRENCE_CHOICES = (
    (RECURRING, _("Events and related recurrences")),
    (NOT_RECURRING, _("Only base events without recurrences")),
)


class EventFilterForm(forms.Form):
    all_day = forms.ChoiceField(
        widget=forms.RadioSelect, choices=ALL_DAY_CHOICES, required=False
    )

    recurring = forms.ChoiceField(
        widget=forms.RadioSelect, choices=RECURRENCE_CHOICES, required=False
    )

    after_date = forms.DateField(
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        required=False,
    )
    before_date = forms.DateField(
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        required=False,
    )

    after_time = forms.TimeField(
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}), required=False
    )
    before_time = forms.TimeField(
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}), required=False
    )

    status = forms.ChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=status_constants.CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["all_day"] = BOTH
        self.initial["recurring"] = RECURRING
