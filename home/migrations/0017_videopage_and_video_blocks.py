# Squashed from migrations 0017–0021.
# Net result: VideoPage model (final fields), PhotoPage.photo FK fix,
# and updated StreamFields (video_with_caption block). No CustomImage table.

import django.db.models.deletion
import home.models.common
import home.models.gallery
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_remove_photopage_show_in_sidebar_and_more'),
        ('wagtailcore', '0096_referenceindex_referenceindex_source_object_and_more'),
        ('wagtailimages', '0027_image_description'),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # VideoPage                                                           #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='VideoPage',
            fields=[
                ('page_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='wagtailcore.page',
                )),
                ('media_file', models.FileField(
                    blank=True,
                    help_text='Videodatei (MP4, WebM, Ogg) oder animiertes GIF',
                    null=True,
                    upload_to='videos/%Y/%m/',
                    validators=[home.models.gallery.validate_media_file],
                )),
                ('media_type', models.CharField(
                    choices=[('gif', 'Animiertes GIF'), ('video', 'Videodatei')],
                    default='video',
                    help_text='Typ des Mediums',
                    max_length=10,
                )),
                ('media_alt_text', models.CharField(
                    blank=True,
                    default='',
                    help_text='Beschreibung für Barrierefreiheit',
                    max_length=255,
                )),
                ('description', wagtail.fields.RichTextField(
                    blank=True,
                    default='',
                    max_length=800,
                )),
                ('author', models.CharField(blank=True, default='', max_length=120)),
                ('date', models.DateField()),
                ('time', models.TimeField(blank=True, null=True)),
                ('location', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(home.models.common.CommonContextMixin, 'wagtailcore.page', models.Model),
        ),

        # ------------------------------------------------------------------ #
        # PhotoPage.photo FK — point at the standard Wagtail image table     #
        # ------------------------------------------------------------------ #
        migrations.AlterField(
            model_name='photopage',
            name='photo',
            field=models.ForeignKey(
                blank=True,
                help_text='Wagtail-Bild',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='wagtailimages.image',
            ),
        ),

        # ------------------------------------------------------------------ #
        # EventPage.body — final StreamField with video_with_caption block   #
        # ------------------------------------------------------------------ #
        migrations.AlterField(
            model_name='eventpage',
            name='body',
            field=wagtail.fields.StreamField(
                [
                    ('h1', 0), ('h2', 1), ('h3', 2), ('paragraph', 3),
                    ('image', 4), ('image_with_caption', 12),
                    ('video_with_caption', 21),
                    ('event_list', 23), ('multi_column', 28),
                ],
                block_lookup={
                    0: ('home.models.common.HeadingBlock', (), {'form_classname': 'h1', 'label': 'Kopfzeile 1'}),
                    1: ('home.models.common.HeadingBlock', (), {'form_classname': 'h2', 'label': 'Kopfzeile 2'}),
                    2: ('home.models.common.HeadingBlock', (), {'form_classname': 'h3', 'label': 'Kopfzeile 3'}),
                    3: ('wagtail.blocks.RichTextBlock', (), {'features': ['anchor-identifier', 'h4', 'h5', 'bold', 'italic', 'link', 'ol', 'ul', 'document-link', 'image', 'embed']}),
                    4: ('wagtail.images.blocks.ImageChooserBlock', (), {}),
                    5: ('wagtail.images.blocks.ImageChooserBlock', (), {'label': 'Bild'}),
                    6: ('wagtail.blocks.RichTextBlock', (), {'help_text': 'Optional formatted text to display with the image', 'label': 'Bildunterschrift', 'required': False}),
                    7: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('top', 'Oben'), ('bottom', 'Unten'), ('left', 'Links'), ('right', 'Rechts')], 'label': 'Position der Bildunterschrift'}),
                    8: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('none', 'Kein Link'), ('internal', 'Interne Seite'), ('external', 'Externe URL')], 'label': 'Link-Typ'}),
                    9: ('wagtail.blocks.PageChooserBlock', (), {'help_text': 'Wählen Sie eine Seite aus dieser Website', 'label': 'Interne Seite', 'required': False}),
                    10: ('wagtail.blocks.URLBlock', (), {'help_text': 'Geben Sie eine vollständige URL ein (z.B. https://example.com)', 'label': 'Externe URL', 'required': False}),
                    11: ('wagtail.blocks.StructBlock', [[('link_type', 8), ('internal_page', 9), ('external_url', 10)]], {'help_text': 'Optionaler Link für das Bild (interne Seite oder externe URL)', 'label': 'Optional Link'}),
                    12: ('wagtail.blocks.StructBlock', [[('image', 5), ('caption', 6), ('caption_position', 7), ('link', 11)]], {}),
                    13: ('home.models.common.VideoDocumentChooserBlock', (), {'help_text': 'Video (MP4, WebM, Ogg) oder animiertes GIF', 'label': 'Datei'}),
                    14: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('gif', 'Animiertes GIF'), ('video', 'Videodatei')], 'label': 'Medientyp'}),
                    15: ('wagtail.blocks.CharBlock', (), {'help_text': 'Beschreibung für Barrierefreiheit (wird nicht angezeigt, aber von Screenreadern gelesen)', 'label': 'Alt-Text', 'max_length': 255, 'required': False}),
                    16: ('wagtail.blocks.RichTextBlock', (), {'label': 'Beschriftung', 'required': False}),
                    17: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('top', 'Oben'), ('bottom', 'Unten'), ('left', 'Links'), ('right', 'Rechts')], 'label': 'Position der Beschriftung'}),
                    18: ('wagtail.blocks.StructBlock', [[('link_type', 8), ('internal_page', 9), ('external_url', 10)]], {'help_text': 'Optionaler Link für das Medium (interne Seite oder externe URL)', 'label': 'Optionaler Link'}),
                    19: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('true', 'Ja'), ('false', 'Nein')], 'help_text': 'Nur für Videos und animierte GIFs', 'label': 'Autoplay'}),
                    20: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('true', 'Ja'), ('false', 'Nein')], 'help_text': 'Nur für Videos und animierte GIFs', 'label': 'Schleife'}),
                    21: ('wagtail.blocks.StructBlock', [[('media_file', 13), ('media_type', 14), ('media_alt_text', 15), ('caption', 16), ('caption_position', 17), ('link', 18), ('autoplay', 19), ('loop', 20)]], {}),
                    22: ('wagtail.blocks.MultipleChoiceBlock', [], {'choices': [('Vortrag', 'Vortrag'), ('Hybride Vortrag', 'Hybride Vortrag'), ('Online Vortrag', 'Online Vortrag'), ('Beobachtungsabend', 'Beobachtungsabend'), ('Ausflug', 'Ausflug')], 'help_text': 'Liste von Veranstaltungen', 'label': 'Art der Veranstaltung', 'required': False}),
                    23: ('wagtail.blocks.StructBlock', [[('event_type', 22)]], {}),
                    24: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('1', '1 Spalte'), ('2', '2 Spalten'), ('4', '4 Spalten')], 'help_text': 'Die Anzahl der Spalten für das Layout', 'label': 'Maximale Anzahl von Spalten'}),
                    25: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('1', '1 Spalte'), ('2', '2 Spalten'), ('4', '4 Spalten')], 'help_text': 'Die Mindestanzahl von Spalten auch auf mobilen Geräten', 'label': 'Minimale Anzahl von Spalten'}),
                    26: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('full', 'Volle Breite'), ('half', '1/2 Breite (auf Desktop)'), ('quarter', '1/4 Breite (auf Desktop)')], 'help_text': 'Auf mobilen Geräten wird immer die volle Breite verwendet', 'label': 'Breite des Blocks'}),
                    27: ('wagtail.blocks.StreamBlock', [[('h1', 0), ('h2', 1), ('h3', 2), ('paragraph', 3), ('image', 4), ('image_with_caption', 12), ('video_with_caption', 21), ('event_list', 23)]], {'label': 'Inhalt'}),
                    28: ('wagtail.blocks.StructBlock', [[('max_columns', 24), ('min_columns', 25), ('width', 26), ('content', 27)]], {}),
                },
                default=[],
            ),
        ),

        # ------------------------------------------------------------------ #
        # HomePage.body — final StreamField with video_with_caption block    #
        # ------------------------------------------------------------------ #
        migrations.AlterField(
            model_name='homepage',
            name='body',
            field=wagtail.fields.StreamField(
                [
                    ('h1', 0), ('h2', 1), ('h3', 2), ('paragraph', 3),
                    ('image', 4), ('image_with_caption', 12),
                    ('video_with_caption', 21),
                    ('multi_column', 26),
                ],
                block_lookup={
                    0: ('home.models.common.HeadingBlock', (), {'form_classname': 'h1', 'label': 'Kopfzeile 1'}),
                    1: ('home.models.common.HeadingBlock', (), {'form_classname': 'h2', 'label': 'Kopfzeile 2'}),
                    2: ('home.models.common.HeadingBlock', (), {'form_classname': 'h3', 'label': 'Kopfzeile 3'}),
                    3: ('wagtail.blocks.RichTextBlock', (), {'features': ['anchor-identifier', 'h4', 'h5', 'bold', 'italic', 'link', 'ol', 'ul', 'document-link', 'image', 'embed']}),
                    4: ('wagtail.images.blocks.ImageChooserBlock', (), {}),
                    5: ('wagtail.images.blocks.ImageChooserBlock', (), {'label': 'Bild'}),
                    6: ('wagtail.blocks.RichTextBlock', (), {'help_text': 'Optional formatted text to display with the image', 'label': 'Bildunterschrift', 'required': False}),
                    7: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('top', 'Oben'), ('bottom', 'Unten'), ('left', 'Links'), ('right', 'Rechts')], 'label': 'Position der Bildunterschrift'}),
                    8: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('none', 'Kein Link'), ('internal', 'Interne Seite'), ('external', 'Externe URL')], 'label': 'Link-Typ'}),
                    9: ('wagtail.blocks.PageChooserBlock', (), {'help_text': 'Wählen Sie eine Seite aus dieser Website', 'label': 'Interne Seite', 'required': False}),
                    10: ('wagtail.blocks.URLBlock', (), {'help_text': 'Geben Sie eine vollständige URL ein (z.B. https://example.com)', 'label': 'Externe URL', 'required': False}),
                    11: ('wagtail.blocks.StructBlock', [[('link_type', 8), ('internal_page', 9), ('external_url', 10)]], {'help_text': 'Optionaler Link für das Bild (interne Seite oder externe URL)', 'label': 'Optional Link'}),
                    12: ('wagtail.blocks.StructBlock', [[('image', 5), ('caption', 6), ('caption_position', 7), ('link', 11)]], {}),
                    13: ('home.models.common.VideoDocumentChooserBlock', (), {'help_text': 'Video (MP4, WebM, Ogg) oder animiertes GIF', 'label': 'Datei'}),
                    14: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('gif', 'Animiertes GIF'), ('video', 'Videodatei')], 'label': 'Medientyp'}),
                    15: ('wagtail.blocks.CharBlock', (), {'help_text': 'Beschreibung für Barrierefreiheit (wird nicht angezeigt, aber von Screenreadern gelesen)', 'label': 'Alt-Text', 'max_length': 255, 'required': False}),
                    16: ('wagtail.blocks.RichTextBlock', (), {'label': 'Beschriftung', 'required': False}),
                    17: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('top', 'Oben'), ('bottom', 'Unten'), ('left', 'Links'), ('right', 'Rechts')], 'label': 'Position der Beschriftung'}),
                    18: ('wagtail.blocks.StructBlock', [[('link_type', 8), ('internal_page', 9), ('external_url', 10)]], {'help_text': 'Optionaler Link für das Medium (interne Seite oder externe URL)', 'label': 'Optionaler Link'}),
                    19: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('true', 'Ja'), ('false', 'Nein')], 'help_text': 'Nur für Videos und animierte GIFs', 'label': 'Autoplay'}),
                    20: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('true', 'Ja'), ('false', 'Nein')], 'help_text': 'Nur für Videos und animierte GIFs', 'label': 'Schleife'}),
                    21: ('wagtail.blocks.StructBlock', [[('media_file', 13), ('media_type', 14), ('media_alt_text', 15), ('caption', 16), ('caption_position', 17), ('link', 18), ('autoplay', 19), ('loop', 20)]], {}),
                    22: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('1', '1 Spalte'), ('2', '2 Spalten'), ('4', '4 Spalten')], 'help_text': 'Die Anzahl der Spalten für das Layout', 'label': 'Maximale Anzahl von Spalten'}),
                    23: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('1', '1 Spalte'), ('2', '2 Spalten'), ('4', '4 Spalten')], 'help_text': 'Die Mindestanzahl von Spalten auch auf mobilen Geräten', 'label': 'Minimale Anzahl von Spalten'}),
                    24: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('full', 'Volle Breite'), ('half', '1/2 Breite (auf Desktop)'), ('quarter', '1/4 Breite (auf Desktop)')], 'help_text': 'Auf mobilen Geräten wird immer die volle Breite verwendet', 'label': 'Breite des Blocks'}),
                    25: ('wagtail.blocks.StreamBlock', [[('h1', 0), ('h2', 1), ('h3', 2), ('paragraph', 3), ('image', 4), ('image_with_caption', 12), ('video_with_caption', 21)]], {'label': 'Inhalt'}),
                    26: ('wagtail.blocks.StructBlock', [[('max_columns', 22), ('min_columns', 23), ('width', 24), ('content', 25)]], {}),
                },
                default=[],
            ),
        ),
    ]
