# Changelog

## Unreleased

### Fixed

**LEDD Calculations** 
  - Added `directory=DATA_DIR` argument to `get_latest_file()` for the LEDD Concomitant Medication Log file import. Default was working if the Jupyter notebook was launched from the right directory, but the notebook could fail to find the file if Jupyter was launched elsewhere.
  - Added a missing comma in the `maob_names` list. Previously was missing a comma between `'Azilect'` and `'Safinamid'`, so they were silently concatenated into a single string (`'AzilectSafinamid'`). This means neither MAO-B inhibitor was matching with the data previously.
  - corrected `'Artanis'` to `'Artane'` in the anticholinergic medication name list; the misspelled brand name meant Artane was not matching previously.
  - the entacapone/COMT-adjustment step relied on a hardcoded dataset-download date (`pd.to_datetime('2025-01-01')`) to fill missing `STOPDT` values, which silently produces wrong results if left stale after downloading a new data extract. Now derived automatically from the LEDD filename via `extract_date_from_filename()`, with a clear error if the filename can't be parsed instead of a silent wrong default.

**utils/helpers.py**
  - `get_latest_file()` sorted candidate files by the embedded date as a raw string rather than an actual date, which can pick the wrong "latest" file across different months (e.g. `"01Apr2025"` sorts before `"01Jan2025"` alphabetically). Now sorts using `extract_date_from_filename()` so ordering is chronological.


### Added

**utils/helpers.py**
  - `check_unmatched_terms()` — given a dict of `{label: [term, ...]}` and a free-text column, reports any term that never appears in the data. Catches typos, terms silently merged by a missing comma, and case-sensitivity mismatches before they cause silent under-counting.
  - `extract_date_from_filename()` — parses the "DDMonYYYY" date embedded in PPMI/LONI download filenames (e.g. `"LEDD_Concomitant_Medication_Log_24Jul2026.csv"` → `2026-07-24`) into a proper date, for notebooks that need "the date this dataset was downloaded" without relying on a hardcoded value.

**LEDD Calculations**
  - Sanity-check cells using `check_unmatched_terms()`  against drugs listed in `LEDTRT`. Flags aren't necessarily bugs. Should help to catch issues like the missing comma fixed above.

