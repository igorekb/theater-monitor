# TCE.BY Scanning Logic - Visual Guide

## Overview

The TCE.BY scanner uses a **range-based approach** that always checks 10 IDs ahead of the last found event.

## Key Concept: Base ID

- **Base ID** = Last found event ID (or config default on first run)
- Always checks next 10 IDs from base: `[base+1, base+2, ..., base+10]`
- When event found, that ID becomes new base
- Stops when no events found in 10 ID range

## Visual Example

```
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 1: Base = 4070                                    │
├─────────────────────────────────────────────────────────────┤
│ Check IDs: 4071 → 4080                                      │
│                                                              │
│ 4071 [404] ────┐                                            │
│ 4072 [404]     │                                            │
│ 4073 [EVENT]   ├─→ Events found!                            │
│ 4074 [404]     │   Highest ID: 4075                         │
│ 4075 [EVENT] ──┘                                            │
│ 4076 [404]                                                  │
│ 4077 [404]                                                  │
│ 4078 [404]                                                  │
│ 4079 [404]                                                  │
│ 4080 [404]                                                  │
│                                                              │
│ Result: Update base to 4075                                 │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 2: Base = 4075 (from highest found)              │
├─────────────────────────────────────────────────────────────┤
│ Check IDs: 4076 → 4085                                      │
│                                                              │
│ 4076 [404]                                                  │
│ 4077 [404]                                                  │
│ 4078 [404]                                                  │
│ 4079 [404]                                                  │
│ 4080 [404]     Event found!                                 │
│ 4081 [404]     Highest ID: 4082                             │
│ 4082 [EVENT] ──┘                                            │
│ 4083 [404]                                                  │
│ 4084 [404]                                                  │
│ 4085 [404]                                                  │
│                                                              │
│ Result: Update base to 4082                                 │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ ITERATION 3: Base = 4082                                    │
├─────────────────────────────────────────────────────────────┤
│ Check IDs: 4083 → 4092                                      │
│                                                              │
│ 4083 [404]                                                  │
│ 4084 [404]                                                  │
│ 4085 [404]                                                  │
│ 4086 [404]                                                  │
│ 4087 [404]     No events found                              │
│ 4088 [404]     in this range                                │
│ 4089 [404]                                                  │
│ 4090 [404]                                                  │
│ 4091 [404]                                                  │
│ 4092 [404]                                                  │
│                                                              │
│ Result: STOP - Save base 4082                               │
└─────────────────────────────────────────────────────────────┘
                        ↓
            Next run starts from 4082
            (will check 4083-4092 again)
```

## Comparison: Old vs New Logic

### Old Logic (Consecutive 404s)
```
Start: 4070
4070 → Event (404 count: 0)
4071 → 404 (404 count: 1)
4072 → 404 (404 count: 2)
...
4080 → 404 (404 count: 10)
STOP

Problem: If event at 4085, we'd miss it!
```

### New Logic (Range-Based)
```
Base: 4070
Check 4071-4080 → No events
STOP

But next run:
Base: 4070 (unchanged)
Check 4071-4080 again

If event added at 4075:
Base: 4070
Check 4071-4080 → Found 4075!
Base: 4075
Check 4076-4085 → Would find 4085!
```

## Advantages

### 1. No Skipped IDs
Always checks every ID in the 10 ID window ahead of base.

### 2. Smart Continuation
When event found at ID X, immediately checks 10 IDs from X.

### 3. Handles Sparse Events
Works efficiently even if events are spread out:
```
Events at: 4070, 4080, 4090

Iteration 1: Base 4070, check 4071-4080 → Find 4080
Iteration 2: Base 4080, check 4081-4090 → Find 4090
Iteration 3: Base 4090, check 4091-4100 → None
Stop at 4090
```

### 4. Re-checks Same Range
If no events found, next run checks same range again.
Perfect for catching newly added events.

## Configuration

```python
# config.py
TCE_START_ID = 4070      # Initial base (first run only)
TCE_ID_RANGE = 10        # How many IDs to check ahead
```

## Real-World Scenarios

### Scenario 1: New Event Added Daily
```
Day 1: Base 4070, check 4071-4080 → Find 4075
       Base 4075, check 4076-4085 → None
       Save base: 4075

Day 2: Base 4075, check 4076-4085 → Find 4081
       Base 4081, check 4082-4091 → None
       Save base: 4081

Result: Catches each new event and moves forward
```

### Scenario 2: Multiple Events in Batch
```
Events added at: 4073, 4075, 4078

Run: Base 4070, check 4071-4080
     → Find 4073, 4075, 4078
     → Highest: 4078
     Base 4078, check 4079-4088
     → None
     Save base: 4078

Result: Finds all events in one run!
```

### Scenario 3: Large Gap Between Events
```
Events at: 4070, 4095 (25 IDs apart)

Run 1: Base 4070, check 4071-4080 → None
       Save base: 4070

Run 2: Base 4070, check 4071-4080 → None
       Save base: 4070

Eventually: Event added at 4075
Run N: Base 4070, check 4071-4080 → Find 4075
       Base 4075, check 4076-4085 → None
       Base 4085, check 4086-4095 → Find 4095!

Result: Will eventually find 4095 through progressive checking
```

## Summary

| Feature | Old Logic | New Logic |
|---------|-----------|-----------|
| Stop condition | 10 consecutive 404s | No events in 10 ID range |
| ID skipping | Possible | Never |
| Continuation | Linear +1 | Jump to highest found |
| Re-checking | No | Yes (same range if no events) |
| Efficiency | Good for dense | Good for any distribution |

The new logic is more robust and adapts to any event distribution pattern!
