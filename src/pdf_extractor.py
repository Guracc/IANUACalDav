"""
PDF extraction module for extracting text from locandina PDFs.
"""

import requests
import pdfplumber
import io
import re
from typing import Optional

class PDFExtractor:
    """
    Handles downloading and extracting text from PDF files.
    """
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_url: str) -> Optional[str]:
        """
        Download a PDF from URL and extract all text content.
        
        Args:
            pdf_url: The URL of the PDF to extract text from
            
        Returns:
            Extracted text content, or None if extraction fails
        """
        try:
            # Download the PDF
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Extract text using pdfplumber
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text.strip() if text else None
                
        except requests.RequestException as e:
            print(f"Error downloading PDF {pdf_url}: {e}")
            return None
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_url}: {e}")
            return None

    def extract_location_from_pdf(self, pdf_url: str) -> Optional[str]:
        """
        Download a PDF and extract the location information.
        
        Args:
            pdf_url: The URL of the PDF
            
        Returns:
            Location string or None
        """
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # Find location after time pattern
                # Look for pattern like "Dalle ore 09:00 alle 13:00" followed by location
                time_pattern = r"Dalle ore.*?alle.*?(?=\n\n|\n[A-Z]|\Z)"
                match = re.search(time_pattern, text, re.DOTALL)
                if match:
                    # Get text after the time line
                    after_time = text[match.end():].strip()
                    # Take first few lines as location, stop before ABSTRACT
                    lines = after_time.split('\n')
                    location_lines = []
                    for line in lines:
                        line = line.strip()
                        if not line or 'ABSTRACT' in line.upper():
                            break
                        location_lines.append(line)
                    location = '\n'.join(location_lines[:3])  # Usually 2-3 lines
                    return location if location else None
                
                return None
                
        except Exception as e:
            print(f"Error extracting location from PDF {pdf_url}: {e}")
            return None

    def extract_speaker_info(self, pdf_url: str) -> Optional[str]:
        """
        Extract speaker information from PDF.
        
        Args:
            pdf_url: The URL of the PDF
            
        Returns:
            Speaker information string or None
        """
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # Look for speaker info after title
                lines = text.split('\n')
                speaker_lines = []
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip title (all caps lines that are likely titles)
                    if line.isupper() and len(line) > 10 and not any(char.isdigit() for char in line):
                        continue
                    
                    # Stop at date (starts with number)
                    if re.match(r'^\d+', line):
                        break
                    
                    # Skip time and location patterns
                    if 'Dalle ore' in line or 'Polo Didattico' in line or 'Via ' in line:
                        break
                    
                    # Look for speaker name (contains name-like patterns)
                    if (len(line.split()) >= 2 and 
                        not any(word in line.upper() for word in ['INDIRIZZO', 'ANNO', 'CL3', 'LMCU', 'ISB', 'DIFAR']) and
                        not line.isupper()):  # Not all caps
                        # Check if this looks like a name (has title words or is name-like)
                        if (any(title in line for title in ['Prof', 'Dott', 'Dr', 'Direzione', 'Segretario']) or
                            (len(line.split()) == 2 and not any(char.isdigit() for char in line))):
                            # This is likely speaker info
                            speaker_lines.append(line)
                            # Add next few lines that are likely bio
                            for j in range(i+1, min(i+4, len(lines))):
                                next_line = lines[j].strip()
                                if (next_line and 
                                    not next_line.isupper() and 
                                    not re.match(r'^\d+', next_line) and
                                    not 'Dalle ore' in next_line and
                                    not 'Polo Didattico' in next_line):
                                    speaker_lines.append(next_line)
                                else:
                                    break
                            break
                
                speaker_info = '\n'.join(speaker_lines).strip()
                return speaker_info if speaker_info else None
                
        except Exception as e:
            print(f"Error extracting speaker from PDF {pdf_url}: {e}")
            return None

def extract_pdf_text(pdf_url: str) -> Optional[str]:
    """
    Convenience function to extract text from a PDF URL.
    
    Args:
        pdf_url: The URL of the PDF
        
    Returns:
        Extracted text or None
    """
    extractor = PDFExtractor()
    return extractor.extract_text_from_pdf(pdf_url)

def extract_pdf_location(pdf_url: str) -> Optional[str]:
    """
    Convenience function to extract location from a PDF URL.
    
    Args:
        pdf_url: The URL of the PDF
        
    Returns:
        Location string or None
    """
    extractor = PDFExtractor()
    return extractor.extract_location_from_pdf(pdf_url)

def extract_pdf_speaker_info(pdf_url: str) -> Optional[str]:
    """
    Convenience function to extract speaker information from a PDF URL.
    
    Args:
        pdf_url: The URL of the PDF
        
    Returns:
        Speaker information string or None
    """
    extractor = PDFExtractor()
    return extractor.extract_speaker_info(pdf_url)

def extract_pdf_speaker(pdf_url: str) -> Optional[str]:
    """
    Convenience function to extract speaker info from a PDF URL.
    
    Args:
        pdf_url: The URL of the PDF
        
    Returns:
        Speaker info or None
    """
    extractor = PDFExtractor()
    return extractor.extract_speaker_info(pdf_url)