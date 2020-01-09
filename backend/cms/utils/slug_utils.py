import logging

from django.utils.text import slugify


logger = logging.getLogger(__name__)


def generate_unique_slug(form_object, foreign_model=None):

    logger.info('generate_unique_slug()')
    if foreign_model:
        logger.info('foreign_model: "%s"', foreign_model)
        logger.info('region: "%s"', form_object.region)
        logger.info('language: "%s"', form_object.language)

    slug = form_object.cleaned_data['slug']

    # if slug is empty, generate from title/name
    if not slug:
        # determine fallback field of the model
        if foreign_model:
            fallback = 'title'
        else:
            fallback = 'name'
        # slugify to make sure slug doesn't contain special chars etc.
        slug = slugify(form_object.cleaned_data[fallback], allow_unicode=True)
        # If the title/name field didn't contain valid characters for a slug, we use a hardcoded fallback slug
        if not slug:
            slug = 'page'

    unique_slug = slug
    i = 1
    pre_filtered_objects = form_object.Meta.model.objects

    # if the foreign model is a content type (e.g. page, event or poi), make sure slug is unique per region and language
    if foreign_model:
        pre_filtered_objects = pre_filtered_objects.filter(**{
            foreign_model + '__region': form_object.region,
            'language': form_object.language
        })

    # generate new slug while it is not unique
    while True:
        # get other objects with same slug
        other_objects = pre_filtered_objects.filter(slug=unique_slug)
        if form_object.instance.id:
            if foreign_model:
                # other objects which are just other versions of this object are allowed to have the same slug
                other_objects = other_objects.exclude(**{
                    foreign_model: form_object.instance.foreign_object,
                    'language': form_object.language
                })
            else:
                # the current object is also allowed to have the same slug
                other_objects = other_objects.exclude(id=form_object.instance.id)
        if not other_objects.exists():
            break
        i += 1
        unique_slug = '{}-{}'.format(slug, i)

    logger.info('unique slug: %s', unique_slug)
    return unique_slug