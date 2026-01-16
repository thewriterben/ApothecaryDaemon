#!/usr/bin/env python3
"""
PDF Processor Module for Herbal Medicine Recognition

This module provides comprehensive herb recognition and extraction capabilities
for Western, Ayurvedic, and Traditional Chinese Medicine (TCM) traditions.
"""

import re
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set
from enum import Enum


class MedicineTradition(Enum):
    """Medical tradition categories"""
    WESTERN = "western"
    AYURVEDIC = "ayurvedic"
    TCM = "tcm"
    MIXED = "mixed"
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

    """Represents an herb extracted from a document with tradition-specific properties"""
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
    
    # Ayurvedic properties
    sanskrit_name: Optional[str] = None
    doshas: Dict[str, str] = field(default_factory=dict)  # {'vata': 'pacifies', 'pitta': 'aggravates', etc.}
    rasa: List[str] = field(default_factory=list)  # tastes
    virya: Optional[str] = None  # potency
    vipaka: Optional[str] = None  # post-digestive effect
    
    # TCM properties
    pinyin_name: Optional[str] = None
    chinese_name: Optional[str] = None
    channels: List[str] = field(default_factory=list)  # meridians entered
    tcm_temperature: Optional[str] = None
    tcm_taste: List[str] = field(default_factory=list)
    tcm_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return asdict(self)


# ============================================================================
# KNOWN_HERBS - Western Herbal Medicine (100+ herbs)
# ============================================================================

KNOWN_HERBS = {
    # Original herbs
    "St. John's Wort": {
        "scientific_name": "Hypericum perforatum",
        "common_names": ["St Johns Wort", "Hypericum", "Klamath Weed"],
        "tradition": "western"
    },
    "Valerian Root": {
        "scientific_name": "Valeriana officinalis",
        "common_names": ["Valerian", "Garden Heliotrope"],
        "tradition": "western"
    },
    "Kava": {
        "scientific_name": "Piper methysticum",
        "common_names": ["Kava Kava", "Awa"],
        "tradition": "western"
    },
    "Ginseng": {
        "scientific_name": "Panax ginseng",
        "common_names": ["Asian Ginseng", "Korean Ginseng", "Ren Shen"],
        "tradition": "western"
    },
    "Chamomile": {
        "scientific_name": "Matricaria chamomilla",
        "common_names": ["German Chamomile", "Blue Chamomile"],
        "tradition": "western"
    },
    "Ginkgo Biloba": {
        "scientific_name": "Ginkgo biloba",
        "common_names": ["Ginkgo", "Maidenhair Tree"],
        "tradition": "western"
    },
    "Passionflower": {
        "scientific_name": "Passiflora incarnata",
        "common_names": ["Passiflora", "Maypop"],
        "tradition": "western"
    },
    
    # Expanded Western herbs
    "Feverfew": {
        "scientific_name": "Tanacetum parthenium",
        "common_names": ["Featherfew", "Bachelor's Buttons"],
        "tradition": "western"
    },
    "Butterbur": {
        "scientific_name": "Petasites hybridus",
        "common_names": ["Petasites", "Bog Rhubarb"],
        "tradition": "western"
    },
    "Skullcap": {
        "scientific_name": "Scutellaria lateriflora",
        "common_names": ["American Skullcap", "Blue Skullcap"],
        "tradition": "western"
    },
    "Lemon Balm": {
        "scientific_name": "Melissa officinalis",
        "common_names": ["Melissa", "Balm"],
        "tradition": "western"
    },
    "Hops": {
        "scientific_name": "Humulus lupulus",
        "common_names": ["Common Hops"],
        "tradition": "western"
    },
    "Wild Yam": {
        "scientific_name": "Dioscorea villosa",
        "common_names": ["Colic Root", "Devil's Bones"],
        "tradition": "western"
    },
    "Dong Quai": {
        "scientific_name": "Angelica sinensis",
        "common_names": ["Female Ginseng", "Dang Gui"],
        "tradition": "western"
    },
    "Evening Primrose": {
        "scientific_name": "Oenothera biennis",
        "common_names": ["Evening Star", "Sun Drop"],
        "tradition": "western"
    },
    "Boswellia": {
        "scientific_name": "Boswellia serrata",
        "common_names": ["Indian Frankincense", "Salai Guggal"],
        "tradition": "western"
    },
    "Devil's Claw": {
        "scientific_name": "Harpagophytum procumbens",
        "common_names": ["Grapple Plant", "Wood Spider"],
        "tradition": "western"
    },
    "Cat's Claw": {
        "scientific_name": "Uncaria tomentosa",
        "common_names": ["Una de Gato", "Cats Claw"],
        "tradition": "western"
    },
    "Rhodiola": {
        "scientific_name": "Rhodiola rosea",
        "common_names": ["Golden Root", "Arctic Root"],
        "tradition": "western"
    },
    "Schisandra": {
        "scientific_name": "Schisandra chinensis",
        "common_names": ["Five Flavor Berry", "Wu Wei Zi"],
        "tradition": "western"
    },
    "Astragalus": {
        "scientific_name": "Astragalus membranaceus",
        "common_names": ["Huang Qi", "Milk Vetch"],
        "tradition": "western"
    },
    "Eleuthero": {
        "scientific_name": "Eleutherococcus senticosus",
        "common_names": ["Siberian Ginseng", "Ci Wu Jia"],
        "tradition": "western"
    },
    "Maca": {
        "scientific_name": "Lepidium meyenii",
        "common_names": ["Peruvian Ginseng", "Maca Root"],
        "tradition": "western"
    },
    "Tribulus": {
        "scientific_name": "Tribulus terrestris",
        "common_names": ["Puncture Vine", "Gokshura"],
        "tradition": "western"
    },
    "Fenugreek": {
        "scientific_name": "Trigonella foenum-graecum",
        "common_names": ["Greek Hay", "Methi"],
        "tradition": "western"
    },
    "Gymnema": {
        "scientific_name": "Gymnema sylvestre",
        "common_names": ["Gurmar", "Sugar Destroyer"],
        "tradition": "western"
    },
    "Bitter Melon": {
        "scientific_name": "Momordica charantia",
        "common_names": ["Bitter Gourd", "Karela"],
        "tradition": "western"
    },
    "Berberine": {
        "scientific_name": "Berberis vulgaris",
        "common_names": ["Barberry", "European Barberry"],
        "tradition": "western"
    },
    "Goldenseal": {
        "scientific_name": "Hydrastis canadensis",
        "common_names": ["Orange Root", "Yellow Puccoon"],
        "tradition": "western"
    },
    "Oregon Grape": {
        "scientific_name": "Mahonia aquifolium",
        "common_names": ["Mountain Grape", "Holly Grape"],
        "tradition": "western"
    },
    "Uva Ursi": {
        "scientific_name": "Arctostaphylos uva-ursi",
        "common_names": ["Bearberry", "Kinnikinnick"],
        "tradition": "western"
    },
    "Cranberry": {
        "scientific_name": "Vaccinium macrocarpon",
        "common_names": ["American Cranberry", "Large Cranberry"],
        "tradition": "western"
    },
    "Nettle": {
        "scientific_name": "Urtica dioica",
        "common_names": ["Stinging Nettle", "Common Nettle"],
        "tradition": "western"
    },
    "Dandelion": {
        "scientific_name": "Taraxacum officinale",
        "common_names": ["Lion's Tooth", "Blowball"],
        "tradition": "western"
    },
    "Burdock": {
        "scientific_name": "Arctium lappa",
        "common_names": ["Greater Burdock", "Gobo"],
        "tradition": "western"
    },
    "Yellow Dock": {
        "scientific_name": "Rumex crispus",
        "common_names": ["Curled Dock", "Curly Dock"],
        "tradition": "western"
    },
    "Red Clover": {
        "scientific_name": "Trifolium pratense",
        "common_names": ["Purple Clover", "Meadow Clover"],
        "tradition": "western"
    },
    "Vitex": {
        "scientific_name": "Vitex agnus-castus",
        "common_names": ["Chaste Tree", "Monk's Pepper"],
        "tradition": "western"
    },
    "Motherwort": {
        "scientific_name": "Leonurus cardiaca",
        "common_names": ["Lion's Tail", "Throw-wort"],
        "tradition": "western"
    },
    "Yarrow": {
        "scientific_name": "Achillea millefolium",
        "common_names": ["Common Yarrow", "Nosebleed Plant"],
        "tradition": "western"
    },
    "Calendula": {
        "scientific_name": "Calendula officinalis",
        "common_names": ["Pot Marigold", "Garden Marigold"],
        "tradition": "western"
    },
    "Arnica": {
        "scientific_name": "Arnica montana",
        "common_names": ["Mountain Arnica", "Wolf's Bane"],
        "tradition": "western"
    },
    "Comfrey": {
        "scientific_name": "Symphytum officinale",
        "common_names": ["Knitbone", "Boneset"],
        "tradition": "western"
    },
    "Plantain": {
        "scientific_name": "Plantago major",
        "common_names": ["Broadleaf Plantain", "Greater Plantain"],
        "tradition": "western"
    },
    "Slippery Elm": {
        "scientific_name": "Ulmus rubra",
        "common_names": ["Red Elm", "Indian Elm"],
        "tradition": "western"
    },
    "Marshmallow": {
        "scientific_name": "Althaea officinalis",
        "common_names": ["Marsh Mallow", "White Mallow"],
        "tradition": "western"
    },
    "Licorice": {
        "scientific_name": "Glycyrrhiza glabra",
        "common_names": ["Sweet Root", "Gan Cao"],
        "tradition": "western"
    },
    "Fennel": {
        "scientific_name": "Foeniculum vulgare",
        "common_names": ["Sweet Fennel", "Florence Fennel"],
        "tradition": "western"
    },
    "Caraway": {
        "scientific_name": "Carum carvi",
        "common_names": ["Meridian Fennel", "Persian Cumin"],
        "tradition": "western"
    },
    "Anise": {
        "scientific_name": "Pimpinella anisum",
        "common_names": ["Aniseed", "Sweet Cumin"],
        "tradition": "western"
    },
    "Cardamom": {
        "scientific_name": "Elettaria cardamomum",
        "common_names": ["Green Cardamom", "True Cardamom"],
        "tradition": "western"
    },
    "Cinnamon": {
        "scientific_name": "Cinnamomum verum",
        "common_names": ["True Cinnamon", "Ceylon Cinnamon"],
        "tradition": "western"
    },
    "Clove": {
        "scientific_name": "Syzygium aromaticum",
        "common_names": ["Cloves", "Lavang"],
        "tradition": "western"
    },
    "Oregano": {
        "scientific_name": "Origanum vulgare",
        "common_names": ["Wild Marjoram", "Common Oregano"],
        "tradition": "western"
    },
    "Thyme": {
        "scientific_name": "Thymus vulgaris",
        "common_names": ["Common Thyme", "Garden Thyme"],
        "tradition": "western"
    },
    "Rosemary": {
        "scientific_name": "Rosmarinus officinalis",
        "common_names": ["Compass Plant", "Polar Plant"],
        "tradition": "western"
    },
    "Sage": {
        "scientific_name": "Salvia officinalis",
        "common_names": ["Common Sage", "Garden Sage"],
        "tradition": "western"
    },
    "Holy Basil": {
        "scientific_name": "Ocimum tenuiflorum",
        "common_names": ["Tulsi", "Sacred Basil"],
        "tradition": "western"
    },
}


# ============================================================================
# AYURVEDIC_HERBS - Ayurvedic Medicine (30+ herbs)
# ============================================================================

AYURVEDIC_HERBS = {
    "Ashwagandha": {
        "scientific_name": "Withania somnifera",
        "sanskrit_name": "अश्वगंधा",
        "common_names": ["Indian Ginseng", "Winter Cherry"],
        "tradition": "ayurvedic"
    },
    "Tulsi": {
        "scientific_name": "Ocimum tenuiflorum",
        "sanskrit_name": "तुलसी",
        "common_names": ["Holy Basil", "Sacred Basil"],
        "tradition": "ayurvedic"
    },
    "Brahmi": {
        "scientific_name": "Bacopa monnieri",
        "sanskrit_name": "ब्राह्मी",
        "common_names": ["Water Hyssop", "Bacopa"],
        "tradition": "ayurvedic"
    },
    "Shatavari": {
        "scientific_name": "Asparagus racemosus",
        "sanskrit_name": "शतावरी",
        "common_names": ["Wild Asparagus", "Satavari"],
        "tradition": "ayurvedic"
    },
    "Triphala": {
        "scientific_name": "Combination formula",
        "sanskrit_name": "त्रिफला",
        "common_names": ["Three Fruits"],
        "tradition": "ayurvedic"
    },
    "Amalaki": {
        "scientific_name": "Phyllanthus emblica",
        "sanskrit_name": "आमलकी",
        "common_names": ["Amla", "Indian Gooseberry"],
        "tradition": "ayurvedic"
    },
    "Haritaki": {
        "scientific_name": "Terminalia chebula",
        "sanskrit_name": "हरीतकी",
        "common_names": ["Chebulic Myrobalan", "Black Myrobalan"],
        "tradition": "ayurvedic"
    },
    "Bibhitaki": {
        "scientific_name": "Terminalia bellirica",
        "sanskrit_name": "बिभीतकी",
        "common_names": ["Bahera", "Beleric Myrobalan"],
        "tradition": "ayurvedic"
    },
    "Guduchi": {
        "scientific_name": "Tinospora cordifolia",
        "sanskrit_name": "गुडूची",
        "common_names": ["Giloy", "Heart-leaved Moonseed"],
        "tradition": "ayurvedic"
    },
    "Neem": {
        "scientific_name": "Azadirachta indica",
        "sanskrit_name": "निम्ब",
        "common_names": ["Indian Lilac", "Margosa"],
        "tradition": "ayurvedic"
    },
    "Turmeric": {
        "scientific_name": "Curcuma longa",
        "sanskrit_name": "हरिद्रा",
        "common_names": ["Haridra", "Indian Saffron"],
        "tradition": "ayurvedic"
    },
    "Ginger": {
        "scientific_name": "Zingiber officinale",
        "sanskrit_name": "शुण्ठी",
        "common_names": ["Shunti", "Adrak"],
        "tradition": "ayurvedic"
    },
    "Black Pepper": {
        "scientific_name": "Piper nigrum",
        "sanskrit_name": "मरिच",
        "common_names": ["Maricha", "Kali Mirch"],
        "tradition": "ayurvedic"
    },
    "Long Pepper": {
        "scientific_name": "Piper longum",
        "sanskrit_name": "पिप्पली",
        "common_names": ["Pippali", "Indian Long Pepper"],
        "tradition": "ayurvedic"
    },
    "Trikatu": {
        "scientific_name": "Combination formula",
        "sanskrit_name": "त्रिकटु",
        "common_names": ["Three Pungents", "Three Spices"],
        "tradition": "ayurvedic"
    },
    "Guggulu": {
        "scientific_name": "Commiphora mukul",
        "sanskrit_name": "गुग्गुलु",
        "common_names": ["Indian Bdellium", "Guggul"],
        "tradition": "ayurvedic"
    },
    "Shilajit": {
        "scientific_name": "Mineral pitch",
        "sanskrit_name": "शिलाजीत",
        "common_names": ["Mineral Pitch", "Asphaltum"],
        "tradition": "ayurvedic"
    },
    "Arjuna": {
        "scientific_name": "Terminalia arjuna",
        "sanskrit_name": "अर्जुन",
        "common_names": ["Arjun", "White Marudah"],
        "tradition": "ayurvedic"
    },
    "Punarnava": {
        "scientific_name": "Boerhavia diffusa",
        "sanskrit_name": "पुनर्नवा",
        "common_names": ["Hogweed", "Red Spiderling"],
        "tradition": "ayurvedic"
    },
    "Bhringaraj": {
        "scientific_name": "Eclipta prostrata",
        "sanskrit_name": "भृङ्गराज",
        "common_names": ["False Daisy", "Eclipta"],
        "tradition": "ayurvedic"
    },
    "Shankhpushpi": {
        "scientific_name": "Convolvulus pluricaulis",
        "sanskrit_name": "शंखपुष्पी",
        "common_names": ["Morning Glory", "Speed Wheel"],
        "tradition": "ayurvedic"
    },
    "Jatamansi": {
        "scientific_name": "Nardostachys jatamansi",
        "sanskrit_name": "जटामांसी",
        "common_names": ["Spikenard", "Muskroot"],
        "tradition": "ayurvedic"
    },
    "Vacha": {
        "scientific_name": "Acorus calamus",
        "sanskrit_name": "वचा",
        "common_names": ["Calamus", "Sweet Flag"],
        "tradition": "ayurvedic"
    },
    "Kutki": {
        "scientific_name": "Picrorhiza kurroa",
        "sanskrit_name": "कुटकी",
        "common_names": ["Katuki", "Kutki"],
        "tradition": "ayurvedic"
    },
    "Chirata": {
        "scientific_name": "Swertia chirata",
        "sanskrit_name": "चिरायता",
        "common_names": ["Chirayata", "Indian Gentian"],
        "tradition": "ayurvedic"
    },
    "Vidanga": {
        "scientific_name": "Embelia ribes",
        "sanskrit_name": "विडङ्ग",
        "common_names": ["False Black Pepper", "Embelia"],
        "tradition": "ayurvedic"
    },
    "Bakuchi": {
        "scientific_name": "Psoralea corylifolia",
        "sanskrit_name": "बाकुची",
        "common_names": ["Babchi", "Scurfy Pea"],
        "tradition": "ayurvedic"
    },
    "Manjistha": {
        "scientific_name": "Rubia cordifolia",
        "sanskrit_name": "मञ्जिष्ठा",
        "common_names": ["Indian Madder", "Manjishtha"],
        "tradition": "ayurvedic"
    },
    "Sariva": {
        "scientific_name": "Hemidesmus indicus",
        "sanskrit_name": "सारिवा",
        "common_names": ["Indian Sarsaparilla", "Anantmool"],
        "tradition": "ayurvedic"
    },
    "Gokshura": {
        "scientific_name": "Tribulus terrestris",
        "sanskrit_name": "गोक्षुर",
        "common_names": ["Puncture Vine", "Gokhru"],
        "tradition": "ayurvedic"
    },
    "Kapikacchu": {
        "scientific_name": "Mucuna pruriens",
        "sanskrit_name": "कपिकच्छू",
        "common_names": ["Mucuna", "Velvet Bean", "Cowhage"],
        "tradition": "ayurvedic"
    },
    "Safed Musli": {
        "scientific_name": "Chlorophytum borivilianum",
        "sanskrit_name": "सफेद मुसली",
        "common_names": ["White Musli", "Musli"],
        "tradition": "ayurvedic"
    },
}


# ============================================================================
# TCM_HERBS - Traditional Chinese Medicine (40+ herbs)
# ============================================================================

TCM_HERBS = {
    "Ren Shen": {
        "scientific_name": "Panax ginseng",
        "pinyin_name": "Rén Shēn",
        "chinese_name": "人参",
        "common_names": ["Ginseng", "Asian Ginseng", "Korean Ginseng"],
        "tradition": "tcm"
    },
    "Huang Qi": {
        "scientific_name": "Astragalus membranaceus",
        "pinyin_name": "Huáng Qí",
        "chinese_name": "黄芪",
        "common_names": ["Astragalus", "Milk Vetch Root"],
        "tradition": "tcm"
    },
    "Gan Cao": {
        "scientific_name": "Glycyrrhiza uralensis",
        "pinyin_name": "Gān Cǎo",
        "chinese_name": "甘草",
        "common_names": ["Licorice", "Chinese Licorice"],
        "tradition": "tcm"
    },
    "Sheng Jiang": {
        "scientific_name": "Zingiber officinale",
        "pinyin_name": "Shēng Jiāng",
        "chinese_name": "生姜",
        "common_names": ["Fresh Ginger", "Ginger"],
        "tradition": "tcm"
    },
    "Gan Jiang": {
        "scientific_name": "Zingiber officinale",
        "pinyin_name": "Gān Jiāng",
        "chinese_name": "干姜",
        "common_names": ["Dried Ginger", "Dry Ginger"],
        "tradition": "tcm"
    },
    "Rou Gui": {
        "scientific_name": "Cinnamomum cassia",
        "pinyin_name": "Ròu Guì",
        "chinese_name": "肉桂",
        "common_names": ["Cinnamon Bark", "Cassia Bark"],
        "tradition": "tcm"
    },
    "Gui Zhi": {
        "scientific_name": "Cinnamomum cassia",
        "pinyin_name": "Guì Zhī",
        "chinese_name": "桂枝",
        "common_names": ["Cinnamon Twig", "Cassia Twig"],
        "tradition": "tcm"
    },
    "Bai Shao": {
        "scientific_name": "Paeonia lactiflora",
        "pinyin_name": "Bái Sháo",
        "chinese_name": "白芍",
        "common_names": ["White Peony Root", "Peony"],
        "tradition": "tcm"
    },
    "Chi Shao": {
        "scientific_name": "Paeonia lactiflora",
        "pinyin_name": "Chì Sháo",
        "chinese_name": "赤芍",
        "common_names": ["Red Peony Root", "Red Peony"],
        "tradition": "tcm"
    },
    "Di Huang": {
        "scientific_name": "Rehmannia glutinosa",
        "pinyin_name": "Dì Huáng",
        "chinese_name": "地黄",
        "common_names": ["Rehmannia", "Chinese Foxglove"],
        "tradition": "tcm"
    },
    "Shu Di Huang": {
        "scientific_name": "Rehmannia glutinosa",
        "pinyin_name": "Shú Dì Huáng",
        "chinese_name": "熟地黄",
        "common_names": ["Prepared Rehmannia", "Cooked Rehmannia"],
        "tradition": "tcm"
    },
    "Dang Gui": {
        "scientific_name": "Angelica sinensis",
        "pinyin_name": "Dāng Guī",
        "chinese_name": "当归",
        "common_names": ["Angelica", "Dong Quai", "Female Ginseng"],
        "tradition": "tcm"
    },
    "Chuan Xiong": {
        "scientific_name": "Ligusticum chuanxiong",
        "pinyin_name": "Chuān Xiōng",
        "chinese_name": "川芎",
        "common_names": ["Ligusticum", "Szechuan Lovage"],
        "tradition": "tcm"
    },
    "Bai Zhu": {
        "scientific_name": "Atractylodes macrocephala",
        "pinyin_name": "Bái Zhú",
        "chinese_name": "白术",
        "common_names": ["Atractylodes", "White Atractylodes"],
        "tradition": "tcm"
    },
    "Fu Ling": {
        "scientific_name": "Poria cocos",
        "pinyin_name": "Fú Líng",
        "chinese_name": "茯苓",
        "common_names": ["Poria", "Hoelen", "China Root"],
        "tradition": "tcm"
    },
    "Dang Shen": {
        "scientific_name": "Codonopsis pilosula",
        "pinyin_name": "Dǎng Shēn",
        "chinese_name": "党参",
        "common_names": ["Codonopsis", "Poor Man's Ginseng"],
        "tradition": "tcm"
    },
    "Wu Wei Zi": {
        "scientific_name": "Schisandra chinensis",
        "pinyin_name": "Wǔ Wèi Zǐ",
        "chinese_name": "五味子",
        "common_names": ["Schisandra", "Five Flavor Berry"],
        "tradition": "tcm"
    },
    "Mai Men Dong": {
        "scientific_name": "Ophiopogon japonicus",
        "pinyin_name": "Mài Mén Dōng",
        "chinese_name": "麦门冬",
        "common_names": ["Ophiopogon", "Dwarf Lilyturf"],
        "tradition": "tcm"
    },
    "Yu Zhu": {
        "scientific_name": "Polygonatum odoratum",
        "pinyin_name": "Yù Zhú",
        "chinese_name": "玉竹",
        "common_names": ["Polygonatum", "Solomon's Seal"],
        "tradition": "tcm"
    },
    "Gou Qi Zi": {
        "scientific_name": "Lycium barbarum",
        "pinyin_name": "Gǒu Qǐ Zǐ",
        "chinese_name": "枸杞子",
        "common_names": ["Lycium", "Goji Berry", "Wolfberry"],
        "tradition": "tcm"
    },
    "Ju Hua": {
        "scientific_name": "Chrysanthemum morifolium",
        "pinyin_name": "Jú Huā",
        "chinese_name": "菊花",
        "common_names": ["Chrysanthemum", "Florist's Daisy"],
        "tradition": "tcm"
    },
    "Jin Yin Hua": {
        "scientific_name": "Lonicera japonica",
        "pinyin_name": "Jīn Yín Huā",
        "chinese_name": "金银花",
        "common_names": ["Honeysuckle", "Japanese Honeysuckle"],
        "tradition": "tcm"
    },
    "Lian Qiao": {
        "scientific_name": "Forsythia suspensa",
        "pinyin_name": "Lián Qiào",
        "chinese_name": "连翘",
        "common_names": ["Forsythia", "Weeping Forsythia"],
        "tradition": "tcm"
    },
    "Huang Qin": {
        "scientific_name": "Scutellaria baicalensis",
        "pinyin_name": "Huáng Qín",
        "chinese_name": "黄芩",
        "common_names": ["Scutellaria", "Baikal Skullcap"],
        "tradition": "tcm"
    },
    "Huang Lian": {
        "scientific_name": "Coptis chinensis",
        "pinyin_name": "Huáng Lián",
        "chinese_name": "黄连",
        "common_names": ["Coptis", "Chinese Goldthread"],
        "tradition": "tcm"
    },
    "Huang Bai": {
        "scientific_name": "Phellodendron amurense",
        "pinyin_name": "Huáng Bǎi",
        "chinese_name": "黄柏",
        "common_names": ["Phellodendron", "Amur Cork Tree"],
        "tradition": "tcm"
    },
    "Chai Hu": {
        "scientific_name": "Bupleurum chinense",
        "pinyin_name": "Chái Hú",
        "chinese_name": "柴胡",
        "common_names": ["Bupleurum", "Hare's Ear"],
        "tradition": "tcm"
    },
    "Dan Shen": {
        "scientific_name": "Salvia miltiorrhiza",
        "pinyin_name": "Dān Shēn",
        "chinese_name": "丹参",
        "common_names": ["Salvia", "Red Sage"],
        "tradition": "tcm"
    },
    "Hong Hua": {
        "scientific_name": "Carthamus tinctorius",
        "pinyin_name": "Hóng Huā",
        "chinese_name": "红花",
        "common_names": ["Safflower", "Carthamus"],
        "tradition": "tcm"
    },
    "Tao Ren": {
        "scientific_name": "Prunus persica",
        "pinyin_name": "Táo Rén",
        "chinese_name": "桃仁",
        "common_names": ["Peach Kernel", "Peach Seed"],
        "tradition": "tcm"
    },
    "Da Zao": {
        "scientific_name": "Ziziphus jujuba",
        "pinyin_name": "Dà Zǎo",
        "chinese_name": "大枣",
        "common_names": ["Red Dates", "Chinese Date", "Jujube"],
        "tradition": "tcm"
    },
    "Long Yan Rou": {
        "scientific_name": "Dimocarpus longan",
        "pinyin_name": "Lóng Yǎn Ròu",
        "chinese_name": "龙眼肉",
        "common_names": ["Longan", "Dragon Eye"],
        "tradition": "tcm"
    },
    "Suan Zao Ren": {
        "scientific_name": "Ziziphus jujuba var. spinosa",
        "pinyin_name": "Suān Zǎo Rén",
        "chinese_name": "酸枣仁",
        "common_names": ["Ziziphus", "Sour Jujube Seed"],
        "tradition": "tcm"
    },
    "Ma Huang": {
        "scientific_name": "Ephedra sinica",
        "pinyin_name": "Má Huáng",
        "chinese_name": "麻黄",
        "common_names": ["Ephedra", "Ma Huang"],
        "tradition": "tcm"
    },
    "Hou Po": {
        "scientific_name": "Magnolia officinalis",
        "pinyin_name": "Hòu Pò",
        "chinese_name": "厚朴",
        "common_names": ["Magnolia Bark", "Magnolia"],
        "tradition": "tcm"
    },
    "Ban Xia": {
        "scientific_name": "Pinellia ternata",
        "pinyin_name": "Bàn Xià",
        "chinese_name": "半夏",
        "common_names": ["Pinellia", "Pinellia Tuber"],
        "tradition": "tcm"
    },
    "Chen Pi": {
        "scientific_name": "Citrus reticulata",
        "pinyin_name": "Chén Pí",
        "chinese_name": "陈皮",
        "common_names": ["Citrus Peel", "Tangerine Peel"],
        "tradition": "tcm"
    },
    "Jie Geng": {
        "scientific_name": "Platycodon grandiflorus",
        "pinyin_name": "Jié Gěng",
        "chinese_name": "桔梗",
        "common_names": ["Platycodon", "Balloon Flower"],
        "tradition": "tcm"
    },
    "Bei Mu": {
        "scientific_name": "Fritillaria cirrhosa",
        "pinyin_name": "Bèi Mǔ",
        "chinese_name": "贝母",
        "common_names": ["Fritillaria", "Fritillary Bulb"],
        "tradition": "tcm"
    },
}


# ============================================================================
# AYURVEDIC PATTERNS
# ============================================================================

AYURVEDIC_PATTERNS = [
    r'(?:Dosha[s]?:\s*)([^\n]+)',
    r'(?:Rasa[s]?:\s*)([^\n]+)',
    r'(?:Guna[s]?:\s*)([^\n]+)',
    r'(?:Virya:\s*)([^\n]+)',
    r'(?:Vipaka:\s*)([^\n]+)',
    r'(?:Prabhava:\s*)([^\n]+)',
    r'(?:Balances?\s+)(Vata|Pitta|Kapha)',
    r'(?:Aggravates?\s+)(Vata|Pitta|Kapha)',
    r'(?:Pacifies?\s+)(Vata|Pitta|Kapha)',
]


# ============================================================================
# TCM PATTERNS
# ============================================================================

TCM_PATTERNS = [
    r'(?:Channel[s]?|Meridian[s]?:\s*)([^\n]+)',
    r'(?:Temperature:\s*)([^\n]+)',
    r'(?:Taste[s]?:\s*)([^\n]+)',
    r'(?:Action[s]?:\s*)([^\n]+)',
    r'(?:Tonifies?\s+)(Qi|Blood|Yin|Yang|Kidney|Liver|Heart|Spleen|Lung)',
    r'(?:Clears?\s+)(Heat|Damp|Phlegm|Wind)',
    r'(?:Moves?\s+)(Qi|Blood)',
    r'(?:Enters?\s+the\s+)(Liver|Heart|Spleen|Lung|Kidney)',
]


# ============================================================================
# PARSER CLASSES
# ============================================================================

class AyurvedicParser:
    """Parser for Ayurvedic herbal medicine text"""
    
    def __init__(self):
        self.herbs = AYURVEDIC_HERBS
        self.patterns = AYURVEDIC_PATTERNS
    
    def _find_pattern_matches(self, pattern: str, text: str) -> list:
        """Helper method to find all pattern matches in text"""
        matches = re.finditer(pattern, text, re.IGNORECASE)
        return [match.group(1).lower() for match in matches]
    
    def parse_dosha_effects(self, text: str) -> Dict[str, str]:
        """Extract dosha balancing/aggravating effects"""
        dosha_effects = {}
        
        # Pattern for balances/pacifies
        for pattern in [r'(?:Balances?|Pacifies?)\s+(Vata|Pitta|Kapha)', 
                       r'(Vata|Pitta|Kapha)[- ](?:balancing|pacifying)']:
            for dosha in self._find_pattern_matches(pattern, text):
                dosha_effects[dosha] = 'pacifies'
        
        # Pattern for aggravates
        for pattern in [r'(?:Aggravates?|Increases?)\s+(Vata|Pitta|Kapha)',
                       r'(Vata|Pitta|Kapha)[- ](?:aggravating|increasing)']:
            for dosha in self._find_pattern_matches(pattern, text):
                dosha_effects[dosha] = 'aggravates'
        
        return dosha_effects
    
    def parse_rasa(self, text: str) -> List[str]:
        """Extract rasa (taste) information"""
        rasas = []
        rasa_terms = ['Madhura', 'Sweet', 'Amla', 'Sour', 'Lavana', 'Salty', 
                      'Katu', 'Pungent', 'Tikta', 'Bitter', 'Kashaya', 'Astringent']
        
        for rasa in rasa_terms:
            if re.search(rf'\b{rasa}\b', text, re.IGNORECASE):
                if rasa not in rasas:
                    rasas.append(rasa)
        
        return rasas
    
    def parse_virya(self, text: str) -> Optional[str]:
        """Extract virya (potency) information"""
        if re.search(r'\b(?:Ushna|Heating|Hot\s+potency)\b', text, re.IGNORECASE):
            return 'Ushna (heating)'
        elif re.search(r'\b(?:Shita|Cooling|Cool\s+potency)\b', text, re.IGNORECASE):
            return 'Shita (cooling)'
        return None
    
    def parse_vipaka(self, text: str) -> Optional[str]:
        """Extract vipaka (post-digestive effect) information"""
        if re.search(r'Vipaka:\s*Madhura', text, re.IGNORECASE):
            return 'Madhura (sweet)'
        elif re.search(r'Vipaka:\s*Amla', text, re.IGNORECASE):
            return 'Amla (sour)'
        elif re.search(r'Vipaka:\s*Katu', text, re.IGNORECASE):
            return 'Katu (pungent)'
        return None
    
    def extract_ayurvedic_properties(self, text: str, herb_name: str) -> dict:
        """Extract all Ayurvedic properties from text"""
        properties = {
            'doshas': self.parse_dosha_effects(text),
            'rasa': self.parse_rasa(text),
            'virya': self.parse_virya(text),
            'vipaka': self.parse_vipaka(text),
        }
        
        # Add Sanskrit name if available
        if herb_name in self.herbs:
            properties['sanskrit_name'] = self.herbs[herb_name].get('sanskrit_name')
        
        return properties


class TCMParser:
    """Parser for Traditional Chinese Medicine herbal text"""
    
    def __init__(self):
        self.herbs = TCM_HERBS
        self.patterns = TCM_PATTERNS
    
    def parse_channels(self, text: str) -> List[str]:
        """Extract channel/meridian affiliations"""
        channels = []
        channel_terms = ['Liver', 'Heart', 'Spleen', 'Lung', 'Kidney', 
                        'Stomach', 'Large Intestine', 'Small Intestine',
                        'Bladder', 'Gallbladder', 'Pericardium', 'Triple Burner']
        
        for channel in channel_terms:
            if re.search(rf'\b{channel}\b.*(?:channel|meridian)', text, re.IGNORECASE):
                if channel not in channels:
                    channels.append(channel)
        
        return channels
    
    def parse_temperature(self, text: str) -> Optional[str]:
        """Extract temperature property"""
        temp_map = {
            r'\b(?:Hot|热)\b': 'Hot',
            r'\b(?:Warm|温)\b': 'Warm',
            r'\b(?:Neutral|平)\b': 'Neutral',
            r'\b(?:Cool|凉)\b': 'Cool',
            r'\b(?:Cold|寒)\b': 'Cold'
        }
        
        for pattern, temp in temp_map.items():
            if re.search(pattern, text, re.IGNORECASE):
                return temp
        return None
    
    def parse_taste(self, text: str) -> List[str]:
        """Extract taste properties"""
        tastes = []
        taste_terms = ['Pungent', 'Sweet', 'Sour', 'Bitter', 'Salty', '辛', '甘', '酸', '苦', '咸']
        
        for taste in taste_terms:
            if re.search(rf'\b{taste}\b', text, re.IGNORECASE):
                if taste not in tastes:
                    tastes.append(taste)
        
        return tastes
    
    def parse_actions(self, text: str) -> List[str]:
        """Extract TCM actions"""
        actions = []
        action_patterns = [
            r'Tonif(?:y|ies)\s+(?:Qi|Blood|Yin|Yang)',
            r'Clears?\s+(?:Heat|Damp|Phlegm|Wind)',
            r'Moves?\s+(?:Qi|Blood)',
            r'Transforms?\s+Phlegm',
            r'Nourishes?\s+(?:Blood|Yin)',
        ]
        
        for pattern in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                action = match.group(0)
                if action not in actions:
                    actions.append(action)
        
        return actions
    
    def extract_tcm_properties(self, text: str, herb_name: str) -> dict:
        """Extract all TCM properties from text"""
        properties = {
            'channels': self.parse_channels(text),
            'tcm_temperature': self.parse_temperature(text),
            'tcm_taste': self.parse_taste(text),
            'tcm_actions': self.parse_actions(text),
        }
        
        # Add Pinyin and Chinese names if available
        if herb_name in self.herbs:
            properties['pinyin_name'] = self.herbs[herb_name].get('pinyin_name')
            properties['chinese_name'] = self.herbs[herb_name].get('chinese_name')
        
        return properties


# ============================================================================
# MAIN PDF PROCESSOR
# ============================================================================

class PDFProcessor:
    """Main PDF processing class for herb extraction"""
    
    def __init__(self):
        self.known_herbs = KNOWN_HERBS
        self.ayurvedic_herbs = AYURVEDIC_HERBS
        self.tcm_herbs = TCM_HERBS
        self.ayurvedic_parser = AyurvedicParser()
        self.tcm_parser = TCMParser()
        
        # Merge all herbs with cross-referencing
        self.all_herbs = self._merge_herb_dictionaries()
    
    def _merge_herb_dictionaries(self) -> Dict[str, dict]:
        """Merge all herb dictionaries, avoiding duplicates and cross-referencing"""
        merged = {}
        
        # Add Western herbs
        for name, data in self.known_herbs.items():
            merged[name] = data.copy()
        
        # Add Ayurvedic herbs (check for cross-references)
        for name, data in self.ayurvedic_herbs.items():
            if name in merged:
                # Cross-reference: add Ayurvedic properties to existing entry
                merged[name]['tradition'] = 'mixed'
                merged[name]['sanskrit_name'] = data.get('sanskrit_name')
            else:
                merged[name] = data.copy()
        
        # Add TCM herbs (check for cross-references)
        for name, data in self.tcm_herbs.items():
            # Check by scientific name for cross-references
            found = False
            for existing_name, existing_data in merged.items():
                if existing_data.get('scientific_name') == data.get('scientific_name'):
                    # Cross-reference found
                    merged[existing_name]['tradition'] = 'mixed'
                    merged[existing_name]['pinyin_name'] = data.get('pinyin_name')
                    merged[existing_name]['chinese_name'] = data.get('chinese_name')
                    # Add TCM name as common name
                    if name not in merged[existing_name].get('common_names', []):
                        merged[existing_name].setdefault('common_names', []).append(name)
                    found = True
                    break
            
            if not found:
                merged[name] = data.copy()
        
        return merged
    
    def extract_herbs_from_text(self, text: str, source_doc: str = "") -> List[ExtractedHerb]:
        """Extract herbs from text content"""
        extracted_herbs = []
        
        for herb_name, herb_data in self.all_herbs.items():
            # Simple pattern matching for herb names
            pattern = rf'\b{re.escape(herb_name)}\b'
            if re.search(pattern, text, re.IGNORECASE):
                herb = ExtractedHerb(
                    name=herb_name,
                    scientific_name=herb_data.get('scientific_name'),
                    common_names=herb_data.get('common_names', []),
                    source_document=source_doc,
                    tradition=herb_data.get('tradition', 'western')
                )
                
                # Extract tradition-specific properties
                tradition = herb_data.get('tradition', 'western')
                
                if tradition in ['ayurvedic', 'mixed']:
                    ayur_props = self.ayurvedic_parser.extract_ayurvedic_properties(text, herb_name)
                    herb.sanskrit_name = ayur_props.get('sanskrit_name')
                    herb.doshas = ayur_props.get('doshas', {})
                    herb.rasa = ayur_props.get('rasa', [])
                    herb.virya = ayur_props.get('virya')
                    herb.vipaka = ayur_props.get('vipaka')
                
                if tradition in ['tcm', 'mixed']:
                    tcm_props = self.tcm_parser.extract_tcm_properties(text, herb_name)
                    herb.pinyin_name = tcm_props.get('pinyin_name')
                    herb.chinese_name = tcm_props.get('chinese_name')
                    herb.channels = tcm_props.get('channels', [])
                    herb.tcm_temperature = tcm_props.get('tcm_temperature')
                    herb.tcm_taste = tcm_props.get('tcm_taste', [])
                    herb.tcm_actions = tcm_props.get('tcm_actions', [])
                
                extracted_herbs.append(herb)
        
        return extracted_herbs
    
    def export_to_json(self, herbs: List[ExtractedHerb], filepath: str):
        """Export extracted herbs to JSON file"""
        herbs_dict = [herb.to_dict() for herb in herbs]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(herbs_dict, f, indent=2, ensure_ascii=False)
    
    def generate_apothecary_code(self, herbs: List[ExtractedHerb]) -> str:
        """Generate Python code for apothecary.py integration"""
        code_lines = [
            "# Generated herb definitions for ApothecaryDaemon",
            "# This code can be integrated into apothecary.py",
            "",
            "# Add these substances to the database:",
            ""
        ]
        
        for herb in herbs:
            code_lines.append(f"self._add_substance(Substance(")
            code_lines.append(f'    name="{herb.name}",')
            code_lines.append(f'    category="herb",')
            
            # Build common names list
            common_names = [herb.name.lower()]
            if herb.common_names:
                common_names.extend([n.lower() for n in herb.common_names])
            if herb.sanskrit_name:
                # Add "sanskrit_name" as a searchable term if different from herb name
                common_names.append(f"{herb.sanskrit_name}")
            if herb.pinyin_name:
                common_names.append(herb.pinyin_name.lower())
            
            code_lines.append(f'    common_names={common_names},')
            code_lines.append(f'    primary_effects=[],  # TODO: Add effects')
            
            # Build description
            desc_parts = []
            if herb.scientific_name:
                desc_parts.append(f"({herb.scientific_name})")
            if herb.tradition:
                desc_parts.append(f"{herb.tradition.title()} herb")
            description = f"{herb.name} " + " - ".join(desc_parts) if desc_parts else herb.name
            
            code_lines.append(f'    description="{description}"')
            code_lines.append(f"))")
            code_lines.append("")
        
        return "\n".join(code_lines)
    
    def get_herb_statistics(self) -> dict:
        """Get statistics about the herb database"""
        stats = {
            'total_herbs': len(self.all_herbs),
            'western_herbs': sum(1 for h in self.all_herbs.values() if h.get('tradition') == 'western'),
            'ayurvedic_herbs': sum(1 for h in self.all_herbs.values() if h.get('tradition') == 'ayurvedic'),
            'tcm_herbs': sum(1 for h in self.all_herbs.values() if h.get('tradition') == 'tcm'),
            'mixed_tradition': sum(1 for h in self.all_herbs.values() if h.get('tradition') == 'mixed'),
        }
        return stats


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Example usage of the PDF processor"""
    processor = PDFProcessor()
    
    # Display statistics
    stats = processor.get_herb_statistics()
    print("PDF Processor - Herb Recognition Module")
    print("=" * 50)
    print(f"Total herbs in database: {stats['total_herbs']}")
    print(f"Western herbs: {stats['western_herbs']}")
    print(f"Ayurvedic herbs: {stats['ayurvedic_herbs']}")
    print(f"TCM herbs: {stats['tcm_herbs']}")
    print(f"Mixed tradition herbs: {stats['mixed_tradition']}")
    print("=" * 50)
    
    # Example: Extract herbs from sample text
    sample_text = """
    Ashwagandha (Withania somnifera) is a powerful adaptogen in Ayurvedic medicine.
    It balances Vata and Kapha doshas. The rasa is bitter, astringent, and sweet.
    Virya is heating (Ushna). Used for stress and anxiety.
    
    Huang Qi (Astragalus) tonifies Qi and strengthens the immune system.
    It enters the Spleen and Lung channels. Temperature is warm, taste is sweet.
    """
    
    herbs = processor.extract_herbs_from_text(sample_text, "sample.pdf")
    print(f"\nExtracted {len(herbs)} herbs from sample text:")
    for herb in herbs:
        print(f"  - {herb.name} ({herb.tradition})")
        if herb.sanskrit_name:
            print(f"    Sanskrit: {herb.sanskrit_name}")
        if herb.pinyin_name:
            print(f"    Pinyin: {herb.pinyin_name}")
        if herb.doshas:
            print(f"    Doshas: {herb.doshas}")
        if herb.channels:
            print(f"    Channels: {herb.channels}")

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
