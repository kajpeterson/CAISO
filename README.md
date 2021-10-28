# CAISO
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kajpeterson/CAISO/HEAD)

CAISO-scraper...something...automtrim.py is the latest version, which scrapes battery dispatch data from CAISO's Todays Outlook page.
See comment lines at beginning of code for instructions.
* creates CAISOcsv & Results directories in sys.path[0]
* handles data with blank timestamps
* checks for duplicates
* checks for wrong number of values in each date
* Downloads, sorts, concatenates

CAISO-scraper-imports.py is the imports data version.

