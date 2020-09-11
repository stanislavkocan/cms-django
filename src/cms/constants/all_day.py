"""
This module contains all string representations of all day filter options, used by :class:`~cms.forms.events.event_filter_form.EventFilterForm` and
:class:`~cms.views.events.event_list_view.EventListView`:

* ``ALL_DAY``: Only events which are all day long

* ``NOT_ALL_DAY``: Exclude events which are all day long

* ``BOTH``: All events
"""
from django.utils.translation import ugettext_lazy as _

ALL_DAY = 1
NOT_ALL_DAY = 2
BOTH = 3

CHOICES = (
    (BOTH, _("All events")),
    (ALL_DAY, _("Only all day events")),
    (NOT_ALL_DAY, _("Only part day events")),
)
