#!/usr/bin/env python3
"""Test script to verify TCE date/time extraction"""
from tce_monitor import extract_date_time_from_text

# Test cases
test_cases = [
    ("Начало 07.01.2026 в 15:45", "07.01.2026", "15:45"),
    ("Концерт начнется Начало 15.12.2025 в 19:00 в большом зале", "15.12.2025", "19:00"),
    ("начало 25.03.2025 в 20:30", "25.03.2025", "20:30"),  # lowercase
    ("Дата: 10.05.2025, время 18:00", "10.05.2025", "18:00"),  # fallback pattern
    ("Событие 01.01.2026", "01.01.2026", None),  # date only
    ("No date here", None, None),  # no match
]

print("=" * 70)
print("Testing TCE Date/Time Extraction")
print("=" * 70)

all_passed = True

for i, (text, expected_date, expected_time) in enumerate(test_cases, 1):
    print(f"\nTest {i}:")
    print(f"Input: {text}")
    print(f"Expected: date={expected_date}, time={expected_time}")

    date_str, time_str = extract_date_time_from_text(text)

    print(f"Got:      date={date_str}, time={time_str}")

    if date_str == expected_date and time_str == expected_time:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print("✅ All tests PASSED!")
else:
    print("❌ Some tests FAILED")
print("=" * 70)
