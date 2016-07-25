from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from wagtail.wagtailcore.models import Page


class HomePage(Page):
    description = models.TextField(max_length=400, default='')
    sponsor_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='This image will be displayed in all sponsor display locations accross the website'
    )

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
        ImageChooserPanel('sponsor_image'),
    ]
