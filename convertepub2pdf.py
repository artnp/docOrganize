#!/usr/bin/env python3
"""
EPUB to PDF Converter
Converts EPUB files to PDF format using ebooklib and reportlab
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional
import tempfile
import shutil

try:
    from ebooklib import epub
    import ebooklib
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import re
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install required packages:")
    print("pip install ebooklib reportlab beautifulsoup4")
    sys.exit(1)


class EPUBToPDFConverter:
    def __init__(self, page_size: str = 'A4', margin: float = 0.75):
        """Initialize the converter with page settings"""
        self.page_size = A4 if page_size.upper() == 'A4' else letter
        self.margin = margin * inch
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor='#2E4057'
        )
        
        # Heading styles
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor='#2E4057'
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        )
        
    def _clean_html_text(self, html_content: str) -> str:
        """Clean HTML content and extract plain text"""
        if not html_content:
            return ""
            
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace but preserve paragraph structure
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Replace problematic characters
        text = text.replace('—', '-')
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        text = text.replace(''', "'")
        text = text.replace(''', "'")
        text = text.replace('…', '...')
        
        return text
        
    def _extract_chapter_content(self, chapter) -> str:
        """Extract text content from an EPUB chapter"""
        try:
            if hasattr(chapter, 'get_body_content'):
                content = chapter.get_body_content()
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                return self._clean_html_text(content)
            elif hasattr(chapter, 'content'):
                content = chapter.content
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                return self._clean_html_text(content)
            else:
                return str(chapter)
        except Exception as e:
            print(f"Warning: Could not extract content from chapter: {e}")
            return ""
            
    def _get_book_metadata(self, epub_book) -> dict:
        """Extract metadata from EPUB book"""
        metadata = {
            'title': 'Unknown Title',
            'author': 'Unknown Author',
            'language': 'en'
        }
        
        try:
            # Try different metadata formats
            if hasattr(epub_book, 'metadata') and epub_book.metadata:
                # Check Dublin Core metadata
                if 'DC' in epub_book.metadata:
                    dc_metadata = epub_book.metadata['DC']
                    
                    # Extract title
                    if 'title' in dc_metadata and dc_metadata['title']:
                        metadata['title'] = str(dc_metadata['title'][0])
                    
                    # Extract author/creator
                    if 'creator' in dc_metadata and dc_metadata['creator']:
                        metadata['author'] = str(dc_metadata['creator'][0])
                    elif 'contributor' in dc_metadata and dc_metadata['contributor']:
                        metadata['author'] = str(dc_metadata['contributor'][0])
                    
                    # Extract language
                    if 'language' in dc_metadata and dc_metadata['language']:
                        metadata['language'] = str(dc_metadata['language'][0])
                
                # Try direct metadata access
                elif hasattr(epub_book, 'title') and epub_book.title:
                    metadata['title'] = str(epub_book.title)
                elif hasattr(epub_book, 'get_metadata'):
                    title_meta = epub_book.get_metadata('DC', 'title')
                    if title_meta:
                        metadata['title'] = str(title_meta[0][0])
                    
                    author_meta = epub_book.get_metadata('DC', 'creator')
                    if author_meta:
                        metadata['author'] = str(author_meta[0][0])
                
        except Exception as e:
            print(f"Warning: Could not extract metadata: {e}")
            
        return metadata
        
    def convert_epub_to_pdf(self, epub_path: str, pdf_path: str) -> bool:
        """Convert EPUB file to PDF"""
        try:
            print(f"Converting {epub_path} to {pdf_path}...")
            
            # Read EPUB file
            epub_book = epub.read_epub(epub_path)
            
            # Get metadata
            metadata = self._get_book_metadata(epub_book)
            print(f"Title: {metadata['title']}")
            print(f"Author: {metadata['author']}")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=self.page_size,
                leftMargin=self.margin,
                rightMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Build story content
            story = []
            
            # Add title page
            story.append(Paragraph(metadata['title'], self.title_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"By: {metadata['author']}", self.styles['Normal']))
            story.append(PageBreak())
            
            # Extract and add chapters
            chapters = list(epub_book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            
            if not chapters:
                print("Warning: No chapters found in EPUB file")
                return False
                
            for i, chapter in enumerate(chapters, 1):
                print(f"Processing chapter {i}/{len(chapters)}...")
                
                # Extract chapter content
                content = self._extract_chapter_content(chapter)
                
                if content:
                    # Add chapter content to story
                    paragraphs = content.split('\n')
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            # Skip very short lines (likely page numbers or headers)
                            if len(para) < 3:
                                continue
                            
                            # Check if it might be a heading
                            if len(para) < 100 and (para.istitle() or para.isupper()):
                                story.append(Paragraph(para, self.heading_style))
                            else:
                                # Clean paragraph for ReportLab
                                para = para.replace('&', '&amp;')
                                para = para.replace('<', '&lt;')
                                para = para.replace('>', '&gt;')
                                story.append(Paragraph(para, self.body_style))
                            story.append(Spacer(1, 6))
                    
                    # Add page break between chapters (except last one)
                    if i < len(chapters):
                        story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            print(f"Successfully converted {epub_path} to {pdf_path}")
            return True
            
        except Exception as e:
            print(f"Error converting EPUB to PDF: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Convert EPUB files to PDF format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convertepub2pdf.py book.epub
  python convertepub2pdf.py book.epub -o output.pdf
  python convertepub2pdf.py *.epub --page-size A4
        """
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='Input EPUB file(s) to convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file (only valid for single input file)'
    )
    
    parser.add_argument(
        '--page-size',
        choices=['A4', 'letter'],
        default='A4',
        help='Page size for PDF (default: A4)'
    )
    
    parser.add_argument(
        '--margin',
        type=float,
        default=0.75,
        help='Page margin in inches (default: 0.75)'
    )
    
    parser.add_argument(
        '--delete-epub',
        action='store_true',
        help='Delete EPUB file after successful conversion'
    )
    
    args = parser.parse_args()
    
    # Create converter
    converter = EPUBToPDFConverter(
        page_size=args.page_size,
        margin=args.margin
    )
    
    # Process files
    success_count = 0
    total_count = len(args.input_files)
    
    for epub_file in args.input_files:
        # Check if input file exists
        if not os.path.exists(epub_file):
            print(f"Error: Input file '{epub_file}' not found")
            continue
            
        # Determine output file path
        if args.output and total_count == 1:
            pdf_file = args.output
        else:
            epub_path = Path(epub_file)
            pdf_file = epub_path.with_suffix('.pdf')
        
        # Convert file
        if converter.convert_epub_to_pdf(epub_file, str(pdf_file)):
            success_count += 1
            
            # Delete EPUB file if requested and conversion was successful
            if args.delete_epub:
                try:
                    if os.path.exists(epub_file):
                        os.remove(epub_file)
                        print(f"Deleted original EPUB file: {epub_file}")
                    else:
                        print(f"Warning: EPUB file not found for deletion: {epub_file}")
                except PermissionError:
                    print(f"Permission denied: Cannot delete {epub_file}")
                    print("Try running as administrator or move the file to a different location")
                except Exception as e:
                    print(f"Warning: Could not delete EPUB file {epub_file}: {e}")
        else:
            print(f"Failed to convert {epub_file}")
    
    print(f"\nConversion complete: {success_count}/{total_count} files converted successfully")
    
    if success_count == 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
