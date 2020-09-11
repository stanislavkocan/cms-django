"""
This module contains all string representations of recurrence filter options, used by :class:`~cms.forms.events.event_filter_form.EventFilterForm` and
:class:`~cms.views.events.event_list_view.EventListView`:

* ``Recurring``: Events and their recurrences

* ``NOT_RECURRING``: Only meta events without their recurrences (if existing)
"""
from django.utils.translation import ugettext_lazy as _

RECURRING = 1
NOT_RECURRING = 2

CHOICES = (
    (RECURRING, _("Events and related recurrences")),
    (NOT_RECURRING, _("Only base events without recurrences")),
)
