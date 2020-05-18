from django.db import models
from django.utils.translation import ugettext_lazy as _

from contuga.models import TimestampModel
from parler.models import TranslatableModel, TranslatedFields

from . import constants

# TODO: Make sure there is only one home page


class Page(TimestampModel, TranslatableModel):
    type = models.CharField(
        _("Type"), max_length=254, choices=constants.PAGE_TYPE_CHOICES
    )

    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=254),
        slug=models.SlugField(_("Slug"), max_length=254, unique=True),
        description=models.CharField(_("Description"), max_length=1000, blank=True),
        background=models.FileField(verbose_name=_("Background image")),
    )

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    def __str__(self):
        return self.title

    @property
    def page_sections(self):
        return self.sections.all()


class PageSection(TranslatableModel):
    page = models.ForeignKey(Page, related_name="sections", on_delete=models.CASCADE)

    translations = TranslatedFields(
        #  Some of the images will be screenshots and it's better to use different for each language
        image=models.FileField(verbose_name=_("Image")),
        text=models.TextField(),
        #  Makes it easier to customize the sections
        image_position=models.CharField(
            _("Image position"),
            max_length=254,
            choices=constants.IMAGE_POSITION_CHOICES,
            default=constants.RIGHT,
        ),
    )

    class Meta:
        verbose_name = _("Page section")
        verbose_name_plural = _("Page sections")

    def __str__(self):
        return self.text

    @property
    def is_image_on_right(self):
        return self.image_position == constants.RIGHT
