# Example Usage Scenarios

This document provides real-world scenarios demonstrating how ApothecaryDaemon helps prevent dangerous interactions and unexpected effects.

## Scenario 1: Relaxation Tea Gone Wrong

**Situation**: A user wants to brew chamomile tea for relaxation but has already taken Benadryl (diphenhydramine) for allergies.

**Command**:
```bash
python3 apothecary.py chamomile benadryl
```

**Result**: The application warns of MODERATE interaction causing excessive drowsiness and sedation. The user learns to avoid activities requiring alertness.

**Without ApothecaryDaemon**: The user might have experienced unexpected extreme drowsiness, making it dangerous to drive or operate machinery.

---

## Scenario 2: Dangerous Antidepressant Combination

**Situation**: A user is taking prescription SSRIs for depression and reads online that St. John's Wort is a "natural antidepressant."

**Command**:
```bash
python3 apothecary.py "st johns wort" ssri
```

**Result**: The application displays a SEVERE interaction warning about serotonin syndrome, with effects including confusion, agitation, and rapid heart rate. The recommendation is "DO NOT COMBINE."

**Without ApothecaryDaemon**: The user could develop life-threatening serotonin syndrome, requiring emergency medical treatment.

---

## Scenario 3: Blood Thinner Overload

**Situation**: A patient on warfarin for heart health takes ginkgo biloba for memory and occasional aspirin for headaches.

**Command**:
```bash
python3 apothecary.py "ginkgo biloba" warfarin aspirin
```

**Result**: The application identifies two interactions:
- MAJOR: Ginkgo + Warfarin (increased bleeding risk)
- MODERATE: Ginkgo + Aspirin (increased bleeding risk)

**Without ApothecaryDaemon**: The user faces significantly increased bleeding risk, potentially leading to dangerous internal bleeding or excessive bleeding from minor cuts.

---

## Scenario 4: Sedative Stacking

**Situation**: A person with anxiety takes prescribed benzodiazepines and adds valerian root thinking "natural" means it's safe to combine.

**Command**:
```bash
python3 apothecary.py "valerian root" benzodiazepines
```

**Result**: The application warns of MAJOR interaction causing excessive sedation and impaired coordination.

**Without ApothecaryDaemon**: The user might experience dangerous levels of sedation, respiratory depression, or impaired motor function leading to falls or accidents.

---

## Scenario 5: Anxiety Relief Combination

**Situation**: A user wants to combine kava and benzodiazepines for anxiety relief.

**Command**:
```bash
python3 apothecary.py kava benzodiazepines
```

**Result**: MAJOR interaction warning for excessive sedation and liver damage risk.

**Without ApothecaryDaemon**: Risk of severe sedation and potential liver toxicity.

---

## Scenario 6: Safe Combination Check

**Situation**: A user wants to have chamomile tea in the evening and ginseng tea in the morning.

**Command**:
```bash
python3 apothecary.py chamomile ginseng
```

**Result**: No known interactions found. The application still reminds users to consult healthcare providers.

**Learning**: Not all combinations are dangerous, and the tool helps identify what's safe as well as what's risky.

---

## Scenario 7: Interactive Mode Example

**Situation**: A user wants a guided experience to check multiple substances.

**Command**:
```bash
python3 apothecary.py
```

**Interactive Session**:
```
Enter substance #1: passionflower
Enter substance #2: benzodiazepines  
Enter substance #3: done
```

**Result**: MODERATE interaction warning for excessive sedation and drowsiness.

---

## Scenario 8: Preventing Unexpected Effects

**Situation**: Someone brewing an herbal tea blend for relaxation includes multiple sedative herbs while taking sleep medications.

**Command**:
```bash
python3 apothecary.py "valerian root" passionflower chamomile diphenhydramine
```

**Result**: Multiple interaction warnings showing cumulative sedative effects.

**Without ApothecaryDaemon**: Instead of gentle relaxation, the user might experience:
- Extreme drowsiness
- Impaired coordination
- Difficulty waking up
- Potential respiratory depression

---

## Key Benefits Demonstrated

1. **Prevents Unexpected Effects**: Users expecting relaxation won't get hallucinations, hyperactivity, or dangerous sedation
2. **Severity Classification**: Clear indication of which combinations are merely cautionary vs. life-threatening
3. **Practical Recommendations**: Specific guidance on what to do (avoid, reduce dose, monitor, consult doctor)
4. **Safety First**: Consistent reminders that the tool supplements but doesn't replace medical advice

---

## Using the Examples

To try any example:

1. Navigate to the ApothecaryDaemon directory
2. Copy and paste the command from any scenario
3. Review the output and warnings
4. Consider how this information protects user safety

Remember: Always consult healthcare providers before making decisions about combining substances!
