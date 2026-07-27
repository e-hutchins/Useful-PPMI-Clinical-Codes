import os
import glob
import re
import pandas as pd

#pulls the embedded download date out of a PPMI/LONI filename, e.g.
#"LEDD_Concomitant_Medication_Log_24Jul2026.csv" -> Timestamp("2026-07-24")
def extract_date_from_filename(filename):
    """
    Parse the date embedded in a PPMI/LONI download filename (format
    "DDMonYYYY", e.g. "24Jul2026") and return it as a pandas Timestamp.

    Useful for notebooks that need "the date this dataset was downloaded"
    (e.g. to fill in still-open medication end dates) without relying on
    someone remembering to hardcode it by hand.

    Returns None if no matching date pattern is found in `filename`.
    """
    match = re.search(r"(\d{2}[A-Za-z]{3}\d{4})", filename)
    if not match:
        return None
    return pd.to_datetime(match.group(1), format="%d%b%Y")

#function for importing files based on prefix
#this future proofs for future updates with different date suffixes
def get_latest_file(prefix, ext=".csv", directory="../data/"):
    """
    Finds the most recent file with the given prefix and extension.
    """
    print(f"Looking for files in: {directory}")

    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist.")

    # Search for files matching the pattern
    pattern = os.path.join(directory, f"{prefix}_*{ext}")
    files = glob.glob(pattern)

    print(f"Found files: {files}")  # Debugging output

    if not files:
        raise FileNotFoundError(f"No files found matching {prefix}_*.{ext} in {directory}")

    # Sort by the actual embedded date (not the raw filename string) so files
    # are ordered chronologically rather than alphabetically across months
    # (e.g. "01Apr2025" would otherwise sort before "01Jan2025"). Filenames
    # with no parseable date are treated as oldest, so they sort last.
    files.sort(key=lambda f: extract_date_from_filename(f) or pd.Timestamp.min, reverse=True)

    latest_file = files[0]
    print(f"Latest file: {latest_file}")
    return latest_file

#manually handles non-numeric values
def safe_to_numeric(column):
    try:
        return pd.to_numeric(column)
    except ValueError:
        return column  # Return the original column if conversion fails

#sanity check for hardcoded synonym/name lists (e.g. medication or condition
#name lists) used to search free-text columns like LEDTRT, CMTRT, MHTERM
def check_unmatched_terms(df, column, name_lists, case_insensitive=True):
    """
    For each synonym/name list, report any term that never appears as a
    substring anywhere in `column`.

    This is meant to be run right after defining a dict of
    {label: [term, term, ...]} used to search a free-text column (e.g.
    medication or condition name lists matched against LEDTRT, CMTRT, or
    MHTERM). It helps catch typos, terms that got silently merged by a
    missing comma in the list definition, and names that simply don't
    occur in this particular data extract.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the free-text column to search.
    column : str
        Name of the free-text column to search within (e.g. "LEDTRT").
    name_lists : dict
        Mapping of label -> list of terms, e.g. {"MAO-B": maob_names}.
    case_insensitive : bool, default True
        Whether to compare terms and column values case-insensitively.

    Notes
    -----
    This only reports terms with zero matches; it does not fix
    case-sensitivity bugs in the code that later performs the actual
    matching. Make sure matching code lowercases (or otherwise normalizes)
    both the column values and the terms being searched for.
    """
    values = df[column].dropna().astype(str)
    if case_insensitive:
        values = values.str.lower()

    any_unmatched = False
    for label, terms in name_lists.items():
        for term in terms:
            check_term = term.lower() if case_insensitive else term
            if not values.str.contains(check_term, regex=False).any():
                any_unmatched = True
                print(f"[{label}] '{term}' not found in any '{column}' value")

    if not any_unmatched:
        print(f"All terms in name_lists were found at least once in '{column}'.")
