# Debugging Guide for Anchor Link Feature

## Quick Test Steps

1. **Restart the development server:**
   ```bash
   python manage.py runserver 8001
   ```

2. **Open browser console (F12) and check for logs:**
   - Should see: `[Anchor Chooser] Script initialized`

3. **Test the anchor feature:**
   - Go to Wagtail admin
   - Edit a page with RichTextBlock content
   - Select some text
   - Click the link icon (🔗) in the toolbar
   - Choose "Link zu einer Seite" or "Link to a page"
   - Select a page from the chooser
   - **Expected:** After selecting a page, you should see a dropdown "Anker auf der Seite:" below the URL field
   - **Check console:** Should see logs like:
     - `[Anchor Chooser] Found page chooser modal`
     - `[Anchor Chooser] Page selected: <page_id>`
     - `[Anchor Chooser] Anchors received: X`

## Troubleshooting

### If you don't see the anchor dropdown:

1. **Check browser console for errors:**
   - Press F12
   - Go to Console tab
   - Look for `[Anchor Chooser]` messages

2. **Verify API endpoint works:**
   - Open a new browser tab
   - Go to: `http://localhost:8001/admin/api/anchors/2/` (replace 2 with a valid page ID)
   - Should see JSON response: `{"anchors": [...]}`

3. **Check if page has anchors:**
   - Make sure the page you're linking to has h1, h2, or h3 heading blocks
   - Test API: `curl http://localhost:8001/admin/api/anchors/<page_id>/`

4. **Clear browser cache:**
   - Sometimes JavaScript is cached
   - Hard refresh: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (Mac)

5. **Check Wagtail version compatibility:**
   ```bash
   python -c "import wagtail; print(wagtail.__version__)"
   ```
   Should be 7.1.2

## Manual Testing

To manually test without the UI:

```python
python manage.py shell
```

```python
from home.models import HomePage
from home.models.common import generate_anchor_id

# Test anchor generation
print(generate_anchor_id("Test Heading"))  # Should print: block-test-heading

# Test anchor extraction
page = HomePage.objects.first()
if page:
    print(f"Page: {page.title}")
    anchors = page.get_anchors()
    print(f"Anchors: {anchors}")
```

## Common Issues

### 1. No anchors showing up
- Make sure the target page has h1, h2, or h3 blocks (not just RichTextBlock paragraphs)
- h4 and h5 inside RichTextBlock don't generate anchors

### 2. JavaScript not loading
- Check that `insert_global_admin_js` hook is registered
- Verify home/wagtail_hooks/__init__.py imports both anchor_chooser and anchor_link_feature

### 3. API returns empty array
- The page might not have CommonContextMixin (check if page model inherits from it)
- HomePage, EventPage, GalleryPage should all work

## Alternative: Manual Anchor Entry

If the dropdown doesn't appear, you can still manually add anchors:

1. In the link dialog, after selecting a page
2. The URL field shows something like: `/page/slug/`
3. Manually append: `/page/slug/#block-your-anchor`
4. Click "Insert Link"

This should work even if the JavaScript enhancement fails.

## Getting Help

If issues persist, check:
1. Browser console logs (F12 → Console)
2. Django development server logs
3. Network tab (F12 → Network) - check if `/admin/api/anchors/` calls succeed
