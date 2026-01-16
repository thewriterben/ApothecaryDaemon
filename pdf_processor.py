#!/usr/bin/env python3
"""
PDF Processor for ApothecaryDaemon

This module extracts herbal medicine data from PDF documents and builds a database
of substances that can be integrated into the ApothecaryDaemon application.

Features:
- Multiple PDF extraction methods with fallbacks (pdfplumber, PyPDF2, OCR)
- Pattern matching for herb identification
- Tradition detection from filename patterns
- Export to JSON and Python code generation
"""

import os
import re
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict

# Optional imports with graceful degradation
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ExtractedHerb:
    """Represents an herb extracted from PDF documents"""
    name: str
    scientific_name: Optional[str] = None
    common_names: List[str] = field(default_factory=list)
    traditional_uses: List[str] = field(default_factory=list)
    preparation_methods: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    interactions: List[str] = field(default_factory=list)
    source_document: str = ""
    tradition: str = ""

    def merge_with(self, other: 'ExtractedHerb') -> None:
        """Merge data from another ExtractedHerb instance"""
        if other.scientific_name and not self.scientific_name:
            self.scientific_name = other.scientific_name
        
        # Merge lists, avoiding duplicates
        self.common_names = list(set(self.common_names + other.common_names))
        self.traditional_uses = list(set(self.traditional_uses + other.traditional_uses))
        self.preparation_methods = list(set(self.preparation_methods + other.preparation_methods))
        self.contraindications = list(set(self.contraindications + other.contraindications))
        self.interactions = list(set(self.interactions + other.interactions))
        
        # Append source document if different
        if other.source_document and other.source_document not in self.source_document:
            self.source_document += f"; {other.source_document}"


class PDFProcessor:
    """Processes PDF files to extract herbal medicine data"""
    
    # Dictionary of known herbs with scientific names
    KNOWN_HERBS = {
        "st. john's wort": "Hypericum perforatum",
        "st john's wort": "Hypericum perforatum",
        "hypericum": "Hypericum perforatum",
        "valerian": "Valeriana officinalis",
        "valerian root": "Valeriana officinalis",
        "kava": "Piper methysticum",
        "kava kava": "Piper methysticum",
        "ginseng": "Panax ginseng",
        "asian ginseng": "Panax ginseng",
        "panax ginseng": "Panax ginseng",
        "chamomile": "Matricaria chamomilla",
        "german chamomile": "Matricaria chamomilla",
        "ginkgo": "Ginkgo biloba",
        "ginkgo biloba": "Ginkgo biloba",
        "passionflower": "Passiflora incarnata",
        "echinacea": "Echinacea purpurea",
        "ginger": "Zingiber officinale",
        "turmeric": "Curcuma longa",
        "ashwagandha": "Withania somnifera",
        "brahmi": "Bacopa monnieri",
        "tulsi": "Ocimum sanctum",
        "holy basil": "Ocimum sanctum",
        "triphala": "Terminalia chebula, Terminalia bellirica, Phyllanthus emblica",
        "rhodiola": "Rhodiola rosea",
        "milk thistle": "Silybum marianum",
        "saw palmetto": "Serenoa repens",
        "black cohosh": "Actaea racemosa",
        "dong quai": "Angelica sinensis",
        "astragalus": "Astragalus membranaceus",
        "licorice": "Glycyrrhiza glabra",
        "peppermint": "Mentha piperita",
        "garlic": "Allium sativum",
        "gotu kola": "Centella asiatica",
        "hawthorn": "Crataegus monogyna",
    }
    
    # Patterns for tradition detection
    TRADITION_PATTERNS = {
        "Ayurveda": [r"ayurved", r"ayurvedic"],
        "Traditional Chinese Medicine": [r"tcm", r"chinese\s+medicine", r"chinese"],
        "Mediterranean/European": [r"mediterranean", r"european"],
        "African": [r"african", r"west\s+african"],
        "Latin American": [r"latin", r"mexican", r"dominican", r"south\s+america"],
        "Native American": [r"native\s+american"],
    }
    
    # Patterns for extracting information
    USE_PATTERNS = [
        r"used\s+for\s+(.+?)(?:\.|;|,\s+and\s+|\n)",
        r"traditional\s+use[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"medicinal\s+use[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"therapeutic\s+action[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"indication[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
    ]
    
    INTERACTION_PATTERNS = [
        r"interaction[s]?\s+with\s+(.+?)(?:\.|;|\n)",
        r"drug\s+interaction[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"contraindicated\s+with\s+(.+?)(?:\.|;|\n)",
    ]
    
    CONTRAINDICATION_PATTERNS = [
        r"contraindication[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"warning[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"caution[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"avoid\s+(.+?)(?:\.|;|\n)",
    ]
    
    PREPARATION_PATTERNS = [
        r"preparation[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"dosage[s]?\s*:?\s*(.+?)(?:\.|;|\n)",
        r"administered\s+as\s+(.+?)(?:\.|;|\n)",
        r"taken\s+as\s+(.+?)(?:\.|;|\n)",
    ]
    
    def __init__(self):
        """Initialize the PDF processor"""
        self.extracted_herbs: Dict[str, ExtractedHerb] = {}
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check and report available PDF processing libraries"""
        available = []
        missing = []
        
        if HAS_PDFPLUMBER:
            available.append("pdfplumber")
        else:
            missing.append("pdfplumber")
        
        if HAS_PYPDF2:
            available.append("PyPDF2")
        else:
            missing.append("PyPDF2")
        
        if HAS_OCR:
            available.append("pytesseract/pdf2image")
        else:
            missing.append("pytesseract/pdf2image")
        
        logger.info(f"Available PDF libraries: {', '.join(available) if available else 'None'}")
        if missing:
            logger.warning(f"Missing optional libraries: {', '.join(missing)}")
            logger.warning("Install with: pip install pdfplumber PyPDF2 pytesseract pdf2image Pillow")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using available methods
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Extracted text content
        """
        text = ""
        
        # Try pdfplumber first (most reliable)
        if HAS_PDFPLUMBER:
            try:
                text = self._extract_with_pdfplumber(pdf_path)
                if text.strip():
                    logger.info(f"Extracted text using pdfplumber from {os.path.basename(pdf_path)}")
                    return text
            except Exception as e:
                logger.warning(f"pdfplumber failed for {pdf_path}: {e}")
        
        # Fallback to PyPDF2
        if HAS_PYPDF2:
            try:
                text = self._extract_with_pypdf2(pdf_path)
                if text.strip():
                    logger.info(f"Extracted text using PyPDF2 from {os.path.basename(pdf_path)}")
                    return text
            except Exception as e:
                logger.warning(f"PyPDF2 failed for {pdf_path}: {e}")
        
        # Fallback to OCR
        if HAS_OCR:
            try:
                text = self._extract_with_ocr(pdf_path)
                if text.strip():
                    logger.info(f"Extracted text using OCR from {os.path.basename(pdf_path)}")
                    return text
            except Exception as e:
                logger.warning(f"OCR failed for {pdf_path}: {e}")
        
        logger.error(f"Failed to extract text from {pdf_path} - no working methods available")
        return ""
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber"""
        text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        text = []
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)
    
    def _extract_with_ocr(self, pdf_path: str, max_pages: int = 10) -> str:
        """Extract text using OCR (for scanned PDFs)"""
        logger.info(f"Using OCR for {pdf_path} (limited to first {max_pages} pages)")
        text = []
        images = convert_from_path(pdf_path, first_page=1, last_page=max_pages)
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            if page_text:
                text.append(page_text)
        return "\n".join(text)
    
    def detect_tradition(self, filename: str) -> str:
        """
        Detect the medical tradition from the filename
        
        Args:
            filename: Name of the PDF file
        
        Returns:
            Detected tradition or "General"
        """
        filename_lower = filename.lower()
        
        for tradition, patterns in self.TRADITION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, filename_lower):
                    return tradition
        
        return "General"
    
    def extract_herbs_from_text(self, text: str, source_document: str, tradition: str) -> List[ExtractedHerb]:
        """
        Extract herb information from text using pattern matching
        
        Args:
            text: Extracted text from PDF
            source_document: Name of source PDF file
            tradition: Medical tradition
        
        Returns:
            List of extracted herbs
        """
        herbs = []
        text_lower = text.lower()
        
        # Find known herbs in the text
        for common_name, scientific_name in self.KNOWN_HERBS.items():
            # Search for the herb name in text
            pattern = r'\b' + re.escape(common_name) + r'\b'
            if re.search(pattern, text_lower):
                herb = ExtractedHerb(
                    name=common_name.title(),
                    scientific_name=scientific_name,
                    source_document=source_document,
                    tradition=tradition
                )
                
                # Extract context around the herb mention
                context = self._extract_context(text, common_name, window=500)
                
                # Extract traditional uses
                for pattern in self.USE_PATTERNS:
                    matches = re.finditer(pattern, context, re.IGNORECASE)
                    for match in matches:
                        use = match.group(1).strip()
                        if use and len(use) > 3:
                            herb.traditional_uses.append(use[:200])  # Limit length
                
                # Extract interactions
                for pattern in self.INTERACTION_PATTERNS:
                    matches = re.finditer(pattern, context, re.IGNORECASE)
                    for match in matches:
                        interaction = match.group(1).strip()
                        if interaction and len(interaction) > 3:
                            herb.interactions.append(interaction[:200])
                
                # Extract contraindications
                for pattern in self.CONTRAINDICATION_PATTERNS:
                    matches = re.finditer(pattern, context, re.IGNORECASE)
                    for match in matches:
                        contraindication = match.group(1).strip()
                        if contraindication and len(contraindication) > 3:
                            herb.contraindications.append(contraindication[:200])
                
                # Extract preparation methods
                for pattern in self.PREPARATION_PATTERNS:
                    matches = re.finditer(pattern, context, re.IGNORECASE)
                    for match in matches:
                        preparation = match.group(1).strip()
                        if preparation and len(preparation) > 3:
                            herb.preparation_methods.append(preparation[:200])
                
                # Add common names from text
                herb.common_names.append(common_name)
                
                herbs.append(herb)
                logger.debug(f"Found {common_name} in {source_document}")
        
        return herbs
    
    def _extract_context(self, text: str, search_term: str, window: int = 500) -> str:
        """
        Extract context around a search term
        
        Args:
            text: Full text
            search_term: Term to search for
            window: Number of characters before and after
        
        Returns:
            Context text
        """
        text_lower = text.lower()
        search_lower = search_term.lower()
        
        contexts = []
        start = 0
        while True:
            pos = text_lower.find(search_lower, start)
            if pos == -1:
                break
            
            context_start = max(0, pos - window)
            context_end = min(len(text), pos + len(search_term) + window)
            contexts.append(text[context_start:context_end])
            
            start = pos + 1
        
        return " ... ".join(contexts)
    
    def process_pdf(self, pdf_path: str) -> List[ExtractedHerb]:
        """
        Process a single PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of extracted herbs
        """
        filename = os.path.basename(pdf_path)
        logger.info(f"Processing: {filename}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"No text extracted from {filename}")
            return []
        
        # Detect tradition
        tradition = self.detect_tradition(filename)
        logger.info(f"Detected tradition: {tradition}")
        
        # Extract herbs
        herbs = self.extract_herbs_from_text(text, filename, tradition)
        logger.info(f"Found {len(herbs)} herbs in {filename}")
        
        return herbs
    
    def process_directory(self, directory: str) -> Dict[str, ExtractedHerb]:
        """
        Process all PDF files in a directory
        
        Args:
            directory: Path to directory containing PDFs
        
        Returns:
            Dictionary of herbs (keyed by normalized name)
        """
        pdf_files = list(Path(directory).glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory}")
            return {}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_path in pdf_files:
            herbs = self.process_pdf(str(pdf_path))
            
            # Merge herbs with existing entries
            for herb in herbs:
                normalized_name = herb.name.lower()
                if normalized_name in self.extracted_herbs:
                    self.extracted_herbs[normalized_name].merge_with(herb)
                else:
                    self.extracted_herbs[normalized_name] = herb
        
        logger.info(f"Total unique herbs extracted: {len(self.extracted_herbs)}")
        return self.extracted_herbs
    
    def export_to_json(self, output_path: str):
        """
        Export extracted herbs to JSON file
        
        Args:
            output_path: Path to output JSON file
        """
        herbs_list = [asdict(herb) for herb in self.extracted_herbs.values()]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(herbs_list, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(herbs_list)} herbs to {output_path}")
    
    def _truncate_at_word_boundary(self, text: str, max_length: int) -> str:
        """
        Truncate text at word boundary without breaking words
        
        Args:
            text: Text to truncate
            max_length: Maximum length
        
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        # Find the last space before max_length
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            return truncated[:last_space]
        else:
            # No space found, return up to max_length
            return truncated
    
    def _escape_string(self, text: str) -> str:
        """
        Escape special characters for Python string literals
        
        Args:
            text: Text to escape
        
        Returns:
            Escaped text
        """
        # Replace backslashes first, then quotes
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        text = text.replace('\n', ' ')
        text = text.replace('\r', '')
        return text
    
    def generate_python_code(self) -> str:
        """
        Generate Python code that can be added to apothecary.py
        
        Returns:
            Python code as string
        """
        code_lines = [
            "# Generated code for apothecary.py integration",
            "# Add these substances to the _initialize_database method",
            "",
        ]
        
        for herb in sorted(self.extracted_herbs.values(), key=lambda h: h.name):
            # Create common names list
            common_names = [herb.name.lower()]
            if herb.scientific_name:
                common_names.append(herb.scientific_name.lower())
            common_names.extend([name.lower() for name in herb.common_names if name.lower() not in common_names])
            
            # Create primary effects list
            primary_effects = []
            for use in herb.traditional_uses[:3]:  # Use first 3 uses
                # Clean up the use text
                cleaned_use = use.split(',')[0].strip()
                if len(cleaned_use) < 50:
                    primary_effects.append(self._escape_string(cleaned_use))
            
            if not primary_effects:
                primary_effects = ["traditional medicine"]
            
            # Create description
            description = f"Herb from {herb.tradition}"
            if herb.traditional_uses:
                first_use = self._truncate_at_word_boundary(herb.traditional_uses[0], 100)
                description = f"Used in {herb.tradition} for {first_use}"
            
            # Escape description
            description = self._escape_string(self._truncate_at_word_boundary(description, 150))
            
            code_lines.extend([
                "self._add_substance(Substance(",
                f"    name=\"{self._escape_string(herb.name)}\",",
                f"    category=\"herb\",",
                f"    common_names={common_names[:5]},",  # Limit to 5 names
                f"    primary_effects={primary_effects[:3]},",  # Limit to 3 effects
                f"    description=\"{description}\"",
                "))",
                "",
            ])
        
        return "\n".join(code_lines)


def main():
    """Main entry point for the PDF processor"""
    parser = argparse.ArgumentParser(
        description="Extract herbal medicine data from PDF documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all PDFs in current directory
  python pdf_processor.py
  
  # Process PDFs in specific directory with custom output
  python pdf_processor.py --directory ./docs --output herbs_data.json
  
  # Generate Python code for integration
  python pdf_processor.py --generate-code
        """
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Directory containing PDF files (default: current directory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='extracted_herbs.json',
        help='Output JSON file path (default: extracted_herbs.json)'
    )
    
    parser.add_argument(
        '-g', '--generate-code',
        action='store_true',
        help='Generate Python code for apothecary.py integration'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if any PDF processing library is available
    if not (HAS_PDFPLUMBER or HAS_PYPDF2 or HAS_OCR):
        logger.error("No PDF processing libraries available!")
        logger.error("Please install at least one of: pdfplumber, PyPDF2, or pytesseract+pdf2image")
        logger.error("Run: pip install pdfplumber PyPDF2")
        sys.exit(1)
    
    # Initialize processor
    processor = PDFProcessor()
    
    # Process PDFs
    logger.info(f"Processing PDFs in: {args.directory}")
    herbs = processor.process_directory(args.directory)
    
    if not herbs:
        logger.warning("No herbs extracted from PDFs")
        sys.exit(0)
    
    # Export to JSON
    processor.export_to_json(args.output)
    print(f"\n✓ Exported {len(herbs)} herbs to {args.output}")
    
    # Generate Python code if requested
    if args.generate_code:
        code = processor.generate_python_code()
        code_file = "apothecary_generated_code.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"✓ Generated Python code saved to {code_file}")
        print("\nTo integrate into apothecary.py:")
        print("1. Open apothecary_generated_code.py")
        print("2. Copy the substance definitions")
        print("3. Add them to the _initialize_database() method in apothecary.py")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total herbs extracted: {len(herbs)}")
    
    # Group by tradition
    traditions = defaultdict(int)
    for herb in herbs.values():
        traditions[herb.tradition] += 1
    
    print(f"\nBy tradition:")
    for tradition, count in sorted(traditions.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tradition}: {count}")
    
    print("\n✓ Processing complete!")


if __name__ == "__main__":
    main()
