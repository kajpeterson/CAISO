#CAISO TODAY'S OUTLOOK BATTERY SCRAPER

print('\n\n')
#=================================================================================
#DOWNLOADS DAILY 5-MIN BATTERIES TREND DATA FOR A SPECIFIED DATE RANGE FROM CAISO'S "TODAY'S OUTLOOK" PAGE.
#SAVES TO path/CAISOcsv/Results, WHERE "path" IS THE DIRECTORY WHERE THIS FILE IS SAVED

#The following libraries must be installed:
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime
import os
import glob
import pandas as pd
import csv
import shutil
import time
import sys
import numpy as np

#Must have Chrome browser.
#Must have corresponding version of chromedriver installed here (or change path below):
chromedriver = '/usr/local/bin/chromedriver'

#INSTRUCTIONS:
#Open Terminal
#Set directory to the folder where the code is saved.
#Then enter command line with the following format (delineated by spaces):
#python3 filename(code) filename(results) startdate(mm dd yyyy) enddate(mm dd yyyy)

#example command line:
#cd /Volumes/KajHD/CPUC/GHG_impact_of_Utility-scale_Storage/CAISO
#python3 caiso-scraper-battery_2021.py battery_august2021.csv 08 01 2021 08 31 2021

#Some data cleanup will probably be required for example due to errors in CAISO's data.
#See error report in terminal for which dates need to be fixed.
#Some common errors:
    #Date has 289 values instead of 288.
        #Sometimes CAISO's data for a given date includes an extra value at the end, corresponding to the following day's first value.
        #This appears in the results file as 2 "0:00" values.
        #See "dates with missing or extra data" list returned in terminal.
        #Fix: Find the imposter value (probably a 0:00). If one of the 2 0:00 values matches the 0:00 value from the following date, delete that value.
        #If it's unclear which value is wrong, download the date's CSV manually from Today's Outlook (or just hover over the chart). That CSV will still be in the original order, so the imposter 0:00 value will appear at the end.
    #Duplication. If the code tries to download a date's data before it finishes loading, the previous date's data will be duplicated.
        #See "duplicate_data_log:" list returned in terminal
        #Fix: Download the duplicate date individually, or run code again for that range of dates. Replace duplicate data with newly downloaded data.

tic = time.time()
#=================================================================================
#INPUTS
filename = sys.argv[1]
startdate = datetime.date(int(sys.argv[4]),int(sys.argv[2]),int(sys.argv[3]))
enddate = datetime.date(int(sys.argv[7]),int(sys.argv[5]),int(sys.argv[6]))
date = startdate

#=================================================================================
#SETUP DIRECTORIES AND CHROMEDRIVER

#Make CAISOcsv & Results folders if they don't already exist
#Clear and make temporary directories for downloads and intermediary transposed csv's
#TempDir1 for downloads, TempDir2 for intermiediary transposed csv's, Results for final csv's:
path = sys.path[0]
CAISOcsv_path = f'{path}/CAISOcsv/'
Results_path = f'{path}/CAISOcsv/Results/'
TempDir1_path = f'{path}/CAISOcsv/TempDir1/'
TempDir2_path = f'{path}/CAISOcsv/TempDir2/'
combined_csv_path = f'{path}/CAISOcsv/TempDir2/combined_csv.csv'

try:
    os.mkdir(CAISOcsv_path)
    print("made new CAISOcsv folder")
except FileExistsError:
    pass

try:
    os.mkdir(Results_path)
    print("made new Results folder")
except FileExistsError:
    pass

try:
    os.mkdir(TempDir1_path)
except FileExistsError:
    try:
        shutil.rmtree(TempDir1_path)
        os.mkdir(TempDir1_path)
        print("made new TempDir1")
    except OSError as e:
        print("Error: %s : %s" %(TempDir1_path, e.strerror))

try:
    os.mkdir(TempDir2_path)
except FileExistsError:
    try:
        shutil.rmtree(TempDir2_path)
        os.mkdir(TempDir2_path)
        print("made new TempDir2")
    except OSError as e:
        print("Error: %s : %s" %(TempDir2_path, e.strerror))

#initiate chromedriver, set download directory to TempDir1, make headless, get CAISO page.

options = webdriver.ChromeOptions()
prefs = {"download.default_directory" : TempDir1_path}
options.add_experimental_option("prefs",prefs)
options.add_argument('headless')
browser = webdriver.Chrome(executable_path=chromedriver, options=options) #DeprecationWarning: use options instead of chrome_options // browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
browser.get('http://www.caiso.com/TodaysOutlook/Pages/supply.aspx')

#=================================================================================
#DOWNLOADER

#finds date input element
elements = browser.find_elements_by_tag_name('input')
for element in elements:
    if 'batteries-date' in element.get_attribute('class'):       
        
        #Enters date
        while date <= enddate:
            element.click()
            element.clear()
            date_input = (date.strftime("%m/%d/%Y"))
            element.send_keys(date_input)
            element.send_keys(Keys.ENTER)
            
            #Clicks download link
            button1 = browser.find_element_by_xpath('//*[@id="dropdownMenuBatteries"]')
            time.sleep(1.5)       #make sure it has time to load. Otherwise, there can be missing values or duplicates. I TRIED CHANGING 1.5 TO 2, BUT IT DIDN'T REDUCE DUPLICATES.
            button1.click()
            button2 = browser.find_element_by_xpath('//*[@id="downloadBatteriesCSV"]')
            
            #in case the browser is lagging, it will keep trying to click the link
            while True:
                try:
                    button2.click()
                    print("downloading", date_input)
                except:     #add specific exceptions?
                    time.sleep(0.5)
                    print("needed a nap")
                    continue
                break
            date = date + datetime.timedelta(1)

#kill invisiable headless browser
time.sleep(2)        #make sure the last date has time to download.
browser.close()

#=================================================================================
#FORMAT DAILY DATA

#grabbing csv's from TempDir1, transposing, stripping headings, adding date column
os.chdir(TempDir1_path)
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]            
print("{} files in all_filenames".format(len(all_filenames)))
print("formatting data...")
missing_data_log = []

for f in range(0,len(all_filenames)):
    data = pd.read_csv(TempDir1_path+all_filenames[f], header=None)
    date = (data[0][0])
    print("formatting", date)
    
    #transpose & strip headings
    df = data.T
    df = df.iloc[1:]
    date_column = [date]*len(df)
    
    #flag dates with missing data
    if len(df) != 288:
        print("warning: {} has {} elements".format(date,len(df)))
        missing_data_log.append(date)
    
    #add date column & save csv to TempDir2
    df.insert(0,"date", date_column,True)  
    df.to_csv(TempDir2_path+all_filenames[f])    

#=================================================================================
#CONCATENATOR+SORTER

os.chdir(TempDir2_path)
day_filenames = [i for i in glob.glob('*.{}'.format(extension))]

#combine all files in the list
print("concatenating...")
combined_csv = pd.concat([pd.read_csv(f) for f in day_filenames])
combined_csv.columns = ["Datetime", "Date", "Time", "Discharging"]

#create datetime object for sorting
print("combined_csv")
combined_csv.to_csv(TempDir2_path+'combined_csv.csv')
print("saved combined csv")

#Add datetime column
#I added Try/Except because one value in CAISO's import data was missing a timestamp, which caused an error when I tried to strip the time, but it was still able to make a datetime object without stripping.
print("adding datetime for sorting...")
df = pd.read_csv(combined_csv_path)    ###Untested###
df = df.drop('Unnamed: 0',axis=1)
date_error_counter = 0
time_error_counter = 0
for index,row in df.iterrows():
    try:
        DATE = df.loc[index,'Date'].strip()
    except Exception as e:
        date_message = str(e)
        print (f"Failed to strip Date for index: {index}, row: {row}. Error message: {date_message}")
        date_error_counter += 1
    try:
        TIME = df.loc[index,'Time'].strip()
    except Exception as e:
        time_message = str(e)
        print (f"Failed to strip Time for index: {index}, row: {row}. Error message: {time_message}")
        time_error_counter += 1
    df.loc[index,'Datetime'] = datetime.datetime.combine(datetime.datetime.strptime(DATE, '%m/%d/%Y') ,datetime.datetime.strptime(TIME,'%H:%M').time())
try:
    print (f"Failed to strip Date for {date_error_counter} rows. Error message: {date_message}")
except:
    pass
try:
    print (f"Failed to strip Time for {time_error_counter} rows. Error message: {time_message}")
except:
    pass

#sort by datetime
print("sorting")
final_df = df.sort_values(by='Datetime')

#=================================================================================
#REPORT + SAVE

#report missing data
print("-------------------------")
print("dates queried:", enddate - startdate + datetime.timedelta(1))
print("dates returned:", len(all_filenames))
print("Given dates returned:")
print("  values expected:", 288*len(all_filenames))
print("  values returned:", len(final_df))
print("dates with missing or extra data:", missing_data_log)
#print("dates with duplicate data:", duplicate_data_log)
print("-------------------------")

#save to Results folder
final_df.to_csv(Results_path+filename)
print("saved final csv")

#=================================================================================
#DUPLICATE CHECK

print("checking for duplicates...")
df = pd.read_csv(Results_path+filename)  ###Untested###
df['Date'] = df['Date'].str.strip()
df.set_index("Date", inplace=True)
df.head()
date = startdate
duplicate_data_log = []
previous = []
notfirstday = 0
while date <= enddate:
    date_input = (date.strftime("%m/%d/%Y"))
    elements = df.loc[[date_input],["Discharging"]]   ###Untested###
    if notfirstday == 0:
        pass
    elif np.array_equal(elements.values,previous.values):
        print("warning: {} is a duplicate of the previous date".format(date_input))
        duplicate_data_log.append(date_input)
    previous = elements
    date = date + datetime.timedelta(1)
    notfirstday = 1
print("duplicate_data_log:",duplicate_data_log)
toc = time.time()
print(toc-tic,'seconds elapsed')
print("DONE")

quit()
