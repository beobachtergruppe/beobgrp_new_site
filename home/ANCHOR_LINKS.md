# Anchor Link Feature

## Overview
This feature allows you to create anchor links to specific headings within pages in the Wagtail CMS. Anchors are automatically generated for all h1, h2, and h3 heading blocks and follow the `block-*` naming convention.

## How It Works

### 1. Automatic Anchor Generation
- When you add an h1, h2, or h3 heading block to a page, an anchor ID is automatically generated
- The anchor ID is based on the heading text, slugified with the prefix `block-`
- Example: Heading "Über Uns" becomes anchor `block-uber-uns`

### 2. Using Anchors in Links

#### In RichTextBlock (Rich Text Editor):
1. Select text and click the link button
2. Choose "Link to a page"
3. Select the target page
4. **New**: A dropdown will appear showing available anchors on that page
5. Select an anchor from the dropdown (or leave it blank to link to the page top)
6. The anchor will be automatically appended to the URL

#### Manual Method:
You can also manually add anchors by typing `#block-anchor-name` in the URL field.

### 3. Anchor Format
All anchors follow this pattern:
- Format: `block-{slugified-heading-text}`
- Example: "Programm 2024" → `block-programm-2024`

## Technical Details

### Files Modified/Created:
- `home/models/common.py`: Added `HeadingBlock` class and `generate_anchor_id()` function
- `home/wagtail_hooks/anchor_chooser.py`: API endpoint and JavaScript for anchor selection
- `beobgrp_site/templates/blocks/heading_block.html`: Template for rendering headings with anchors
- `beobgrp_site/static/css/beobgrp_site.scss`: Styling for anchor targets

### API Endpoint:
- URL: `/admin/api/anchors/<page_id>/`
- Returns: JSON list of available anchors for a page
- Format: `{"anchors": [{"id": "block-heading", "text": "Heading Text"}]}`

### Anchor Extraction:
Pages that inherit from `CommonContextMixin` have a `get_anchors()` method that:
- Scans the page's StreamField body
- Extracts all h1, h2, h3 blocks
- Returns a list of (anchor_id, heading_text) tuples

## Example Usage

### In Template:
```html
<!-- Link to a specific section -->
<a href="{% pageurl some_page %}#block-section-title">Go to Section</a>
```

### In Python:
```python
# Get all anchors from a page
page = HomePage.objects.first()
anchors = page.get_anchors()
# Returns: [('block-welcome', 'Welcome'), ('block-about', 'About Us')]
```

### In RichTextBlock:
Simply use the visual editor - select a page and then choose an anchor from the dropdown.

## Styling
Anchors have special CSS that:
- Makes them targetable for navigation
- Adds scroll offset (2rem) to account for headers
- Uses `scroll-margin-top` for smooth scrolling to anchored content

## Notes
- Only h1, h2, and h3 blocks generate anchors (not h4, h5 from RichTextBlock)
- Anchor IDs are regenerated each time based on heading text
- Anchors are case-insensitive and special characters are removed
- The `block-` prefix helps identify auto-generated anchors
