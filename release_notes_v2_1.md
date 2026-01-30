### Fixes
- **Date Sensors:** Fixed `ValueError` for 'Next Earnings' by removing the incorrect currency unit from date sensors.
- **Database Optimization:** Simplified news headlines to only include titles and links. This prevents the 'Attributes exceed maximum size' warning and keeps your Home Assistant database lean.
- **Units:** Fixed an issue where percentage sensors (Yield, Weight) were showing currency symbols instead of '%'."
