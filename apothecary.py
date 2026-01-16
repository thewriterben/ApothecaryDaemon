#!/usr/bin/env python3
"""
ApothecaryDaemon - Interactive herbal treatment safety and effectiveness reference

This application helps users check for interactions between herbal supplements,
over-the-counter medications, and prescription drugs to ensure safety and
desired effects.

WARNING: This tool is for informational purposes only and should NOT replace
professional medical advice. Always consult with a healthcare provider before
combining supplements and medications.
"""

import json
import sys
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from enum import Enum


class InteractionSeverity(Enum):
    """Severity levels for interactions"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"


class EffectType(Enum):
    """Types of effects that can occur"""
    RELAXATION = "relaxation"
    STIMULATION = "stimulation"
    SEDATION = "sedation"
    HALLUCINATION = "hallucination"
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    EUPHORIA = "euphoria"
    HYPERACTIVITY = "hyperactivity"
    DROWSINESS = "drowsiness"
    NAUSEA = "nausea"
    BLOOD_PRESSURE_INCREASE = "blood_pressure_increase"
    BLOOD_PRESSURE_DECREASE = "blood_pressure_decrease"
    BLEEDING_RISK = "bleeding_risk"
    LIVER_DAMAGE = "liver_damage"
    SEROTONIN_SYNDROME = "serotonin_syndrome"


@dataclass
class Substance:
    """Represents a substance (herb, supplement, or medication)"""
    name: str
    category: str  # herb, supplement, otc, prescription
    common_names: List[str]
    primary_effects: List[str]
    description: str


@dataclass
class Interaction:
    """Represents an interaction between substances"""
    substance1: str
    substance2: str
    severity: InteractionSeverity
    effects: List[str]
    description: str
    recommendation: str


class InteractionDatabase:
    """Database of substances and their interactions"""
    
    def __init__(self):
        self.substances: Dict[str, Substance] = {}
        self.interactions: List[Interaction] = []
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with common substances and interactions"""
        
        # Add common herbal supplements
        self._add_substance(Substance(
            name="St. John's Wort",
            category="herb",
            common_names=["st johns wort", "hypericum", "hypericum perforatum"],
            primary_effects=["mood elevation", "antidepressant"],
            description="Popular herbal supplement used for mild to moderate depression"
        ))
        
        self._add_substance(Substance(
            name="Valerian Root",
            category="herb",
            common_names=["valerian", "valerian root"],
            primary_effects=["relaxation", "sedation", "sleep aid"],
            description="Herbal supplement commonly used for relaxation and sleep"
        ))
        
        self._add_substance(Substance(
            name="Kava",
            category="herb",
            common_names=["kava", "kava kava", "piper methysticum"],
            primary_effects=["relaxation", "anxiety relief"],
            description="Herb used for anxiety and relaxation"
        ))
        
        self._add_substance(Substance(
            name="Ginseng",
            category="herb",
            common_names=["ginseng", "panax ginseng", "asian ginseng"],
            primary_effects=["energy", "stimulation", "cognitive enhancement"],
            description="Popular herb used for energy and mental clarity"
        ))
        
        self._add_substance(Substance(
            name="Chamomile",
            category="herb",
            common_names=["chamomile", "chamomile tea"],
            primary_effects=["relaxation", "mild sedation", "digestive aid"],
            description="Gentle herb commonly used in teas for relaxation"
        ))
        
        self._add_substance(Substance(
            name="Ginkgo Biloba",
            category="herb",
            common_names=["ginkgo", "ginkgo biloba", "maidenhair tree"],
            primary_effects=["cognitive enhancement", "circulation"],
            description="Herb used for memory and circulation support"
        ))
        
        self._add_substance(Substance(
            name="Passionflower",
            category="herb",
            common_names=["passionflower", "passiflora"],
            primary_effects=["relaxation", "anxiety relief", "sleep aid"],
            description="Herb used for anxiety and sleep support"
        ))
        
        # Add common medications
        self._add_substance(Substance(
            name="Warfarin",
            category="prescription",
            common_names=["warfarin", "coumadin"],
            primary_effects=["blood thinner", "anticoagulant"],
            description="Prescription blood thinner"
        ))
        
        self._add_substance(Substance(
            name="SSRIs",
            category="prescription",
            common_names=["ssri", "ssris", "selective serotonin reuptake inhibitor"],
            primary_effects=["antidepressant"],
            description="Common class of antidepressant medications"
        ))
        
        self._add_substance(Substance(
            name="Benzodiazepines",
            category="prescription",
            common_names=["benzodiazepine", "benzodiazepines", "benzos"],
            primary_effects=["sedation", "anxiety relief"],
            description="Prescription medications for anxiety and sedation"
        ))
        
        self._add_substance(Substance(
            name="Ibuprofen",
            category="otc",
            common_names=["ibuprofen", "advil", "motrin"],
            primary_effects=["pain relief", "anti-inflammatory"],
            description="Common over-the-counter pain reliever"
        ))
        
        self._add_substance(Substance(
            name="Aspirin",
            category="otc",
            common_names=["aspirin", "acetylsalicylic acid"],
            primary_effects=["pain relief", "blood thinner"],
            description="Common over-the-counter pain reliever and blood thinner"
        ))
        
        self._add_substance(Substance(
            name="Diphenhydramine",
            category="otc",
            common_names=["diphenhydramine", "benadryl"],
            primary_effects=["antihistamine", "sedation"],
            description="Common over-the-counter antihistamine and sleep aid"
        ))
        
        # Add interactions
        self._add_interaction(Interaction(
            substance1="St. John's Wort",
            substance2="SSRIs",
            severity=InteractionSeverity.SEVERE,
            effects=["serotonin syndrome", "confusion", "agitation", "rapid heart rate"],
            description="St. John's Wort can increase serotonin levels dangerously when combined with SSRIs",
            recommendation="DO NOT COMBINE. Consult healthcare provider immediately if taking both."
        ))
        
        self._add_interaction(Interaction(
            substance1="Valerian Root",
            substance2="Benzodiazepines",
            severity=InteractionSeverity.MAJOR,
            effects=["excessive sedation", "drowsiness", "impaired coordination"],
            description="Both substances have sedative effects that can be dangerously enhanced",
            recommendation="Avoid combination. If needed, consult healthcare provider for proper dosing."
        ))
        
        self._add_interaction(Interaction(
            substance1="Valerian Root",
            substance2="Diphenhydramine",
            severity=InteractionSeverity.MODERATE,
            effects=["excessive drowsiness", "sedation"],
            description="Combining sedative herbs with antihistamines can cause excessive drowsiness",
            recommendation="Avoid driving or operating machinery. Consider reducing doses or timing separately."
        ))
        
        self._add_interaction(Interaction(
            substance1="Kava",
            substance2="Benzodiazepines",
            severity=InteractionSeverity.MAJOR,
            effects=["excessive sedation", "liver damage risk"],
            description="Kava combined with benzodiazepines increases sedation and liver toxicity risk",
            recommendation="Avoid combination. Consult healthcare provider."
        ))
        
        self._add_interaction(Interaction(
            substance1="Ginkgo Biloba",
            substance2="Warfarin",
            severity=InteractionSeverity.MAJOR,
            effects=["increased bleeding risk", "bruising"],
            description="Ginkgo has blood-thinning properties that enhance warfarin's effects",
            recommendation="Avoid combination. Requires close monitoring if used together."
        ))
        
        self._add_interaction(Interaction(
            substance1="Ginkgo Biloba",
            substance2="Aspirin",
            severity=InteractionSeverity.MODERATE,
            effects=["increased bleeding risk"],
            description="Both substances have blood-thinning effects",
            recommendation="Use caution. Monitor for unusual bleeding or bruising."
        ))
        
        self._add_interaction(Interaction(
            substance1="Ginkgo Biloba",
            substance2="Ibuprofen",
            severity=InteractionSeverity.MODERATE,
            effects=["increased bleeding risk"],
            description="Ginkgo may enhance the blood-thinning effects of NSAIDs",
            recommendation="Use caution. Monitor for unusual bleeding or bruising."
        ))
        
        self._add_interaction(Interaction(
            substance1="Ginseng",
            substance2="Warfarin",
            severity=InteractionSeverity.MODERATE,
            effects=["altered blood clotting", "reduced warfarin effectiveness"],
            description="Ginseng may interfere with warfarin's anticoagulant effects",
            recommendation="Avoid or use with close medical supervision."
        ))
        
        self._add_interaction(Interaction(
            substance1="Chamomile",
            substance2="Warfarin",
            severity=InteractionSeverity.MINOR,
            effects=["potential increased bleeding risk"],
            description="Chamomile may have mild blood-thinning effects",
            recommendation="Generally safe in tea form, but monitor if using concentrated extracts."
        ))
        
        self._add_interaction(Interaction(
            substance1="Chamomile",
            substance2="Benzodiazepines",
            severity=InteractionSeverity.MINOR,
            effects=["mild additional sedation"],
            description="Chamomile has mild sedative effects that may add to benzodiazepines",
            recommendation="Generally safe in moderate amounts. Avoid excessive use."
        ))
        
        self._add_interaction(Interaction(
            substance1="Passionflower",
            substance2="Benzodiazepines",
            severity=InteractionSeverity.MODERATE,
            effects=["excessive sedation", "drowsiness"],
            description="Both have sedative effects that can be enhanced when combined",
            recommendation="Use caution. May need to adjust dosages. Consult healthcare provider."
        ))
    
    def _add_substance(self, substance: Substance):
        """Add a substance to the database"""
        self.substances[substance.name.lower()] = substance
        for name in substance.common_names:
            self.substances[name.lower()] = substance
    
    def _add_interaction(self, interaction: Interaction):
        """Add an interaction to the database"""
        self.interactions.append(interaction)
    
    def find_substance(self, name: str) -> Optional[Substance]:
        """Find a substance by name or common name"""
        return self.substances.get(name.lower())
    
    def check_interactions(self, substance_names: List[str]) -> List[Interaction]:
        """Check for interactions between multiple substances"""
        found_interactions = []
        
        # Normalize substance names
        normalized_names = set()
        for name in substance_names:
            substance = self.find_substance(name)
            if substance:
                normalized_names.add(substance.name)
        
        # Check all pairs for interactions
        for interaction in self.interactions:
            if (interaction.substance1 in normalized_names and 
                interaction.substance2 in normalized_names):
                found_interactions.append(interaction)
        
        return sorted(found_interactions, 
                     key=lambda x: ["minor", "moderate", "major", "severe"].index(x.severity.value),
                     reverse=True)


class ApothecaryDaemon:
    """Main application class"""
    
    def __init__(self):
        self.db = InteractionDatabase()
    
    def display_welcome(self):
        """Display welcome message"""
        print("=" * 70)
        print("ApothecaryDaemon - Herbal Supplement & Medication Interaction Checker")
        print("=" * 70)
        print()
        print("⚠️  WARNING: This tool is for informational purposes only!")
        print("   This is NOT a replacement for professional medical advice.")
        print("   Always consult with a healthcare provider before combining")
        print("   supplements and medications.")
        print()
        print("=" * 70)
        print()
    
    def display_substance_info(self, substance: Substance):
        """Display information about a substance"""
        print(f"\n📋 {substance.name}")
        print(f"   Category: {substance.category.upper()}")
        print(f"   Description: {substance.description}")
        print(f"   Primary Effects: {', '.join(substance.primary_effects)}")
    
    def display_interaction(self, interaction: Interaction):
        """Display an interaction warning"""
        severity_symbols = {
            InteractionSeverity.MINOR: "ℹ️ ",
            InteractionSeverity.MODERATE: "⚠️ ",
            InteractionSeverity.MAJOR: "⛔",
            InteractionSeverity.SEVERE: "🚨"
        }
        
        symbol = severity_symbols.get(interaction.severity, "⚠️ ")
        
        print(f"\n{symbol} {interaction.severity.value.upper()} INTERACTION")
        print(f"   Between: {interaction.substance1} + {interaction.substance2}")
        print(f"   Effects: {', '.join(interaction.effects)}")
        print(f"   Details: {interaction.description}")
        print(f"   ➜ {interaction.recommendation}")
        print()
    
    def interactive_mode(self):
        """Run in interactive mode"""
        self.display_welcome()
        
        print("Enter substances to check (herbs, supplements, medications).")
        print("Type 'done' when finished, 'list' to see available substances, or 'quit' to exit.")
        print()
        
        substances = []
        
        while True:
            user_input = input(f"Enter substance #{len(substances) + 1} (or command): ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("\nThank you for using ApothecaryDaemon. Stay safe!")
                return
            
            if user_input.lower() == 'done':
                if len(substances) < 2:
                    print("⚠️  Please enter at least 2 substances to check for interactions.\n")
                    continue
                break
            
            if user_input.lower() == 'list':
                print("\n📚 Available substances in database:")
                seen = set()
                for name, substance in self.db.substances.items():
                    if substance.name not in seen:
                        print(f"   • {substance.name} ({substance.category})")
                        seen.add(substance.name)
                print()
                continue
            
            substance = self.db.find_substance(user_input)
            if substance:
                if substance.name not in substances:
                    substances.append(substance.name)
                    self.display_substance_info(substance)
                    print(f"\n✓ Added {substance.name}\n")
                else:
                    print(f"⚠️  {substance.name} already added.\n")
            else:
                print(f"⚠️  '{user_input}' not found in database. Try 'list' to see available substances.\n")
        
        # Check interactions
        print("\n" + "=" * 70)
        print("CHECKING FOR INTERACTIONS...")
        print("=" * 70)
        
        interactions = self.db.check_interactions(substances)
        
        if interactions:
            print(f"\n⚠️  Found {len(interactions)} interaction(s):\n")
            for interaction in interactions:
                self.display_interaction(interaction)
        else:
            print("\n✓ No known interactions found in database.")
            print("  However, this does not guarantee safety. Always consult a healthcare provider.")
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Substances checked: {', '.join(substances)}")
        print(f"Interactions found: {len(interactions)}")
        
        if any(i.severity in [InteractionSeverity.MAJOR, InteractionSeverity.SEVERE] 
               for i in interactions):
            print("\n🚨 CRITICAL: Major or severe interactions detected!")
            print("   Consult a healthcare provider before using these substances together.")
        
        print("\n")
    
    def batch_check(self, substance_names: List[str]):
        """Check interactions for a list of substances in batch mode"""
        self.display_welcome()
        
        print(f"Checking interactions for: {', '.join(substance_names)}\n")
        
        # Find all substances
        found_substances = []
        not_found = []
        
        for name in substance_names:
            substance = self.db.find_substance(name)
            if substance:
                if substance.name not in found_substances:
                    found_substances.append(substance.name)
                    self.display_substance_info(substance)
            else:
                not_found.append(name)
        
        if not_found:
            print(f"\n⚠️  Not found in database: {', '.join(not_found)}")
        
        if len(found_substances) < 2:
            print("\n⚠️  Need at least 2 substances to check for interactions.")
            return
        
        # Check interactions
        print("\n" + "=" * 70)
        print("CHECKING FOR INTERACTIONS...")
        print("=" * 70)
        
        interactions = self.db.check_interactions(found_substances)
        
        if interactions:
            print(f"\n⚠️  Found {len(interactions)} interaction(s):\n")
            for interaction in interactions:
                self.display_interaction(interaction)
        else:
            print("\n✓ No known interactions found in database.")
            print("  However, this does not guarantee safety. Always consult a healthcare provider.")
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Substances checked: {', '.join(found_substances)}")
        print(f"Interactions found: {len(interactions)}")
        
        if any(i.severity in [InteractionSeverity.MAJOR, InteractionSeverity.SEVERE] 
               for i in interactions):
            print("\n🚨 CRITICAL: Major or severe interactions detected!")
            print("   Consult a healthcare provider before using these substances together.")
        
        print("\n")


def main():
    """Main entry point"""
    app = ApothecaryDaemon()
    
    if len(sys.argv) > 1:
        # Batch mode - check substances from command line
        substances = sys.argv[1:]
        app.batch_check(substances)
    else:
        # Interactive mode
        app.interactive_mode()


if __name__ == "__main__":
    main()
