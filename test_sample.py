"""
Sample Test - Create a test image with text for OCR testing
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_aadhaar():
    """Create a sample Aadhaar-like image for testing"""
    # Create image
    img = Image.new('RGB', (800, 500), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw header
    draw.rectangle([(0, 0), (800, 80)], fill='#0066cc')
    draw.text((250, 25), "AADHAAR", fill='white', font=font_large)
    draw.text((200, 90), "Unique Identification Authority of India", fill='black', font=font_small)
    
    # Draw content
    y = 150
    content = [
        ("Name:", "Ramesh Kumar", font_medium),
        ("Aadhaar Number:", "XXXX XXXX 1234", font_medium),
        ("Date of Birth:", "15/08/1990", font_small),
        ("Gender:", "Male", font_small),
        ("Address:", "123 MG Road, Pune 411001", font_small),
    ]
    
    for label, value, font in content:
        draw.text((50, y), label, fill='#666666', font=font_small)
        draw.text((250, y), value, fill='black', font=font)
        y += 40
    
    # Save
    os.makedirs('test_documents', exist_ok=True)
    img.save('test_documents/sample_aadhaar.png')
    print("✅ Created: test_documents/sample_aadhaar.png")

def create_sample_invoice():
    """Create a sample invoice image for testing"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 28)
        font_medium = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Header
    draw.text((300, 30), "TAX INVOICE", fill='black', font=font_large)
    
    # Content
    y = 100
    content = [
        ("Invoice No:", "INV-2024-001", font_medium),
        ("Invoice Date:", "08/05/2026", font_small),
        ("", "", font_small),
        ("Vendor:", "ABC Company Pvt Ltd", font_medium),
        ("GSTIN:", "27AABCU9603R1ZX", font_small),
        ("", "", font_small),
        ("Customer:", "XYZ Enterprises", font_medium),
        ("", "", font_small),
        ("Item: Laptop", "Qty: 2", font_small),
        ("Unit Price: 50000", "Amount: 100000", font_small),
        ("", "", font_small),
        ("Subtotal:", "100000.00", font_medium),
        ("CGST (9%):", "9000.00", font_small),
        ("SGST (9%):", "9000.00", font_small),
        ("Total Amount:", "118000.00", font_large),
    ]
    
    for label, value, font in content:
        if label:
            draw.text((50, y), label, fill='#666666', font=font_small)
        if value:
            draw.text((400, y), value, fill='black', font=font)
        y += 35
    
    # Save
    img.save('test_documents/sample_invoice.png')
    print("✅ Created: test_documents/sample_invoice.png")

if __name__ == "__main__":
    print("🎨 Creating sample test documents...")
    create_sample_aadhaar()
    create_sample_invoice()
    print("\n✅ Sample documents created in 'test_documents/' folder")
    print("You can use these to test the application!")
