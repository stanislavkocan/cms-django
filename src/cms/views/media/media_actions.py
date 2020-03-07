from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect

from ...decorators import region_permission_required
from ...models import Document, Region, Directory
from ...utils.media_utils import attach_file, delete_document


@login_required
@region_permission_required
def delete_file(request, document_id, region_slug):
    region = Region.objects.get(slug=region_slug)

    if request.method == "POST":
        document = Document.objects.get(pk=document_id)
        delete_document(document)

    directory_id = 0
    try:
        directory_id = document.directory.id
    except Directory.DoesNotExist:
        pass

    return redirect(
        "media", **{"region_slug": region.slug, "directory_id": directory_id}
    )


@login_required
@region_permission_required
def upload_file(request, region_slug, directory_id):
    region = Region.objects.get(slug=region_slug)

    if int(directory_id) != 0:
        directory = Directory.objects.get(id=directory_id)

    if "upload" in request.FILES:
        document = Document()
        document.region = region
        document.path = directory
        attach_file(document, request.FILES["upload"])
        document.save()
        return JsonResponse({})

    return JsonResponse({"success": False, "error": "No file was uploaded"})
