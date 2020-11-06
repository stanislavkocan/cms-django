"""
This is a collection of unit tests for the offer and offer template model.
"""

from django.test import TestCase
from cms.models import Offer, OfferTemplate, Region
from cms.constants import postal_code


class OfferTest(TestCase):
    """
    Unit test for the Offer model
    """

    def setUp(self):
        """
        Setup run to create a region and offer objects.
        """
        self.region = Region.objects.create(
            aliases=[], push_notification_channels=[], slug="testregion"
        )

        self.offer1_template = OfferTemplate.objects.create()
        self.offer1 = Offer.objects.create(
            region=self.region, template=self.offer1_template
        )

    def test_offer_slug(self):
        """
        Checks if slug of offer is inherited from its template correctly.
        """
        self.assertEqual(self.offer1.slug, self.offer1_template.slug)

    def test_offer_name(self):
        """
        Checks if name of offer is inherited from its template correctly.
        """
        self.assertTrue(self.offer1.name == "")

        self.offer1_template.name = "test_name"
        self.assertEqual(self.offer1.name, self.offer1_template.name)

    def test_offer_thumbnail(self):
        """
        Checks if thumbnail of offer is inherited from its template correctly.
        """
        self.assertTrue(self.offer1.thumbnail == "")

        self.offer1_template.thumbnail = "test_thumbnail"
        self.assertEqual(self.offer1.thumbnail, self.offer1_template.thumbnail)

    def test_offer_url(self):
        """
        Checks if Url of offer is inherited from its template correctly.
        """
        self.assertEqual(self.offer1.url, self.offer1_template.url)

        self.offer1_template.use_postal_code = postal_code.POST
        self.assertEqual(self.offer1.url, self.offer1_template.url)

        self.offer1_template.use_postal_code = postal_code.GET
        self.assertEqual(
            self.offer1.url, self.offer1_template.url + self.region.postal_code
        )

    def test_post_data(self):
        """
        Checks if Post data of offer is inherited from its template correctly.
        """
        self.offer1_template.use_postal_code = None
        self.assertEqual(self.offer1.post_data, self.offer1_template.post_data)

        self.offer1_template.use_postal_code = postal_code.GET
        self.assertEqual(self.offer1.post_data, self.offer1_template.post_data)

        self.offer1_template.use_postal_code = postal_code.POST
        self.assertEqual(self.offer1.post_data["search-plz"], self.region.postal_code)
