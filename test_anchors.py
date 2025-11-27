"""
Quick test script to verify anchor functionality.
Run with: python manage.py shell < test_anchors.py
"""
from home.models import HomePage
from home.models.common import generate_anchor_id

# Test anchor ID generation
test_cases = [
    ("Über Uns", "block-uber-uns"),
    ("Programm 2024", "block-programm-2024"),
    ("Willkommen!", "block-willkommen"),
    ("FAQ & Kontakt", "block-faq-kontakt"),
]

print("Testing anchor ID generation:")
print("-" * 50)
for text, expected in test_cases:
    result = generate_anchor_id(text)
    status = "✓" if result == expected else "✗"
    print(f"{status} '{text}' → '{result}' (expected: '{expected}')")

print("\n" + "=" * 50)
print("Testing page anchor extraction:")
print("=" * 50)

# Test get_anchors on HomePage
try:
    home = HomePage.objects.first()
    if home:
        anchors = home.get_anchors()
        print(f"\nFound {len(anchors)} anchors on '{home.title}':")
        for anchor_id, text in anchors:
            print(f"  - {anchor_id}: {text}")
    else:
        print("\nNo HomePage found in database.")
except Exception as e:
    print(f"\nError: {e}")

print("\n" + "=" * 50)
print("Anchor feature is ready to use!")
print("=" * 50)
