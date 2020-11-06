"""
This is a collection of unit tests for the events, event_translation and reccurence_rule models
"""

from datetime import datetime, time
from django.test import TestCase
from cms.models import Event, EventTranslation, RecurrenceRule, Region, POI, Language
from dateutil.rrule import DAILY, MONTHLY
from cms.constants import weekdays


class EventTest(TestCase):
    """
    Unit test for the Event model
    """

    def setUp(self):
        """
        Setup run to create a Region, POI, ReccurenceRule and Event objects
        """
        self.region = Region.objects.create(
            aliases=[], push_notification_channels=[], slug="testregion"
        )
        self.location = POI.objects.create(
            region=self.region, city="testlocation", latitude=0, longitude=0
        )

        self.event = Event.objects.create(
            region=self.region,
            location=self.location,
            start_date=datetime(2020, 11, 1),
            end_date=datetime(2020, 11, 30),
            start_time=time(13, 20),
            end_time=time(14, 20),
        )

    def test_languages(self):
        """
        Checks if method returns correct QuerySet
        """
        self.assertEqual(len(self.event.languages), 0)

        language_czech = Language.objects.create(
            native_name="Cestina", english_name="Czech", code="cz-cz"
        )
        language_slovak = Language.objects.create(
            native_name="Slovencina", english_name="Slovak", code="sk-sk"
        )

        event_translation_czech = EventTranslation.objects.create(
            event=self.event, language=language_czech
        )
        event_translation_slovak = EventTranslation.objects.create(
            event=self.event, language=language_slovak
        )

        self.assertEqual(len(self.event.languages), 2)
        self.assertIn(language_czech, self.event.languages)
        self.assertIn(language_slovak, self.event.languages)

    def test_get_translation(self):
        """
        Checks if method filter works correcly
        """
        self.assertEqual(self.event.get_translation(None), None)
        self.assertEqual(self.event.get_translation("slovak"), None)

        language = Language.objects.create(
            native_name="English", english_name="English"
        )
        event_translation = EventTranslation.objects.create(
            event=self.event, language=language
        )

        self.assertEqual(self.event.get_translation(language.code), event_translation)

    def test_is_reccuring(self):
        """
        Checks if the event recurrence rule is set correctly
        """
        self.assertFalse(self.event.is_recurring)

        reccurence_rule = RecurrenceRule.objects.create(frequency=DAILY)
        self.event.recurrence_rule = reccurence_rule
        self.assertTrue(self.event.is_recurring)

    def test_get_occurrences(self):

        self.assertEqual(
            self.event.get_occurrences(datetime(2020, 10, 1), datetime(2020, 10, 30)),
            [],
        )

        self.assertEqual(
            len(
                self.event.get_occurrences(
                    datetime(2020, 11, 1), datetime(2020, 11, 30)
                )
            ),
            1,
        )
        self.assertListEqual(
            self.event.get_occurrences(datetime(2020, 11, 1), datetime(2020, 11, 30)),
            [datetime(2020, 11, 1, 13, 20)],
        )

        # Reccurence rule frequency test
        reccurence_rule = RecurrenceRule.objects.create(frequency=DAILY)
        self.event.recurrence_rule = reccurence_rule
        result_datetimes = [
            datetime(2020, 11, 1, 13, 20),
            datetime(2020, 11, 2, 13, 20),
            datetime(2020, 11, 3, 13, 20),
        ]
        self.assertEqual(
            len(
                self.event.get_occurrences(datetime(2020, 11, 1), datetime(2020, 11, 4))
            ),
            3,
        )
        self.assertListEqual(
            self.event.get_occurrences(datetime(2020, 11, 1), datetime(2020, 11, 4)),
            result_datetimes,
        )

        # Reccurence rule interval test
        reccurence_rule = RecurrenceRule.objects.create(frequency=DAILY, interval=2)
        self.event.recurrence_rule = reccurence_rule
        result_datetimes = [
            datetime(2020, 11, 1, 13, 20),
            datetime(2020, 11, 3, 13, 20),
        ]
        self.assertEqual(
            len(
                self.event.get_occurrences(datetime(2020, 11, 1), datetime(2020, 11, 5))
            ),
            2,
        )
        self.assertListEqual(
            self.event.get_occurrences(datetime(2020, 11, 1), datetime(2020, 11, 4)),
            result_datetimes,
        )

        # Reccurence rule weekday_for_monthly test
        reccurence_rule = RecurrenceRule.objects.create(
            frequency=MONTHLY, weekday_for_monthly=weekdays.MONDAY
        )
        self.event.recurrence_rule = reccurence_rule
        result_datetimes = [
            datetime(2020, 11, 2, 13, 20),
            datetime(2020, 11, 9, 13, 20),
            datetime(2020, 11, 16, 13, 20),
            datetime(2020, 11, 23, 13, 20),
        ]
        self.assertEqual(
            len(
                self.event.get_occurrences(
                    datetime(2020, 11, 1), datetime(2020, 11, 30)
                )
            ),
            4,
        )
        self.assertListEqual(
            self.event.get_occurrences(datetime(2020, 11, 1), datetime(2020, 11, 30)),
            result_datetimes,
        )

    def test_is_all_day(self):
        """
        Checks if the is_all_day method works correctly
        """

        self.assertFalse(self.event.is_all_day)

        self.event.start_time = time(0, 0, 0)
        self.event.end_time = time(23, 59, 0)
        self.assertTrue(self.event.is_all_day)

        self.event.start_time = time(0, 0, 0, 1)
        self.event.end_time = time(23, 59, 0)
        self.assertFalse(self.event.is_all_day)

        self.event.start_time = time(0, 0, 0)
        self.event.end_time = time(23, 59, 59)
        self.assertFalse(self.event.is_all_day)
