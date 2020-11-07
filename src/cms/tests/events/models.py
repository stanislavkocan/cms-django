"""
This is a collection of unit tests for the Event, EventTranslation and ReccurenceRule models
"""

from datetime import datetime, time
from django.test import TestCase
from dateutil.rrule import DAILY, MONTHLY
from cms.models import (
    Event,
    EventTranslation,
    RecurrenceRule,
    Region,
    POI,
    Language,
    LanguageTreeNode,
)
from cms.constants import weekdays, status


class EventTest(TestCase):
    """
    Unit tests for the Event model
    """

    def setUp(self):
        """
        Setup run to create a Region, POI (location) and Event objects
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
        Checks if methods filter works correcly
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
        Checks if the method returns correct occurrences of the event in the given timeframe
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
        Checks if the is_all_day method works correctly (whether an event takes place the whole day)
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


class EventTranslationTest(TestCase):
    """
    Unit tests for the EventTranslation model
    """

    def setUp(self):
        """
        Setup run to create a Region, Event, Language and LanguageTreeNode models
        """

        self.region = Region.objects.create(
            aliases=[], push_notification_channels=[], slug="testregion"
        )

        self.event = Event.objects.create(
            region=self.region,
            start_date=datetime(2020, 11, 1),
            end_date=datetime(2020, 11, 30),
            start_time=time(13, 20),
            end_time=time(14, 20),
        )

        self.language_slovak = Language.objects.create(
            native_name="Slovencina", english_name="Slovak", code="sk-sk"
        )
        self.language_czech = Language.objects.create(
            native_name="Cestina", english_name="Czech", code="cz-cz"
        )
        self.language_tree_node_slovak = LanguageTreeNode.objects.create(
            region=self.region, language=self.language_slovak
        )
        self.language_tree_node_czech = LanguageTreeNode.objects.create(
            region=self.region,
            language=self.language_czech,
            parent=self.language_tree_node_slovak,
        )

        self.event_translation_slovak = EventTranslation.objects.create(
            event=self.event, language=self.language_slovak, version=1
        )
        self.event_translation_czech = EventTranslation.objects.create(
            event=self.event,
            language=self.language_czech,
            version=1,
            status=status.PUBLIC,
        )

    def test_permalink_absolute_url(self):
        """
        Checks if dynamically calculated permalink and absolute_url are correct
        """

        result_permalink = "testregion/sk-sk/events/"
        result_url = "/testregion/sk-sk/events/"
        self.assertEqual(self.event_translation_slovak.permalink, result_permalink)
        self.assertEqual(self.event_translation_slovak.get_absolute_url(), result_url)

        result_permalink = "testregion/sk-sk/events/testslug"
        result_url = "/testregion/sk-sk/events/testslug"
        self.event_translation_slovak.slug = "testslug"
        self.assertEqual(self.event_translation_slovak.permalink, result_permalink)
        self.assertEqual(self.event_translation_slovak.get_absolute_url(), result_url)

    def test_source_translation(self):
        """
        Checks if correct source translation is returned which was used to create the translation
        """

        self.assertEqual(self.event_translation_slovak.source_translation, None)
        self.assertEqual(
            self.event_translation_czech.source_translation,
            self.event_translation_slovak,
        )

        event_translation_czech_2 = EventTranslation.objects.create(
            event=self.event, language=self.language_czech, version=2
        )
        self.assertEqual(
            event_translation_czech_2.source_translation, self.event_translation_slovak
        )

    def test_previous_revision(self):
        """
        Checks if correct EventTranslation object is returned which is previous version of newer one
        """

        self.assertEqual(self.event_translation_czech.previous_revision, None)
        self.assertEqual(self.event_translation_slovak.previous_revision, None)

        event_translation_czech_2 = EventTranslation.objects.create(
            event=self.event, language=self.language_czech, version=2
        )
        self.assertEqual(
            event_translation_czech_2.previous_revision, self.event_translation_czech
        )
        self.assertEqual(self.event_translation_slovak.previous_revision, None)

        event_translation_czech_3 = EventTranslation.objects.create(
            event=self.event, language=self.language_czech, version=3
        )
        self.assertEqual(
            event_translation_czech_2.previous_revision, self.event_translation_czech
        )
        self.assertEqual(
            event_translation_czech_3.previous_revision, event_translation_czech_2
        )

    def test_latest_public_revision(self):
        """
        Checks if correct EventTranslation object is returned which is the newest public version
        """

        self.assertEqual(
            self.event_translation_czech.latest_public_revision,
            self.event_translation_czech,
        )
        self.assertEqual(
            self.event_translation_slovak.latest_public_revision, None
        )  # status is not public

        event_translation_czech_2 = EventTranslation.objects.create(
            event=self.event,
            language=self.language_czech,
            version=2,
            status=status.DRAFT,
        )
        self.assertEqual(
            self.event_translation_czech.latest_public_revision,
            self.event_translation_czech,
        )

        event_translation_czech_2 = EventTranslation.objects.create(
            event=self.event,
            language=self.language_czech,
            version=2,
            status=status.PUBLIC,
        )
        self.assertEqual(
            self.event_translation_czech.latest_public_revision,
            event_translation_czech_2,
        )

    def test_is_outdated(self):
        """
        Checks if EventTranslation object is outdated.
        This happens, when the source translation is updated and the update is no `minor_edit`
        """

        self.assertFalse(self.event_translation_czech.is_outdated)
        self.assertFalse(self.event_translation_slovak.is_outdated)

        event_translation_slovak_2 = EventTranslation.objects.create(
            event=self.event,
            language=self.language_slovak,
            version=2,
            minor_edit=True,
            status=status.PUBLIC,
        )
        self.assertFalse(
            self.event_translation_czech.is_outdated
        )  # minor_edit is True (result is False)

        event_translation_slovak_2 = EventTranslation.objects.create(
            event=self.event, language=self.language_slovak, version=2, minor_edit=False
        )
        self.assertFalse(
            self.event_translation_czech.is_outdated
        )  # not public (result is False)

        event_translation_slovak_2 = EventTranslation.objects.create(
            event=self.event,
            language=self.language_slovak,
            version=2,
            minor_edit=False,
            status=status.PUBLIC,
        )
        self.assertTrue(
            self.event_translation_czech.is_outdated
        )  # public and minor_edit is False (results is True)
