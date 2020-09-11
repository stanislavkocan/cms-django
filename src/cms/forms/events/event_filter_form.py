"""
Form for submitting filter requests
"""
import logging

from django import forms

from ...constants import status as status_constants, all_day, recurrence

logger = logging.getLogger(__name__)


class EventFilterForm(forms.Form):
    all_day = forms.ChoiceField(
        widget=forms.RadioSelect, choices=all_day.CHOICES, required=False
    )

    recurring = forms.ChoiceField(
        widget=forms.RadioSelect, choices=recurrence.CHOICES, required=False
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
        self.initial["all_day"] = all_day.BOTH
        self.initial["recurring"] = recurrence.RECURRING
