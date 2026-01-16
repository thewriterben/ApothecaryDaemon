# PDF Processor Module Documentation

## Overview

The PDF Processor module provides comprehensive herb recognition and extraction capabilities for herbal medicine literature across three major traditions:
- **Western Herbal Medicine** (58 herbs)
- **Ayurvedic Medicine** (32 herbs with Sanskrit names)
- **Traditional Chinese Medicine (TCM)** (39 herbs with Pinyin and Chinese characters)

Total: **120 unique herbs** (after cross-referencing between traditions).

## Features

### 1. Expanded Herb Recognition

The module includes three comprehensive herb dictionaries:

- **KNOWN_HERBS**: 58 Western herbs including Feverfew, Butterbur, Skullcap, Nettle, Holy Basil, and more
- **AYURVEDIC_HERBS**: 32 Ayurvedic herbs with Sanskrit names (Devanagari script)
- **TCM_HERBS**: 39 TCM herbs with Pinyin romanization and Chinese characters

### 2. Tradition-Specific Parsing

#### Ayurvedic Properties:
- **Doshas**: Vata, Pitta, Kapha balancing/aggravating effects
- **Rasa** (tastes): Madhura (sweet), Amla (sour), Lavana (salty), Katu (pungent), Tikta (bitter), Kashaya (astringent)
- **Virya** (potency): Ushna (heating), Shita (cooling)
- **Vipaka** (post-digestive effect): Madhura, Amla, Katu
- **Sanskrit names** in Devanagari script

#### TCM Properties:
- **Channels/Meridians**: Liver, Heart, Spleen, Lung, Kidney, etc.
- **Temperature**: Hot (热), Warm (温), Neutral (平), Cool (凉), Cold (寒)
- **Taste**: Pungent (辛), Sweet (甘), Sour (酸), Bitter (苦), Salty (咸)
- **Actions**: Tonify Qi/Blood/Yin/Yang, Clear Heat, Move Blood, etc.
- **Pinyin names** with tone marks and **Chinese characters**

### 3. Data Classes

#### ExtractedHerb
Comprehensive dataclass for storing extracted herb information:

```python
@dataclass
class ExtractedHerb:
    name: str
    scientific_name: Optional[str]
    common_names: List[str]
    traditional_uses: List[str]
    preparation_methods: List[str]
    contraindications: List[str]
    interactions: List[str]
    source_document: str
    tradition: str
    
    # Ayurvedic properties
    sanskrit_name: Optional[str]
    doshas: Dict[str, str]
    rasa: List[str]
    virya: Optional[str]
    vipaka: Optional[str]
    
    # TCM properties
    pinyin_name: Optional[str]
    chinese_name: Optional[str]
    channels: List[str]
    tcm_temperature: Optional[str]
    tcm_taste: List[str]
    tcm_actions: List[str]
```

### 4. Parser Classes

#### AyurvedicParser
Specialized parser for Ayurvedic medical texts:
- Extracts dosha effects (balances/aggravates Vata/Pitta/Kapha)
- Parses Rasa (taste), Virya (potency), Vipaka (post-digestive effect)
- Recognizes Sanskrit terminology and transliterations
- Identifies Ayurvedic formulas (Triphala, Trikatu, etc.)

#### TCMParser
Specialized parser for Traditional Chinese Medicine texts:
- Extracts channel/meridian affiliations
- Parses temperature and taste properties
- Identifies TCM actions (tonify, clear, move, transform)
- Recognizes Pinyin names with tone marks
- Matches Chinese characters

### 5. Main PDFProcessor Class

Central processing class that:
- Merges all herb dictionaries with intelligent cross-referencing
- Extracts herbs from text with tradition-specific properties
- Exports data to JSON format
- Generates Python code for integration with apothecary.py
- Provides statistics on the herb database

## Usage Examples

### Basic Usage

```python
from pdf_processor import PDFProcessor

# Initialize processor
processor = PDFProcessor()

# Get statistics
stats = processor.get_herb_statistics()
print(f"Total herbs: {stats['total_herbs']}")
print(f"Western: {stats['western_herbs']}")
print(f"Ayurvedic: {stats['ayurvedic_herbs']}")
print(f"TCM: {stats['tcm_herbs']}")
```

### Extract Herbs from Text

```python
# Sample text with herbs from multiple traditions
text = """
Ashwagandha (Withania somnifera) balances Vata and Kapha doshas.
Rasa: bitter, astringent, sweet. Virya: heating (Ushna).

Huang Qi (Astragalus) tonifies Qi and strengthens immunity.
Enters the Spleen and Lung channels. Temperature: Warm.
"""

# Extract herbs
herbs = processor.extract_herbs_from_text(text, source_doc="sample.pdf")

# Display results
for herb in herbs:
    print(f"\n{herb.name} ({herb.tradition})")
    if herb.sanskrit_name:
        print(f"  Sanskrit: {herb.sanskrit_name}")
    if herb.doshas:
        print(f"  Doshas: {herb.doshas}")
    if herb.pinyin_name:
        print(f"  Pinyin: {herb.pinyin_name}")
    if herb.channels:
        print(f"  Channels: {herb.channels}")
```

### Export to JSON

```python
# Export extracted herbs to JSON
processor.export_to_json(herbs, "extracted_herbs.json")
```

Output format:
```json
[
  {
    "name": "Ashwagandha",
    "scientific_name": "Withania somnifera",
    "tradition": "ayurvedic",
    "sanskrit_name": "अश्वगंधा",
    "doshas": {"vata": "pacifies", "kapha": "pacifies"},
    "rasa": ["Bitter", "Astringent", "Sweet"],
    "virya": "Ushna (heating)"
  }
]
```

### Generate Code for apothecary.py

```python
# Generate Python code for integration
code = processor.generate_apothecary_code(herbs)
print(code)
```

Output:
```python
# Generated herb definitions for ApothecaryDaemon
# This code can be integrated into apothecary.py

# Add these substances to the database:

self._add_substance(Substance(
    name="Ashwagandha",
    category="herb",
    common_names=["ashwagandha", "winter cherry", "indian ginseng"],
    primary_effects=[],  # TODO: Add effects
    description="Ashwagandha (Withania somnifera) - Ayurvedic herb"
))
```

## Pattern Matching

### Ayurvedic Patterns

The module includes regex patterns for:
- `Dosha[s]?: ...` - Dosha information
- `Rasa[s]?: ...` - Taste information
- `Virya: ...` - Potency information
- `Vipaka: ...` - Post-digestive effect
- `Balances/Pacifies (Vata|Pitta|Kapha)` - Dosha balancing
- `Aggravates (Vata|Pitta|Kapha)` - Dosha aggravation

### TCM Patterns

The module includes regex patterns for:
- `Channel[s]/Meridian[s]: ...` - Channel affiliations
- `Temperature: ...` - Temperature property
- `Taste[s]: ...` - Taste properties
- `Action[s]: ...` - TCM actions
- `Tonifies (Qi|Blood|Yin|Yang|Organ)` - Tonifying actions
- `Clears (Heat|Damp|Phlegm|Wind)` - Clearing actions
- `Moves (Qi|Blood)` - Moving actions
- `Enters the (Liver|Heart|Spleen|Lung|Kidney)` - Channel entry

## Cross-Referencing

The processor intelligently merges herbs that appear in multiple traditions:

- **Ginseng** (Panax ginseng): Western + TCM (Ren Shen 人参)
- **Astragalus** (Astragalus membranaceus): Western + TCM (Huang Qi 黄芪)
- **Licorice** (Glycyrrhiza): Western + TCM (Gan Cao 甘草)
- **Holy Basil/Tulsi** (Ocimum tenuiflorum): Western + Ayurvedic (तुलसी)

Herbs appearing in multiple traditions are marked with `tradition: "mixed"` and include properties from all relevant traditions.

## Testing

Comprehensive test suite included in `test_pdf_processor.py`:

```bash
python3 test_pdf_processor.py
```

Test coverage includes:
- Herb dictionary completeness (count, structure, specific herbs)
- ExtractedHerb dataclass functionality
- Ayurvedic parser (doshas, rasa, virya, vipaka)
- TCM parser (channels, temperature, taste, actions)
- PDF processor (extraction, merging, export, code generation)
- Pattern matching validation

## Requirements

Add to `requirements.txt`:
```
PyPDF2>=3.0.0  # For PDF text extraction
pdfplumber>=0.10.0  # Alternative PDF processing
```

## Statistics

Current herb database statistics:
- **Total herbs**: 120 (after merging and cross-referencing)
- **Western herbs**: 58 (in KNOWN_HERBS dictionary)
- **Ayurvedic herbs**: 32 (in AYURVEDIC_HERBS dictionary)
- **TCM herbs**: 39 (in TCM_HERBS dictionary)
- **Mixed tradition herbs**: 8 (cross-referenced across traditions)

## Future Enhancements

Potential additions:
1. Actual PDF file reading integration (PyPDF2/pdfplumber)
2. OCR support for scanned documents
3. More classical formulas (Si Wu Tang, Chyawanprash, etc.)
4. Additional herb properties (dosage, preparation methods)
5. Interaction checking integration with apothecary.py
6. Multi-language support for herb names
7. Database backend for larger collections
8. Web API for herb lookup and extraction

## Example: Running the Module

```bash
# Display statistics and test extraction
python3 pdf_processor.py
```

Output:
```
PDF Processor - Herb Recognition Module
==================================================
Total herbs in database: 120
Western herbs: 54
Ayurvedic herbs: 31
TCM herbs: 27
Mixed tradition herbs: 8
==================================================

Extracted 2 herbs from sample text:
  - Astragalus (mixed)
    Doshas: {'vata': 'pacifies'}
    Channels: ['Spleen', 'Lung']
  - Ashwagandha (ayurvedic)
    Sanskrit: अश्वगंधा
    Doshas: {'vata': 'pacifies'}
```

## License

Same as ApothecaryDaemon project license.

## Contributing

When adding new herbs:
1. Use proper scientific names (binomial nomenclature)
2. Include all common names and alternate spellings
3. Add Sanskrit names (Devanagari) for Ayurvedic herbs
4. Add Pinyin (with tones) and Chinese characters for TCM herbs
5. Verify tradition assignment
6. Run test suite to ensure no regressions
