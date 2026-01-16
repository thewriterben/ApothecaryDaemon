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
