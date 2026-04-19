from django.core.exceptions import ValidationError
from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class CustomImage(AbstractImage):
    """
    Custom Wagtail image model that rejects GIF uploads.
    GIF animations belong in VideoPage, not the image library.
    """

    admin_form_fields = Image.admin_form_fields

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        if self.file and self.file.name.lower().endswith(".gif"):
            raise ValidationError(
                {
                    "file": (
                        "GIF-Dateien sind in der Bildbibliothek nicht erlaubt. "
                        "Bitte laden Sie animierte GIFs als Videodatei über eine VideoPage hoch."
                    )
                }
            )

    class Meta:
        verbose_name = "Bild"
        verbose_name_plural = "Bilder"


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
