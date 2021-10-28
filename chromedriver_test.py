#this needs some work. Check paths

from selenium import webdriver
#import sys


chromedriver = "chromedriver"
options = webdriver.ChromeOptions()
#prefs = {"download.default_directory" : TempDir1_path}
#options.add_experimental_option("prefs",prefs)
#options.add_argument('headless')
browser = webdriver.Chrome(executable_path=chromedriver, options=options) #DeprecationWarning: use options instead of chrome_options // browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
browser.get('http://www.caiso.com/TodaysOutlook/Pages/supply.aspx')
