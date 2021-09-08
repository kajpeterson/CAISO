# CAISO
CAISO-scraper-battery_2021.py is the latest version, which scrapes battery dispatch data from CAISO's Todays Outlook page.
See comment lines at beginning of code for instructions.
* creates CAISOcsv & Results directories in sys.path[0]
* handles data with blank timestamps
* checks for duplicates
* checks for wrong number of values in each date
* Downloads, sorts, concatenates

CAISO-scraper-imports.py is the imports data version.

