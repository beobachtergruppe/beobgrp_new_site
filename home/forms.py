from django import forms
from wagtail.images.forms import BaseImageForm


class NoGifImageForm(BaseImageForm):
    """
    Wagtail image upload form that rejects GIF files.
    GIF animations belong in VideoPage (via the video block), not the static image library.
    """

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file and hasattr(file, "name") and file.name.lower().endswith(".gif"):
            raise forms.ValidationError(
                "GIF-Dateien sind in der Bildbibliothek nicht erlaubt. "
                "Für animierte GIFs verwenden Sie bitte den Video-Block."
            )
        return file
