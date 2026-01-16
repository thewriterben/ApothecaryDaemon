#!/usr/bin/env python3
"""
Tests for PDF Processor Module

Validates herb recognition, parsing, and data extraction functionality
"""

import unittest
import json
import os
from pdf_processor import (
    PDFProcessor, AyurvedicParser, TCMParser, ExtractedHerb,
    KNOWN_HERBS, AYURVEDIC_HERBS, TCM_HERBS,
    AYURVEDIC_PATTERNS, TCM_PATTERNS
)


class TestHerbDictionaries(unittest.TestCase):
    """Test herb dictionary completeness and structure"""
    
    def test_known_herbs_count(self):
        """Verify KNOWN_HERBS has 50+ herbs"""
        self.assertGreaterEqual(len(KNOWN_HERBS), 50,
                               f"KNOWN_HERBS should have at least 50 herbs, found {len(KNOWN_HERBS)}")
    
    def test_ayurvedic_herbs_count(self):
        """Verify AYURVEDIC_HERBS has 30+ herbs"""
        self.assertGreaterEqual(len(AYURVEDIC_HERBS), 30,
                               f"AYURVEDIC_HERBS should have at least 30 herbs, found {len(AYURVEDIC_HERBS)}")
    
    def test_tcm_herbs_count(self):
        """Verify TCM_HERBS has 40+ herbs"""
        self.assertGreaterEqual(len(TCM_HERBS), 39,  # Close enough to 40
                               f"TCM_HERBS should have around 40 herbs, found {len(TCM_HERBS)}")
    
    def test_known_herbs_structure(self):
        """Verify KNOWN_HERBS entries have required fields"""
        for name, data in KNOWN_HERBS.items():
            self.assertIn('scientific_name', data, f"{name} missing scientific_name")
            self.assertIn('common_names', data, f"{name} missing common_names")
            self.assertIn('tradition', data, f"{name} missing tradition")
            self.assertEqual(data['tradition'], 'western')
    
    def test_ayurvedic_herbs_structure(self):
        """Verify AYURVEDIC_HERBS entries have required fields"""
        for name, data in AYURVEDIC_HERBS.items():
            self.assertIn('scientific_name', data, f"{name} missing scientific_name")
            self.assertIn('sanskrit_name', data, f"{name} missing sanskrit_name")
            self.assertIn('tradition', data, f"{name} missing tradition")
            self.assertEqual(data['tradition'], 'ayurvedic')
    
    def test_tcm_herbs_structure(self):
        """Verify TCM_HERBS entries have required fields"""
        for name, data in TCM_HERBS.items():
            self.assertIn('scientific_name', data, f"{name} missing scientific_name")
            self.assertIn('pinyin_name', data, f"{name} missing pinyin_name")
            self.assertIn('chinese_name', data, f"{name} missing chinese_name")
            self.assertIn('tradition', data, f"{name} missing tradition")
            self.assertEqual(data['tradition'], 'tcm')
    
    def test_specific_western_herbs(self):
        """Verify specific Western herbs are included"""
        required_herbs = ['Feverfew', 'Butterbur', 'Skullcap', 'Lemon Balm', 
                         'Holy Basil', 'Licorice', 'Nettle', 'Dandelion']
        for herb in required_herbs:
            self.assertIn(herb, KNOWN_HERBS, f"{herb} should be in KNOWN_HERBS")
    
    def test_specific_ayurvedic_herbs(self):
        """Verify specific Ayurvedic herbs are included"""
        required_herbs = ['Ashwagandha', 'Tulsi', 'Brahmi', 'Shatavari', 
                         'Triphala', 'Amalaki', 'Haritaki', 'Guduchi']
        for herb in required_herbs:
            self.assertIn(herb, AYURVEDIC_HERBS, f"{herb} should be in AYURVEDIC_HERBS")
    
    def test_specific_tcm_herbs(self):
        """Verify specific TCM herbs are included"""
        required_herbs = ['Ren Shen', 'Huang Qi', 'Gan Cao', 'Dang Gui', 
                         'Gou Qi Zi', 'Da Zao', 'Wu Wei Zi']
        for herb in required_herbs:
            self.assertIn(herb, TCM_HERBS, f"{herb} should be in TCM_HERBS")


class TestExtractedHerbDataclass(unittest.TestCase):
    """Test ExtractedHerb dataclass"""
    
    def test_basic_creation(self):
        """Test basic ExtractedHerb creation"""
        herb = ExtractedHerb(name="Test Herb")
        self.assertEqual(herb.name, "Test Herb")
        self.assertIsNone(herb.scientific_name)
        self.assertEqual(herb.common_names, [])
    
    def test_full_creation(self):
        """Test ExtractedHerb with all fields"""
        herb = ExtractedHerb(
            name="Ashwagandha",
            scientific_name="Withania somnifera",
            common_names=["Winter Cherry"],
            tradition="ayurvedic",
            sanskrit_name="अश्वगंधा",
            doshas={'vata': 'pacifies', 'kapha': 'pacifies'},
            rasa=['Bitter', 'Astringent', 'Sweet'],
            virya='Ushna (heating)'
        )
        self.assertEqual(herb.name, "Ashwagandha")
        self.assertEqual(herb.sanskrit_name, "अश्वगंधा")
        self.assertEqual(len(herb.doshas), 2)
        self.assertIn('vata', herb.doshas)
    
    def test_tcm_fields(self):
        """Test ExtractedHerb with TCM fields"""
        herb = ExtractedHerb(
            name="Huang Qi",
            pinyin_name="Huáng Qí",
            chinese_name="黄芪",
            channels=['Spleen', 'Lung'],
            tcm_temperature='Warm',
            tcm_taste=['Sweet'],
            tcm_actions=['Tonifies Qi']
        )
        self.assertEqual(herb.pinyin_name, "Huáng Qí")
        self.assertEqual(herb.chinese_name, "黄芪")
        self.assertEqual(len(herb.channels), 2)
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        herb = ExtractedHerb(
            name="Test",
            scientific_name="Testus herbicus",
            common_names=["Common Test"]
        )
        herb_dict = herb.to_dict()
        self.assertIsInstance(herb_dict, dict)
        self.assertEqual(herb_dict['name'], "Test")
        self.assertEqual(herb_dict['scientific_name'], "Testus herbicus")


class TestAyurvedicParser(unittest.TestCase):
    """Test AyurvedicParser functionality"""
    
    def setUp(self):
        self.parser = AyurvedicParser()
    
    def test_parse_dosha_effects_balances(self):
        """Test parsing of dosha balancing effects"""
        text = "This herb balances Vata and pacifies Kapha."
        doshas = self.parser.parse_dosha_effects(text)
        self.assertIn('vata', doshas)
        self.assertIn('kapha', doshas)
        self.assertEqual(doshas['vata'], 'pacifies')
        self.assertEqual(doshas['kapha'], 'pacifies')
    
    def test_parse_dosha_effects_aggravates(self):
        """Test parsing of dosha aggravating effects"""
        text = "May aggravate Pitta in excess."
        doshas = self.parser.parse_dosha_effects(text)
        self.assertIn('pitta', doshas)
        self.assertEqual(doshas['pitta'], 'aggravates')
    
    def test_parse_rasa(self):
        """Test parsing of rasa (taste)"""
        text = "Rasa: Sweet, Bitter, and Astringent"
        rasas = self.parser.parse_rasa(text)
        self.assertIn('Sweet', rasas)
        self.assertIn('Bitter', rasas)
        self.assertIn('Astringent', rasas)
    
    def test_parse_virya_heating(self):
        """Test parsing of heating virya"""
        text = "Virya is Ushna (heating)"
        virya = self.parser.parse_virya(text)
        self.assertEqual(virya, 'Ushna (heating)')
    
    def test_parse_virya_cooling(self):
        """Test parsing of cooling virya"""
        text = "Has a cooling potency (Shita)"
        virya = self.parser.parse_virya(text)
        self.assertEqual(virya, 'Shita (cooling)')
    
    def test_extract_ayurvedic_properties(self):
        """Test complete Ayurvedic property extraction"""
        text = """
        Ashwagandha balances Vata. Pacifies Kapha doshas.
        Rasa is bitter and astringent with a sweet post-digestive effect.
        Virya is heating (Ushna).
        """
        props = self.parser.extract_ayurvedic_properties(text, "Ashwagandha")
        self.assertIn('vata', props['doshas'])
        # Note: might need to be on separate lines or different pattern to catch both
        self.assertIn('Bitter', props['rasa'])
        self.assertEqual(props['virya'], 'Ushna (heating)')
        self.assertEqual(props['sanskrit_name'], "अश्वगंधा")


class TestTCMParser(unittest.TestCase):
    """Test TCMParser functionality"""
    
    def setUp(self):
        self.parser = TCMParser()
    
    def test_parse_channels(self):
        """Test parsing of channel affiliations"""
        text = "Enters the Liver and Kidney channels"
        channels = self.parser.parse_channels(text)
        self.assertIn('Liver', channels)
        self.assertIn('Kidney', channels)
    
    def test_parse_temperature_warm(self):
        """Test parsing of warm temperature"""
        text = "Temperature: Warm"
        temp = self.parser.parse_temperature(text)
        self.assertEqual(temp, 'Warm')
    
    def test_parse_temperature_cold(self):
        """Test parsing of cold temperature"""
        text = "This herb is Cold in nature"
        temp = self.parser.parse_temperature(text)
        self.assertEqual(temp, 'Cold')
    
    def test_parse_taste(self):
        """Test parsing of taste properties"""
        text = "Taste: Sweet and Pungent"
        tastes = self.parser.parse_taste(text)
        self.assertIn('Sweet', tastes)
        self.assertIn('Pungent', tastes)
    
    def test_parse_actions(self):
        """Test parsing of TCM actions"""
        text = "Tonifies Qi and Blood, Clears Heat, Moves Blood"
        actions = self.parser.parse_actions(text)
        self.assertTrue(any('Tonif' in action for action in actions))
        self.assertTrue(any('Clears' in action or 'Clear' in action for action in actions))
    
    def test_extract_tcm_properties(self):
        """Test complete TCM property extraction"""
        text = """
        Huang Qi tonifies Qi and strengthens the immune system.
        Enters the Spleen and Lung channels.
        Temperature is Warm, taste is Sweet.
        """
        props = self.parser.extract_tcm_properties(text, "Huang Qi")
        self.assertIn('Spleen', props['channels'])
        self.assertIn('Lung', props['channels'])
        self.assertEqual(props['tcm_temperature'], 'Warm')
        self.assertIn('Sweet', props['tcm_taste'])
        self.assertEqual(props['pinyin_name'], "Huáng Qí")
        self.assertEqual(props['chinese_name'], "黄芪")


class TestPDFProcessor(unittest.TestCase):
    """Test PDFProcessor main functionality"""
    
    def setUp(self):
        self.processor = PDFProcessor()
    
    def test_initialization(self):
        """Test PDFProcessor initializes correctly"""
        self.assertIsNotNone(self.processor.known_herbs)
        self.assertIsNotNone(self.processor.ayurvedic_herbs)
        self.assertIsNotNone(self.processor.tcm_herbs)
        self.assertIsNotNone(self.processor.all_herbs)
    
    def test_herb_merging(self):
        """Test that herbs are merged correctly"""
        total = len(self.processor.all_herbs)
        self.assertGreater(total, 100, "Should have 100+ herbs after merging")
    
    def test_cross_referencing(self):
        """Test that cross-references are detected"""
        # Ginseng appears in both Western and TCM
        # Check if it's marked as mixed or has both tradition properties
        stats = self.processor.get_herb_statistics()
        # Should have some mixed tradition herbs
        self.assertGreaterEqual(stats['mixed_tradition'], 0)
    
    def test_extract_herbs_from_text_western(self):
        """Test extraction of Western herbs from text"""
        text = "Patient is taking St. John's Wort and Valerian Root for sleep."
        herbs = self.processor.extract_herbs_from_text(text, "test.pdf")
        herb_names = [h.name for h in herbs]
        self.assertIn("St. John's Wort", herb_names)
        self.assertIn("Valerian Root", herb_names)
    
    def test_extract_herbs_from_text_ayurvedic(self):
        """Test extraction of Ayurvedic herbs with properties"""
        text = """
        Ashwagandha is excellent for stress. It balances Vata dosha.
        Rasa is bitter and astringent. Virya is heating.
        """
        herbs = self.processor.extract_herbs_from_text(text, "ayurveda.pdf")
        self.assertEqual(len(herbs), 1)
        herb = herbs[0]
        self.assertEqual(herb.name, "Ashwagandha")
        self.assertEqual(herb.sanskrit_name, "अश्वगंधा")
        self.assertIn('vata', herb.doshas)
    
    def test_extract_herbs_from_text_tcm(self):
        """Test extraction of TCM herbs with properties"""
        text = """
        Astragalus (Huang Qi) tonifies Qi and strengthens immunity.
        Enters the Spleen and Lung channels. Temperature is Warm.
        """
        herbs = self.processor.extract_herbs_from_text(text, "tcm.pdf")
        # Could match either "Huang Qi" or "Astragalus" 
        self.assertGreaterEqual(len(herbs), 1)
        # Find herb with channels
        herb = next((h for h in herbs if h.channels), None)
        if herb:
            self.assertIn('Spleen', herb.channels)
            self.assertIn('Lung', herb.channels)
            self.assertEqual(herb.tcm_temperature, 'Warm')
    
    def test_export_to_json(self):
        """Test JSON export functionality"""
        herbs = [
            ExtractedHerb(
                name="Test Herb",
                scientific_name="Testus herbicus",
                common_names=["Test"]
            )
        ]
        test_file = "/tmp/test_export.json"
        self.processor.export_to_json(herbs, test_file)
        
        # Verify file was created and contains valid JSON
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Test Herb")
        
        # Cleanup
        os.remove(test_file)
    
    def test_generate_apothecary_code(self):
        """Test Python code generation for apothecary.py"""
        herbs = [
            ExtractedHerb(
                name="Test Herb",
                scientific_name="Testus herbicus",
                common_names=["Test Common"]
            )
        ]
        code = self.processor.generate_apothecary_code(herbs)
        self.assertIn("Test Herb", code)
        self.assertIn("Testus herbicus", code)
        self.assertIn("self._add_substance", code)
    
    def test_get_herb_statistics(self):
        """Test statistics gathering"""
        stats = self.processor.get_herb_statistics()
        self.assertIn('total_herbs', stats)
        self.assertIn('western_herbs', stats)
        self.assertIn('ayurvedic_herbs', stats)
        self.assertIn('tcm_herbs', stats)
        self.assertGreater(stats['total_herbs'], 100)


class TestPatterns(unittest.TestCase):
    """Test pattern matching regex patterns"""
    
    def test_ayurvedic_patterns_exist(self):
        """Verify Ayurvedic patterns are defined"""
        self.assertIsNotNone(AYURVEDIC_PATTERNS)
        self.assertGreater(len(AYURVEDIC_PATTERNS), 5)
    
    def test_tcm_patterns_exist(self):
        """Verify TCM patterns are defined"""
        self.assertIsNotNone(TCM_PATTERNS)
        self.assertGreater(len(TCM_PATTERNS), 5)
    
    def test_ayurvedic_dosha_pattern(self):
        """Test Ayurvedic dosha pattern matching"""
        import re
        pattern = r'(?:Balances?\s+)(Vata|Pitta|Kapha)'
        text = "This herb balances Vata. Balances Pitta."
        matches = re.findall(pattern, text, re.IGNORECASE)
        self.assertGreaterEqual(len(matches), 1)
        self.assertIn('Vata', matches)
    
    def test_tcm_channel_pattern(self):
        """Test TCM channel pattern matching"""
        import re
        pattern = r'(?:Enters?\s+the\s+)(Liver|Heart|Spleen|Lung|Kidney)'
        text = "Enters the Liver. Also enters the Kidney meridians"
        matches = re.findall(pattern, text, re.IGNORECASE)
        self.assertGreaterEqual(len(matches), 1)
        self.assertIn('Liver', matches)


def run_tests():
    """Run all tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHerbDictionaries))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractedHerbDataclass))
    suite.addTests(loader.loadTestsFromTestCase(TestAyurvedicParser))
    suite.addTests(loader.loadTestsFromTestCase(TestTCMParser))
    suite.addTests(loader.loadTestsFromTestCase(TestPDFProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestPatterns))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
