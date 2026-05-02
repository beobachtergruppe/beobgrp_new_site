# Media Enhancement Guide - Supporting GIFs and Videos

## Overview

This enhancement adds comprehensive support for animated GIFs and video files across your Wagtail Django site, in addition to static images. The implementation is designed to be backward compatible with existing content while providing new flexible media handling.

## What's New

### 1. **New Media Models** (`home/models/media.py`)

#### `MediaMixin` - Abstract Base Class
A reusable mixin for models that need flexible media handling:

```python
class PhotoPage(MediaMixin, CommonContextMixin, Page):
    # Now has image, video, media_type, and media_alt_text fields
```

**Available Fields:**
- `image` (ImageField): Stores images and animated GIFs
- `video` (FileField): Stores video files (MP4, WebM, Ogg)
- `media_type` (CharField): Indicates file type ('image', 'gif', 'video')
- `media_alt_text` (CharField): Accessibility text for screen readers

**Helper Methods:**
- `.get_media_file()`: Returns the appropriate file based on media_type
- `.get_media_url()`: Returns the URL of the current media
- `.is_gif()`: Check if media is an animated GIF
- `.is_video()`: Check if media is a video
- `.is_static_image()`: Check if media is a static image

### 2. **Enhanced Gallery Models**

#### PhotoPage Updates
- Now inherits from `MediaMixin` for flexible media support
- Maintains backward compatibility with old `photo` field (ForeignKey to wagtailimages.Image)
- New fields for direct image/video uploads: `image`, `video`, `media_type`, `media_alt_text`
- Admin panels updated to show both old and new fields

**Usage:**
```python
# In Django views or templates
photo = PhotoPage.objects.first()

if photo.is_video():
    video_url = photo.get_media_url()
elif photo.is_gif():
    gif_url = photo.get_media_url()
else:
    img = photo.image  # Static image
```

#### GalleryPage Updates
- New fields for cover media: `cover_image_file`, `cover_video`, `cover_media_type`
- Maintains old `cover_image` field for backward compatibility
- Helper method `.get_cover_media_url()` and `.get_cover_media_type()`

### 3. **New Content Blocks**

#### `MediaWithCaptionBlock`
A new streamfield block in `home/models/common.py` that supports:

**Block Features:**
- Media type selector: Image, GIF, or Video
- Image/GIF field using ImageChooserBlock
- Video field using DocumentChooserBlock
- Caption with position options (top, bottom, left, right)
- Optional link (internal page or external URL)
- Autoplay toggle (for videos and GIFs)
- Loop toggle (for videos and GIFs)
- Alt text for accessibility

**Available in:**
- Body content of most page types (added to `gen_body_content`)
- Can be nested in multi-column layouts
- Works alongside existing ImageWithCaptionBlock

### 4. **Updated Templates**

#### photo_page.html
Enhanced to detect and render appropriate media type:
```html
{% if page.is_video %}
    <video controls{% if page.autoplay %}autoplay{% endif %} {% if page.loop %}loop{% endif %}>
{% elif page.is_gif %}
    <img src="{{ page.get_media_url }}" alt="..." />
{% elif page.image %}
    {% image page.image original %}
{% elif page.photo %}
    {% image page.photo original %}
```

#### media_with_caption.html
New template for rendering media blocks with captions:
- Supports all caption positions
- Handles optional links
- Includes media_renderer.html for flexible media handling

#### media_renderer.html
Reusable template for rendering media based on type:
- Video rendering with controls
- GIF rendering as image
- Static image rendering with Wagtail image tag
- Graceful error messages for missing media

### 5. **Backward Compatibility**

All changes maintain full backward compatibility:
- Old `photo` field on PhotoPage still works
- Old `cover_image` field on GalleryPage still works
- Existing ImageWithCaptionBlock unchanged
- Existing photo_page.html template updated to check both old and new fields

## Migration Steps

### 1. **Create and Apply Migrations**
```bash
python manage.py makemigrations home
python manage.py migrate home
```

### 2. **Update Existing Content (Optional)**
If you want to migrate old content to use new media fields:

```python
# In Django shell
from home.models import PhotoPage

# Convert Wagtail Image ForeignKey to new image field
for photo_page in PhotoPage.objects.filter(photo__isnull=False):
    # The old photo field will still work
    # You can manually update if you want to use new fields
    pass
```

### 3. **Create CSS for New Media Classes** (Optional)
Add styles for the new media classes in your CSS:

```css
.media-container {
    max-width: 100%;
    overflow: auto;
}

.media-video {
    max-width: 100%;
    height: auto;
}

.media-gif {
    max-width: 100%;
    height: auto;
}

.media-image {
    max-width: 100%;
    height: auto;
}

.media-wrapper {
    display: flex;
    justify-content: center;
}

.media-caption {
    padding: 1rem;
}

.caption-top {
    order: -1;
}

.caption-bottom {
    order: 1;
}

.caption-left {
    order: -1;
}

.caption-right {
    order: 1;
}
```

## Usage Examples

### In Templates

#### Using MediaWithCaptionBlock:
When editors add a "Medien mit Bildunterschrift" block to page content, they can:
1. Select media type (Image, GIF, or Video)
2. Upload/choose file from Wagtail library
3. Add optional caption and configure position
4. Enable autoplay/loop for videos and GIFs
5. Add optional link to media

#### Checking Media Type in Templates:
```html
{% if page.is_video %}
    <!-- Render video player -->
{% elif page.is_gif %}
    <!-- Render GIF -->
{% else %}
    <!-- Render static image -->
{% endif %}
```

### In Views/Code

```python
from home.models import PhotoPage

photo = PhotoPage.objects.first()

# Check media type
if photo.is_video():
    print(f"Video URL: {photo.get_media_url()}")
elif photo.is_gif():
    print(f"Animated GIF: {photo.get_media_url()}")
else:
    print(f"Static image: {photo.get_media_url()}")

# Access raw fields
if photo.video:
    video_file = photo.video
if photo.image:
    image_file = photo.image
```

## File Storage

Media files are organized by type:
```
media/
├── images/YYYY/MM/           # Static images and GIFs
├── videos/YYYY/MM/           # Video files
├── gallery_covers/YYYY/MM/   # Gallery cover images
└── gallery_cover_videos/YYYY/MM/ # Gallery cover videos
```

## Supported File Formats

### Images
- **Static:** JPEG, PNG, WebP
- **Animated:** GIF (set media_type to 'gif')

### Videos
- MP4 (H.264)
- WebM (VP9)
- Ogg (Theora)

## Video Encoding Recommendations

For best compatibility and performance:

### MP4 (Primary Format)
```bash
ffmpeg -i input.mov -c:v libx264 -preset slow -crf 22 -c:a aac -b:a 128k output.mp4
```

### WebM (Alternative Format)
```bash
ffmpeg -i input.mov -c:v libvpx-vp9 -b:v 1000k -c:a libopus -b:a 128k output.webm
```

## Admin Interface

The enhanced admin panels show:

**PhotoPage:**
- Old field: "Foto (Alt)" - Wagtail Image ForeignKey
- New fields: "Bild oder animiertes GIF", "Videodatei", "Medientyp"
- "Alt-Text für Barrierefreiheit"

**GalleryPage:**
- Old field: "Titelbild (Alt)"
- New fields: "Titelmedium (Bild/GIF)", "Titel-Video", "Typ des Titelmediuns"

## Performance Considerations

### Image Optimization
- Use Wagtail's image library where possible (handles resizing/optimization)
- For GIFs, consider file size - optimize with tools like ImageOptim
- Use next-gen formats (WebP) when browser support is adequate

### Video Optimization
- Provide multiple formats for broad compatibility (MP4 + WebM)
- Use appropriate bitrate based on content (1000-5000 kbps typical)
- Consider using CDN for video delivery
- Implement lazy loading for videos below the fold

### Lazy Loading (Future Enhancement)
Consider adding lazy loading for videos:
```html
<video loading="lazy" ...>
```

## Troubleshooting

### Videos Not Playing
1. Check file format and codec compatibility
2. Ensure MIME types are configured correctly
3. Verify file permissions (readable by web server)
4. Test in different browsers

### GIFs Not Animating
1. Verify media_type is set to 'gif'
2. Check file is actual animated GIF (use `file` command)
3. Browser cache - hard refresh

### Media Not Displaying
1. Check media_type selection
2. Verify file is uploaded and URL is correct
3. Check template for errors (`{% image_url %}` vs manual URL)
4. Review Django media settings in settings.py

## Future Enhancements

1. **Lazy Loading:** Add native lazy loading for images and videos
2. **Thumbnails:** Auto-generate thumbnails for video/GIF previews
3. **Transcoding:** Auto-transcode uploads to multiple formats
4. **Streaming:** HLS/DASH support for large videos
5. **Analytics:** Track video/GIF views and engagement
6. **Responsive Video:** Picture element for responsive media

## Testing

Run tests to verify functionality:
```bash
python manage.py test home
```

### Sample Test Cases
```python
def test_photo_page_is_video(self):
    photo = PhotoPage(media_type='video')
    self.assertTrue(photo.is_video())

def test_photo_page_is_gif(self):
    photo = PhotoPage(media_type='gif')
    self.assertTrue(photo.is_gif())

def test_media_url_returns_correct_file(self):
    photo = PhotoPage(media_type='image', image=test_image)
    self.assertEqual(photo.get_media_url(), photo.image.url)
```

## Questions & Support

For issues or questions about the media enhancements:
1. Check the troubleshooting section above
2. Review Django and Wagtail documentation
3. Check server logs for detailed error messages
