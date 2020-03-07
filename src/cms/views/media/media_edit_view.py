from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ...utils.media_utils import attach_file
from ...decorators import region_permission_required
from ...forms.media import DocumentForm
from ...models import Document, Region, Directory


@method_decorator(login_required, name="dispatch")
@method_decorator(region_permission_required, name="dispatch")
class MediaEditView(TemplateView):
    template_name = "media/media_form.html"
    base_context = {"current_menu_item": "media"}

    def get(self, request, *args, **kwargs):
        slug = kwargs.get("region_slug")
        directory_id = kwargs.get("directory_id")
        region = Region.objects.get(slug=slug)
        document_id = kwargs.get("document_id")
        form = DocumentForm()
        if document_id != "0":
            form = DocumentForm()

        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                "form": form,
                "region_slug": region.slug,
                "directory_id": directory_id,
                "document_id": document_id,
            },
        )

    # pylint: disable=unused-argument
    def post(self, request, *args, **kwargs):
        # current region
        region = Region.objects.get(slug=kwargs.get("region_slug"))

        directory_id = int(kwargs.get("directory_id"))
        document_id = kwargs.get("document_id")
        directory = None
        if directory_id != 0:
            directory = Directory.objects.get(id=directory_id)

        form = DocumentForm()

        if "upload" in request.FILES:
            document = Document()
            document.region = region
            document.path = directory
            attach_file(document, request.FILES["upload"])
            document.save()
            return redirect(
                "media", **{"region_slug": region.slug, "directory_id": directory_id}
            )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "region_slug": region.slug,
                "directory_id": directory_id,
                "document_id": document_id,
            },
        )
