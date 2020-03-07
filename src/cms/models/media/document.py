import os

from django.db import models

from ..regions.region import Region
from .directory import Directory
from .file import File


class Document(models.Model):
    """
    The Document model is used to store basic information about files which are uploaded to the CMS. This is only a
    virtual document and does not necessarily exist on the actual file system. Each document is tied to a region via its
    directory.

    :param id: The database id of the document
    :param uploaded_at: The date and time when the document was uploaded

    Relationship fields:

    :param file: The file object of this document (related name: ``documents``)
    :param path: The directory containing this document (related name: ``documents``)
    :param region: The region to which this document belongs (related name: ``documents``)

    Reverse relationships:

    :param meta_data: The meta properties of this document
    """

    file = models.ForeignKey(
        File, related_name="documents", on_delete=models.CASCADE, null=True
    )
    path = models.ForeignKey(
        Directory, related_name="documents", on_delete=models.PROTECT, null=True
    )
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        This overwrites the default Python __str__ method which would return <Document object at 0xDEADBEEF>
        :return: The string representation (in this case the virtual filepath) of the document
        :rtype: str
        """
        return os.path.basename(self.file.path)

    class Meta:
        """
        This class contains additional meta configuration of the model class, see the
        `official Django docs <https://docs.djangoproject.com/en/2.2/ref/models/options/>`_ for more information.
        :param default_permissions: The default permissions for this model
        :type default_permissions: tuple
        """

        default_permissions = ()
        permissions = (
            ("manage_documents", "Can manage documents"),
            ("can_delete_documents", "Can delete documents"),
        )
