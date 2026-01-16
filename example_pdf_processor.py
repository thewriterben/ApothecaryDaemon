#!/usr/bin/env python3
"""
Example demonstration of PDF Processor functionality

This script shows how to use the new PDF processing module to:
1. View herb database statistics
2. Extract herbs from sample text
3. Export to JSON
4. Generate code for apothecary.py integration
"""

from pdf_processor import PDFProcessor


def main():
    print("=" * 70)
    print("PDF Processor Module - Example Demonstration")
    print("=" * 70)
    print()
    
    # Initialize processor
    processor = PDFProcessor()
    
    # 1. Display statistics
    print("📊 HERB DATABASE STATISTICS")
    print("-" * 70)
    stats = processor.get_herb_statistics()
    print(f"Total herbs in database: {stats['total_herbs']}")
    print(f"  └─ Western herbs: {stats['western_herbs']}")
    print(f"  └─ Ayurvedic herbs: {stats['ayurvedic_herbs']}")
    print(f"  └─ TCM herbs: {stats['tcm_herbs']}")
    print(f"  └─ Mixed tradition herbs: {stats['mixed_tradition']}")
    print()
    
    # 2. Extract herbs from multi-tradition text
    print("📖 EXTRACTING HERBS FROM SAMPLE TEXT")
    print("-" * 70)
    
    sample_text = """
    Traditional Medicine Case Study:
    
    AYURVEDIC APPROACH:
    Patient prescribed Ashwagandha for stress management. This herb balances 
    Vata and Kapha doshas. Rasa is bitter, astringent, and sweet. Virya is 
    heating (Ushna). Also recommended Brahmi for cognitive support.
    
    CHINESE MEDICINE APPROACH:
    Huang Qi (Astragalus) to tonify Qi and strengthen immunity. Enters the 
    Spleen and Lung channels. Temperature is Warm, taste is Sweet. Combined 
    with Gan Cao (Licorice) to harmonize the formula.
    
    WESTERN HERBALISM:
    St. John's Wort for mild depression, Valerian Root for sleep support.
    Also considering Feverfew for migraine prevention and Nettle for allergies.
    """
    
    print("Sample text:")
    print(sample_text[:200] + "...")
    print()
    
    herbs = processor.extract_herbs_from_text(sample_text, source_doc="example.pdf")
    
    print(f"✓ Extracted {len(herbs)} herbs:")
    print()
    
    # 3. Display extracted herbs with details
    for i, herb in enumerate(herbs, 1):
        print(f"{i}. {herb.name}")
        print(f"   Scientific name: {herb.scientific_name or 'N/A'}")
        print(f"   Tradition: {herb.tradition}")
        
        # Show tradition-specific properties
        if herb.tradition in ['ayurvedic', 'mixed'] and herb.sanskrit_name:
            print(f"   Sanskrit: {herb.sanskrit_name}")
            if herb.doshas:
                print(f"   Doshas: {herb.doshas}")
            if herb.rasa:
                print(f"   Rasa (tastes): {', '.join(herb.rasa)}")
            if herb.virya:
                print(f"   Virya (potency): {herb.virya}")
        
        if herb.tradition in ['tcm', 'mixed'] and herb.pinyin_name:
            print(f"   Pinyin: {herb.pinyin_name}")
            if herb.chinese_name:
                print(f"   Chinese: {herb.chinese_name}")
            if herb.channels:
                print(f"   Channels: {', '.join(herb.channels)}")
            if herb.tcm_temperature:
                print(f"   Temperature: {herb.tcm_temperature}")
            if herb.tcm_taste:
                print(f"   Taste: {', '.join(herb.tcm_taste)}")
        
        print()
    
    # 4. Export to JSON
    print("💾 EXPORTING TO JSON")
    print("-" * 70)
    output_file = "/tmp/extracted_herbs_example.json"
    processor.export_to_json(herbs, output_file)
    print(f"✓ Exported {len(herbs)} herbs to: {output_file}")
    print()
    
    # 5. Generate code for apothecary.py
    print("🔧 GENERATING PYTHON CODE FOR APOTHECARY.PY")
    print("-" * 70)
    code = processor.generate_apothecary_code(herbs[:3])  # First 3 herbs as example
    print("Sample generated code (first 3 herbs):")
    print()
    print(code[:500] + "...")
    print()
    
    print("=" * 70)
    print("✓ Demonstration complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Run the full module: python3 pdf_processor.py")
    print("  2. Run tests: python3 test_pdf_processor.py")
    print("  3. Read documentation: PDF_PROCESSOR_README.md")
    print("  4. Integrate with your PDF processing workflow")
    print()


if __name__ == "__main__":
    main()
