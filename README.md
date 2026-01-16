# ApothecaryDaemon

Interactive herbal treatment safety and effectiveness reference

## Overview

ApothecaryDaemon is a command-line application designed to check for interactions between herbal supplements, over-the-counter medications, and prescription drugs. This tool helps individuals ensure their safety and achieve desired effects when combining different substances.

**⚠️ IMPORTANT DISCLAIMER**: This application is for informational purposes only and is NOT intended to replace professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider before starting, stopping, or combining any supplements or medications.

## Features

- **Interaction Checking**: Identifies potential interactions between multiple substances
- **Severity Ratings**: Classifies interactions from minor to severe
- **Effect Warnings**: Alerts users to unexpected effects (e.g., hallucinations, hyperactivity, anxiety)
- **Two Modes**: Interactive mode for step-by-step guidance or batch mode for quick checks
- **Comprehensive Database**: Includes common herbs, supplements, and medications
- **PDF Processing**: Extract herbal medicine data from PDF documents to expand the database

## Installation

### Requirements

- Python 3.7 or higher
- No external dependencies required (uses Python standard library only)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/thewriterben/ApothecaryDaemon.git
cd ApothecaryDaemon
```

2. Make the script executable (optional):
```bash
chmod +x apothecary.py
```

## Usage

### Interactive Mode

Run the application without arguments to enter interactive mode:

```bash
python3 apothecary.py
```

The interactive mode will guide you through:
1. Entering substances one at a time
2. Viewing information about each substance
3. Checking for interactions between all entered substances
4. Receiving detailed warnings about any found interactions

**Example Interactive Session:**
```
$ python3 apothecary.py

======================================================================
ApothecaryDaemon - Herbal Supplement & Medication Interaction Checker
======================================================================

⚠️  WARNING: This tool is for informational purposes only!
   This is NOT a replacement for professional medical advice.
   ...

Enter substances to check (herbs, supplements, medications).
Type 'done' when finished, 'list' to see available substances, or 'quit' to exit.

Enter substance #1 (or command): valerian root

📋 Valerian Root
   Category: HERB
   Description: Herbal supplement commonly used for relaxation and sleep
   Primary Effects: relaxation, sedation, sleep aid

✓ Added Valerian Root

Enter substance #2 (or command): benadryl

📋 Diphenhydramine
   Category: OTC
   Description: Common over-the-counter antihistamine and sleep aid
   Primary Effects: antihistamine, sedation

✓ Added Diphenhydramine

Enter substance #3 (or command): done

======================================================================
CHECKING FOR INTERACTIONS...
======================================================================

⚠️  Found 1 interaction(s):

⚠️  MODERATE INTERACTION
   Between: Valerian Root + Diphenhydramine
   Effects: excessive drowsiness, sedation
   Details: Combining sedative herbs with antihistamines can cause excessive drowsiness
   ➜ Avoid driving or operating machinery. Consider reducing doses or timing separately.
```

### Batch Mode

Check specific substances by passing them as command-line arguments:

```bash
python3 apothecary.py "st johns wort" "ssri"
```

```bash
python3 apothecary.py "ginkgo biloba" "warfarin" "aspirin"
```

### Available Commands (Interactive Mode)

- `list` - Display all substances in the database
- `done` - Finish entering substances and check for interactions
- `quit` - Exit the application

## PDF Processing Module

ApothecaryDaemon includes a powerful PDF processing module that can extract herbal medicine data from PDF documents. This allows you to automatically build and expand the substance database from reference materials.

### Installation

The PDF processing module requires additional dependencies:

```bash
# Install PDF processing dependencies
pip install -r requirements.txt
```

**For OCR support (scanned PDFs)**, you'll also need system dependencies:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
- Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Download and install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases

### Features

The PDF processor can:
- Extract text from multiple PDF formats (text-based and scanned)
- Automatically detect medical traditions (Ayurveda, TCM, Western, African, Latin American, etc.)
- Identify known herbs and their scientific names
- Extract traditional uses, contraindications, and drug interactions
- Export data to JSON format
- Generate Python code for integration into `apothecary.py`
- Handle missing dependencies gracefully

### Usage

#### Basic Usage

Process all PDFs in the current directory:

```bash
python pdf_processor.py
```

This will:
1. Scan for all `.pdf` files in the current directory
2. Extract text using available methods (pdfplumber → PyPDF2 → OCR)
3. Identify known herbs and extract their information
4. Export results to `extracted_herbs.json`

#### Process Specific Directory

```bash
python pdf_processor.py --directory ./docs
```

#### Custom Output File

```bash
python pdf_processor.py --output my_herbs.json
```

#### Generate Python Code

Generate code that can be integrated into `apothecary.py`:

```bash
python pdf_processor.py --generate-code
```

This creates `apothecary_generated_code.py` with substance definitions ready to add to the database.

#### Verbose Output

```bash
python pdf_processor.py --verbose
```

### Command Line Options

- `-d`, `--directory` - Directory containing PDF files (default: current directory)
- `-o`, `--output` - Output JSON file path (default: `extracted_herbs.json`)
- `-g`, `--generate-code` - Generate Python code for apothecary.py integration
- `-v`, `--verbose` - Enable verbose logging

### Example Output

```
Processing PDFs in: /path/to/pdfs
Available PDF libraries: pdfplumber, PyPDF2
Found 23 PDF files to process

Processing: Ayurveda_EDL_list_final.pdf
Detected tradition: Ayurveda
Found 15 herbs in Ayurveda_EDL_list_final.pdf

Processing: Traditional_Chinese_Medicine_08-03-2015.pdf
Detected tradition: Traditional Chinese Medicine
Found 12 herbs in Traditional_Chinese_Medicine_08-03-2015.pdf

...

Total unique herbs extracted: 45

✓ Exported 45 herbs to extracted_herbs.json

Summary:
  Total herbs extracted: 45

By tradition:
  Ayurveda: 18
  Traditional Chinese Medicine: 12
  Mediterranean/European: 8
  Latin American: 4
  African: 3

✓ Processing complete!
```

### Supported Medical Traditions

The processor automatically detects medical traditions from filenames:

- **Ayurveda**: Files containing "ayurved" or "ayurvedic"
- **Traditional Chinese Medicine (TCM)**: Files with "tcm" or "chinese"
- **Mediterranean/European**: Files with "mediterranean" or "european"
- **African**: Files with "african"
- **Latin American**: Files with "latin", "mexican", "dominican", or "south america"
- **Native American**: Files with "native american"
- **General**: Files that don't match any specific tradition

### Known Herbs Database

The processor includes a built-in dictionary of 30+ known herbs with their scientific names, including:

- St. John's Wort (Hypericum perforatum)
- Valerian (Valeriana officinalis)
- Ginkgo Biloba (Ginkgo biloba)
- Turmeric (Curcuma longa)
- Ashwagandha (Withania somnifera)
- Ginseng (Panax ginseng)
- And many more...

### Integration with ApothecaryDaemon

To integrate extracted herbs into the main application:

1. Run the PDF processor with code generation:
   ```bash
   python pdf_processor.py --generate-code
   ```

2. Open the generated `apothecary_generated_code.py` file

3. Copy the substance definitions

4. Add them to the `_initialize_database()` method in `apothecary.py`

5. Optionally, add interaction data for the new herbs

### Troubleshooting

**No text extracted from PDFs:**
- Try installing all PDF libraries: `pip install pdfplumber PyPDF2 pytesseract pdf2image Pillow`
- For scanned PDFs, ensure Tesseract OCR is installed system-wide
- Use `--verbose` flag to see detailed error messages

**OCR not working:**
- Verify Tesseract is installed: `tesseract --version`
- Verify Poppler is installed (for pdf2image)
- Check that the PDF contains actual scanned images

**Import errors:**
- The module will work with just PyPDF2 or pdfplumber
- OCR libraries are optional and only needed for scanned PDFs
- Install dependencies: `pip install -r requirements.txt`

## Interaction Severity Levels

- **🚨 SEVERE**: Life-threatening interactions requiring immediate medical attention
- **⛔ MAJOR**: Serious interactions that should be avoided without medical supervision
- **⚠️  MODERATE**: Significant interactions requiring caution and possible dose adjustment
- **ℹ️  MINOR**: Low-risk interactions that generally require only monitoring

## Included Substances

### Herbal Supplements
- St. John's Wort (mood elevation, antidepressant)
- Valerian Root (relaxation, sleep aid)
- Kava (anxiety relief)
- Ginseng (energy, stimulation)
- Chamomile (relaxation, digestive aid)
- Ginkgo Biloba (cognitive enhancement, circulation)
- Passionflower (anxiety relief, sleep aid)

### Prescription Medications
- Warfarin (blood thinner)
- SSRIs (antidepressants)
- Benzodiazepines (anti-anxiety, sedative)

### Over-the-Counter Medications
- Ibuprofen (pain relief, anti-inflammatory)
- Aspirin (pain relief, blood thinner)
- Diphenhydramine/Benadryl (antihistamine, sleep aid)

## Example Interactions

### Severe Interactions
- **St. John's Wort + SSRIs**: Risk of serotonin syndrome (confusion, agitation, rapid heart rate)

### Major Interactions
- **Valerian Root + Benzodiazepines**: Excessive sedation and impaired coordination
- **Ginkgo Biloba + Warfarin**: Increased bleeding risk
- **Kava + Benzodiazepines**: Excessive sedation and liver damage risk

### Moderate Interactions
- **Valerian Root + Diphenhydramine**: Excessive drowsiness
- **Ginkgo Biloba + Aspirin**: Increased bleeding risk
- **Passionflower + Benzodiazepines**: Excessive sedation

## Safety Guidelines

1. **Always Consult Healthcare Providers**: Before combining any substances
2. **Start Low, Go Slow**: When introducing new supplements
3. **Monitor for Effects**: Watch for unexpected symptoms
4. **Keep Records**: Track all substances you're taking
5. **Report Issues**: Inform your healthcare provider of any adverse effects
6. **Database Limitations**: This database is not exhaustive; absence of a listed interaction does not guarantee safety

## Common Unexpected Effects to Watch For

The application specifically helps prevent unwanted effects such as:
- Hallucinations
- Hyperactivity when expecting relaxation
- Anxiety or agitation
- Depression
- Euphoria
- Excessive sedation
- Bleeding risks
- Liver damage
- Serotonin syndrome

## Development

### Project Structure
```
ApothecaryDaemon/
├── apothecary.py       # Main application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── LICENSE            # License information
```

### Contributing

Contributions are welcome! Please ensure that:
- All added interactions are backed by scientific evidence
- Source citations are included for medical claims
- Code follows Python best practices
- User safety remains the top priority

### Future Enhancements
- Expanded substance database
- Integration with drug interaction APIs
- Export interaction reports
- Multi-language support
- Web interface
- Mobile app

## License

See LICENSE file for details.

## Medical Disclaimer

This software is provided "as is" without warranty of any kind. The creators and contributors are not responsible for any decisions made based on information from this application. This tool is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified health providers with any questions regarding medical conditions or medications.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Remember**: Your health and safety are paramount. When in doubt, consult a healthcare professional.
