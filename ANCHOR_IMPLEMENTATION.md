# Anchor Link Implementation Summary

## What Was Implemented

This implementation adds automatic anchor generation and selection for internal page links in Wagtail CMS. When editors create links in rich text, they can now see and select from available heading anchors on the target page.

## Key Features

### 1. **Automatic Anchor Generation**
- All h1, h2, and h3 heading blocks now automatically generate anchor IDs
- Anchors follow the `block-*` naming convention (e.g., `block-programm-2024`)
- Anchor IDs are based on slugified heading text

### 2. **Anchor Selection UI**
- When linking to a page in the rich text editor, a dropdown appears showing available anchors
- Dropdown is automatically populated by fetching anchors from the selected page
- Users can select an anchor or leave blank to link to the top of the page

### 3. **API Endpoint**
- New endpoint: `/admin/api/anchors/<page_id>/`
- Returns JSON list of available anchors for any page
- Only includes anchors from h1, h2, h3 blocks (matching `block-*` pattern)

## Files Created/Modified

### New Files
1. **`home/wagtail_hooks/__init__.py`** - Wagtail hooks module initialization
2. **`home/wagtail_hooks/anchor_chooser.py`** - API endpoint and JavaScript for anchor selection
3. **`beobgrp_site/templates/blocks/heading_block.html`** - Template for rendering headings with anchors
4. **`home/ANCHOR_LINKS.md`** - User documentation
5. **`test_anchors.py`** - Test script for anchor functionality

### Modified Files
1. **`home/models/common.py`**
   - Added `generate_anchor_id()` function
   - Created custom `HeadingBlock` class
   - Updated `gen_body_content` to use `HeadingBlock` for h1, h2, h3
   - Added `get_anchors()` method to `CommonContextMixin`

2. **`beobgrp_site/static/css/beobgrp_site.scss`**
   - Added styling for anchor targets with scroll offset
   - Added `span[id^="block-"]` selector for anchor positioning

3. **`home/migrations/0011_alter_eventpage_body_alter_homepage_body.py`**
   - Migration to update StreamField block definitions

## How It Works

### Backend Flow
1. When a page is saved, `HeadingBlock` generates anchor IDs for all h1, h2, h3 blocks
2. Anchor IDs are created using `generate_anchor_id()` which slugifies the heading text
3. The `get_anchors()` method scans the page's StreamField and returns all available anchors

### Frontend Flow
1. Editor creates a link in rich text and selects a page
2. JavaScript listens for page selection event
3. AJAX request fetches anchors from `/admin/api/anchors/<page_id>/`
4. Dropdown is dynamically created and populated with available anchors
5. When anchor is selected, it's appended to the URL (e.g., `/page/#block-section`)

### Rendering
1. `HeadingBlock` template wraps heading text in `<span id="block-...">` tags
2. CSS ensures proper scroll positioning with `scroll-margin-top`
3. Links to anchors work seamlessly in frontend

## Usage Examples

### In Wagtail Admin
1. Edit a page with rich text content
2. Select text and click "Link" button
3. Choose "Link to a page" 
4. Select target page
5. **New**: Dropdown appears with available anchors
6. Select anchor or leave blank

### In Templates
```html
<!-- Link to specific section -->
<a href="{% pageurl some_page %}#block-section-name">Jump to Section</a>
```

### In Python
```python
# Get all anchors from a page
page = HomePage.objects.first()
anchors = page.get_anchors()
# Returns: [('block-welcome', 'Welcome'), ('block-about', 'About')]
```

## Testing

All 23 existing tests pass without modifications:
```bash
python manage.py test home.tests
# Ran 23 tests in 0.057s - OK
```

Anchor generation tested with various text inputs:
- German umlauts: "Über Uns" → "block-uber-uns"
- Special characters: "FAQ & Kontakt" → "block-faq-kontakt"
- Numbers: "Programm 2024" → "block-programm-2024"

## Technical Details

### Anchor ID Format
- **Pattern**: `block-{slugified-text}`
- **Slugification**: Django's `slugify()` handles:
  - Lowercase conversion
  - Special character removal
  - Space to hyphen conversion
  - Umlauts and accents normalization

### Compatibility
- Works with Wagtail 7.1.2
- Compatible with Django 5.2.7
- Uses standard Wagtail hooks (`register_admin_urls`, `insert_editor_js`)
- No external dependencies required

### Limitations
- Only h1, h2, h3 blocks generate anchors (not h4, h5 from RichTextBlock)
- Anchor IDs regenerate on each save (based on current heading text)
- Requires JavaScript enabled in admin for dropdown functionality
- Manual anchor entry still works if JavaScript fails

## Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Uses standard APIs: `fetch()`, DOM manipulation, CSS `scroll-margin-top`
- Graceful degradation: manual anchor entry works without JS

## Next Steps (Optional Enhancements)
1. Add visual indicator showing which headings have anchors
2. Add "copy anchor link" button in admin preview
3. Support for anchors in RichTextBlock h4, h5 headings
4. Add anchor validation (warn if target anchor doesn't exist)
5. Create sitemap of page anchors in admin

## Rollback Instructions
If needed, to rollback this feature:
```bash
# Revert migration
python manage.py migrate home 0010

# Revert code changes
git checkout HEAD~1 -- home/models/common.py
git checkout HEAD~1 -- beobgrp_site/static/css/beobgrp_site.scss

# Remove new files
rm -rf home/wagtail_hooks/
rm beobgrp_site/templates/blocks/heading_block.html
rm home/ANCHOR_LINKS.md
rm test_anchors.py

# Regenerate CSS
python manage.py compress --force
```

## Support
See `home/ANCHOR_LINKS.md` for user documentation and examples.
