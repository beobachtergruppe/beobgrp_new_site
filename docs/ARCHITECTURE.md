# Media Enhancement Architecture

## Data Model Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     MediaMixin (Abstract)                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Fields:                                                 │ │
│  │ • image (ImageField)                                    │ │
│  │ • video (FileField)                                     │ │
│  │ • media_type (CharField: image/gif/video)              │ │
│  │ • media_alt_text (CharField)                           │ │
│  │                                                         │ │
│  │ Methods:                                                │ │
│  │ • get_media_file()                                      │ │
│  │ • get_media_url()                                       │ │
│  │ • is_gif()                                              │ │
│  │ • is_video()                                            │ │
│  │ • is_static_image()                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         △                                        △
         │                                        │
         │ inherits                               │ inherits
         │                                        │
    ┌────┴──────────────┐                  ┌─────┴──────────────┐
    │                   │                  │                    │
┌──────────────┐  ┌──────────────┐   ┌───────────────┐  ┌──────────────┐
│  PhotoPage   │  │ [Other Pages]│   │ GalleryPage   │  │ [Future Uses]│
│              │  │              │   │               │  │              │
│ + photo (FK) │  │              │   │ + cover_image │  │              │
│ + date       │  │              │   │   (ImageField)│  │              │
│ + author     │  │              │   │ + cover_video │  │              │
│ + location   │  │              │   │ + cover_media │  │              │
│              │  │              │   │   _type       │  │              │
└──────────────┘  └──────────────┘   └───────────────┘  └──────────────┘
```

## Content Block Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              StreamField Content Blocks                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────┐  ┌─────────────────────────────┐   │
│  │ ImageChooserBlock  │  │  ImageWithCaptionBlock      │   │
│  │ [Static]           │  │  [Static Image Only]        │   │
│  │                    │  │  + caption                  │   │
│  │ Just image         │  │  + caption_position         │   │
│  │                    │  │  + link                     │   │
│  └────────────────────┘  └─────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  MediaWithCaptionBlock (NEW)                        │   │
│  │  [Images, GIFs, Videos]                             │   │
│  │                                                      │   │
│  │  + media_type (image/gif/video) selector           │   │
│  │  + image (ImageChooserBlock)                        │   │
│  │  + video (DocumentChooserBlock)                     │   │
│  │  + media_alt_text                                  │   │
│  │  + caption                                          │   │
│  │  + caption_position (top/bottom/left/right)        │   │
│  │  + link (internal/external)                        │   │
│  │  + autoplay (for video/GIF)                        │   │
│  │  + loop (for video/GIF)                            │   │
│  │                                                      │   │
│  │  → media_with_caption.html template                │   │
│  │     ├─ Supports all caption positions              │   │
│  │     ├─ Includes media_renderer.html                │   │
│  │     └─ Handles optional links                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Template Rendering Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Browser Request for Page with MediaWithCaptionBlock         │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌────────────────────────────────────┐
        │  media_with_caption.html template  │
        │                                    │
        │  • Wraps media in container        │
        │  • Handles caption position        │
        │  • Manages optional link wrapper   │
        └────────────────────────────────────┘
                          │
                          ▼
        ┌────────────────────────────────────┐
        │  media_renderer.html (included)    │
        │  Checks media_type value:          │
        │                                    │
        │  ┌────────────────────────────┐   │
        │  │ IF media_type == 'video'   │   │
        │  │  → <video> element         │   │
        │  └────────────────────────────┘   │
        │                                    │
        │  ┌────────────────────────────┐   │
        │  │ IF media_type == 'gif'     │   │
        │  │  → <img> element (file)    │   │
        │  └────────────────────────────┘   │
        │                                    │
        │  ┌────────────────────────────┐   │
        │  │ ELSE (default: 'image')    │   │
        │  │  → {% image %} tag         │   │
        │  │    (Wagtail optimized)     │   │
        │  └────────────────────────────┘   │
        └────────────────────────────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │  Rendered HTML to Browser    │
           │                              │
           │  • For images: Optimized via │
           │    Wagtail image tag         │
           │  • For GIFs: Direct img tag  │
           │  • For videos: HTML5 video   │
           │    element with fallbacks    │
           └──────────────────────────────┘
```

## PhotoPage Media Resolution

```
PhotoPage Instance
    │
    ├─ Check media_type field
    │
    ├─→ media_type = 'video'
    │   └─→ Use: page.video (FileField)
    │       └─→ Render: <video> tag
    │
    ├─→ media_type = 'gif'
    │   └─→ Use: page.image (ImageField)
    │       └─→ Render: <img> tag
    │
    ├─→ media_type = 'image' (default)
    │   └─→ Use: page.image (ImageField)
    │       └─→ Render: {% image %} tag (Wagtail)
    │
    └─→ Fallback (no new media_type set)
        └─→ Use: page.photo (ForeignKey to wagtailimages.Image)
            └─→ Render: {% image %} tag (Wagtail)
```

## File Storage Organization

```
media/
│
├── images/
│   └── YYYY/MM/
│       ├── static_image.jpg          (Static images)
│       └── animated_image.gif        (Animated GIFs)
│
├── videos/
│   └── YYYY/MM/
│       ├── video.mp4
│       ├── video.webm
│       └── video.ogg
│
├── gallery_covers/
│   └── YYYY/MM/
│       └── cover_image.jpg
│
└── gallery_cover_videos/
    └── YYYY/MM/
        └── cover_video.mp4
```

## Admin Interface Flow

```
┌────────────────────────────────────────────────┐
│  Add/Edit PhotoPage in Admin                   │
├────────────────────────────────────────────────┤
│                                                │
│  [Legacy Fields]                               │
│  • Foto (Alt)  ─→ Old Wagtail Image FK        │
│    (for backward compatibility)                │
│                                                │
│  ──────────────────────────────────────────    │
│                                                │
│  [New Media Fields]                            │
│                                                │
│  • Medientyp     ─→ Select: image/gif/video   │
│                                                │
│  • Bild oder GIF ─→ ImageChooserBlock          │
│                     (appears if media_type    │
│                      != 'video')               │
│                                                │
│  • Videodatei    ─→ DocumentChooserBlock       │
│                     (appears if needed)        │
│                                                │
│  • Alt-Text      ─→ CharField for a11y         │
│                                                │
│  ──────────────────────────────────────────    │
│                                                │
│  [Other Fields - unchanged]                    │
│  • Beschreibung                                │
│  • Autor                                       │
│  • Datum                                       │
│  • etc.                                        │
└────────────────────────────────────────────────┘
```

## Browser Compatibility

```
┌──────────────────────────────────────────────────┐
│  Modern Browsers (with fallback strategy)        │
├──────────────────────────────────────────────────┤
│                                                  │
│  Videos:                                         │
│  ┌──────────────────────────────────────────┐  │
│  │ <video>                                  │  │
│  │   <source src="..." type="video/mp4">    │  │
│  │   <source src="..." type="video/webm">   │  │
│  │ </video>                                 │  │
│  │                                          │  │
│  │ • Chrome/Edge: MP4 ✓ WebM ✓ Ogg ✓      │  │
│  │ • Firefox: WebM ✓ Ogg ✓ (not MP4)       │  │
│  │ • Safari: MP4 ✓ (not WebM)               │  │
│  │ • Mobile: MP4 ✓ (best support)           │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  Images:                                         │
│  ┌──────────────────────────────────────────┐  │
│  │ {% image %} → srcset + multiple formats  │  │
│  │ Fallback: <img src="...">                │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  GIFs:                                           │
│  ┌──────────────────────────────────────────┐  │
│  │ <img src="animated.gif">                 │  │
│  │ • All modern browsers ✓                  │  │
│  │ • Native animation ✓                     │  │
│  └──────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## Migration Path (Old → New)

```
Existing Site:
    ├─ PhotoPage.photo (ForeignKey to wagtailimages.Image) ✓
    └─ GalleryPage.cover_image (same) ✓

After Enhancement:
    ├─ PhotoPage.photo (still works) ✓
    ├─ NEW: PhotoPage.image (ImageField)
    ├─ NEW: PhotoPage.video (FileField)
    ├─ NEW: PhotoPage.media_type (CharField)
    └─ NEW: PhotoPage.media_alt_text (CharField)

Optional Migration:
    • Can gradually add new fields to existing PhotoPages
    • Old photo field acts as fallback
    • No data loss or breaking changes
```

## Key Design Decisions

1. **Mixin-based approach**
   - Reusable across multiple models
   - Clean separation of concerns
   - Easy to apply to future models

2. **Multiple file handling**
   - Separate fields for images and videos
   - media_type field acts as router
   - Clear intent in admin interface

3. **Template flexibility**
   - media_with_caption.html for block rendering
   - media_renderer.html for media-type logic
   - Composable and reusable

4. **Backward compatibility**
   - Old fields still exist and work
   - Fallback rendering logic in templates
   - No breaking changes to API

5. **Accessibility first**
   - Alt text field for all media
   - Proper semantic HTML
   - Accessible video controls

## Performance Considerations

```
                Upload          Storage        Delivery
                
Images      ──────────────────────────────────────────
            • Wagtail      • Per-folder/    • Optimized
            • ResizeImage  month dated      • Srcset

GIFs        ──────────────────────────────────────────
            • Direct upload• images/YYYY/MM • Direct serve
            • No resize    • No optimization• Consider size

Videos      ──────────────────────────────────────────
            • Direct upload• videos/YYYY/MM • Consider CDN
            • No transcode • Separate folder• Multiple formats
```
