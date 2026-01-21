"""
Utility functions for expense report receipt processing.
Handles file validation and combining multiple files into a single PDF.
"""

import os
import io
from PIL import Image
from PyPDF2 import PdfMerger, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile


# File size limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB total

# Allowed file types
ALLOWED_IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/jpg'}
ALLOWED_PDF_TYPE = 'application/pdf'
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf'}


def validate_receipt_file(uploaded_file):
    """
    Validate an uploaded receipt file.
    
    Args:
        uploaded_file: Django UploadedFile object
        
    Raises:
        ValidationError: If file is invalid
    """
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f'File {uploaded_file.name} is too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB.'
        )
    
    # Check file extension
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'File type {ext} is not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        )
    
    # Check content type
    content_type = uploaded_file.content_type
    if content_type not in ALLOWED_IMAGE_TYPES and content_type != ALLOWED_PDF_TYPE:
        raise ValidationError(
            f'Invalid file type: {content_type}. Only PNG, JPEG, and PDF files are allowed.'
        )
    
    return True


def validate_receipt_files(files):
    """
    Validate multiple receipt files.
    
    Args:
        files: List of Django UploadedFile objects
        
    Raises:
        ValidationError: If any file is invalid or total size exceeds limit
    """
    if not files:
        raise ValidationError('At least one receipt file is required.')
    
    # Check total size
    total_size = sum(f.size for f in files)
    if total_size > MAX_TOTAL_SIZE:
        raise ValidationError(
            f'Total file size is too large. Maximum total size is {MAX_TOTAL_SIZE / (1024*1024):.0f}MB.'
        )
    
    # Validate each file
    for uploaded_file in files:
        validate_receipt_file(uploaded_file)
    
    return True


def image_to_pdf_bytes(image_file):
    """
    Convert an image file to PDF bytes.
    
    Args:
        image_file: Django UploadedFile object containing an image
        
    Returns:
        BytesIO object containing PDF data
    """
    # Open the image
    image = Image.open(image_file)
    
    # Convert to RGB if necessary (for PNG with transparency)
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Get image dimensions
    img_width, img_height = image.size
    
    # Determine page size based on image orientation
    # Use letter size and scale image to fit
    page_width, page_height = letter
    
    # Calculate scaling to fit page while maintaining aspect ratio
    width_ratio = page_width / img_width
    height_ratio = page_height / img_height
    scale_ratio = min(width_ratio, height_ratio) * 0.95  # 95% to add margins
    
    new_width = img_width * scale_ratio
    new_height = img_height * scale_ratio
    
    # Center image on page
    x_offset = (page_width - new_width) / 2
    y_offset = (page_height - new_height) / 2
    
    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    # Save image to temporary buffer for reportlab
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='JPEG', quality=95)
    img_buffer.seek(0)
    
    # Draw image on PDF
    c.drawImage(
        ImageReader(img_buffer),
        x_offset,
        y_offset,
        width=new_width,
        height=new_height,
        preserveAspectRatio=True
    )
    
    c.save()
    pdf_buffer.seek(0)
    
    return pdf_buffer


def combine_receipts_to_pdf(uploaded_files):
    """
    Combine multiple receipt files (images and PDFs) into a single PDF.
    
    Args:
        uploaded_files: List of Django UploadedFile objects
        
    Returns:
        BytesIO object containing the combined PDF
    """
    merger = PdfMerger()
    
    try:
        for uploaded_file in uploaded_files:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Determine file type
            content_type = uploaded_file.content_type
            
            if content_type in ALLOWED_IMAGE_TYPES:
                # Convert image to PDF
                pdf_bytes = image_to_pdf_bytes(uploaded_file)
                merger.append(pdf_bytes)
            
            elif content_type == ALLOWED_PDF_TYPE:
                # Add PDF directly
                merger.append(uploaded_file)
            
            else:
                raise ValidationError(f'Unsupported file type: {content_type}')
        
        # Write combined PDF to buffer
        output_buffer = io.BytesIO()
        merger.write(output_buffer)
        merger.close()
        
        output_buffer.seek(0)
        return output_buffer
    
    except Exception as e:
        merger.close()
        raise ValidationError(f'Error combining receipt files: {str(e)}')


def create_receipt_filename(expense_report):
    """
    Create a filename for the combined receipt PDF.
    
    Args:
        expense_report: ExpenseReport instance
        
    Returns:
        String filename
    """
    member_id = expense_report.member.member_id
    report_id = expense_report.id
    timestamp = expense_report.created_at.strftime('%Y%m%d')
    
    return f'receipt_{member_id}_{report_id}_{timestamp}.pdf'
