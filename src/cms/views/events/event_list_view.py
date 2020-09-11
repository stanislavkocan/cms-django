from datetime import date, time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from ...constants import all_day
from ...decorators import region_permission_required
from ...models import Language, Region, Event
from ...forms.events import EventFilterForm


@method_decorator(login_required, name="dispatch")
@method_decorator(region_permission_required, name="dispatch")
# pylint: disable=too-many-ancestors
class EventListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "cms.view_events"
    raise_exception = True

    template = "events/event_list.html"
    template_archived = "events/event_list_archived.html"
    archived = False

    @property
    def template_name(self):
        return self.template_archived if self.archived else self.template

    def get(self, request, *args, **kwargs):
        # current region
        region_slug = kwargs.get("region_slug")
        region = Region.objects.get(slug=region_slug)

        # current language
        language_code = kwargs.get("language_code", None)
        if language_code is not None:
            language = Language.objects.get(code=language_code)
        elif region.default_language is not None:
            return redirect(
                "events",
                **{
                    "region_slug": region_slug,
                    "language_code": region.default_language.code,
                }
            )
        else:
            messages.error(
                request,
                _("Please create at least one language node before creating events."),
            )
            return redirect("language_tree", **{"region_slug": region_slug})

        if not request.user.has_perm("cms.edit_events"):
            messages.warning(
                request, _("You don't have the permission to edit or create events.")
            )

        # all events of the current region in the current language
        events = Event.get_list(region_slug, archived=self.archived)

        event_filter = kwargs.get("event_filter")
        if event_filter is not None:
            events = events.filter(
                start_date__gte=event_filter.get("after_date", date.min),
                start_time__gte=event_filter.get("after_time", time.min),
                end_date__lte=event_filter.get("before_date", date.max),
                end_time__lte=event_filter.get("before_time", time.max),
            )

            if event_filter.get("location") is not None:
                events = events.filter(location=event_filter.get("location"))

            if event_filter.get("all_day") == str(all_day.ALL_DAY):
                events = events.filter(
                    start_time=time.min,
                    end_time=time.max.replace(second=0, microsecond=0),
                )
            elif event_filter.get("all_day") == str(all_day.NOT_ALL_DAY):
                events = events.exclude(
                    start_time=time.min,
                    end_time=time.max.replace(second=0, microsecond=0),
                )

        # all other languages of current region
        languages = region.languages

        event_filter_form = EventFilterForm()

        return render(
            request,
            self.template_name,
            {
                "current_menu_item": "events",
                "events": events,
                "archived_count": Event.archived_count(region_slug),
                "language": language,
                "languages": languages,
                "filter_form": event_filter_form,
            },
        )

    def post(self, request, *args, **kwargs):
        print(request.POST)

        event_filter = {}

        if request.POST.get("after_date") != "":
            event_filter["after_date"] = date.fromisoformat(
                request.POST.get("after_date")
            )
            if request.POST.get("after_time") != "":
                event_filter["after_time"] = time.fromisoformat(
                    request.POST.get("after_time")
                )

        if request.POST.get("before_date") != "":
            event_filter["before_date"] = date.fromisoformat(
                request.POST.get("before_date")
            )
            if request.POST.get("after_time") != "":
                event_filter["before_time"] = time.fromisoformat(
                    request.POST.get("before_time")
                )

        if int(request.POST.get("poi_id", -1)) >= 0:
            event_filter["location"] = request.POST.get("poi_id")

        event_filter["all_day"] = request.POST.get("all_day")

        event_filter_form = EventFilterForm(data=request.POST)

        for field in event_filter_form:
            print((field.value(), field.value() is None))

        print(event_filter)

        return self.get(request, *args, **kwargs, event_filter=event_filter)
