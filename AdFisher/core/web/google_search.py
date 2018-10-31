from __future__ import print_function
import time
import sys                      # some prints
from datetime import datetime                    # for tagging log with datetime
from selenium.webdriver.common.keys import Keys  # to press keys on a webpage
from . import browser_unit
from .browser_unit import FormException, strip_tags


# import re                       # time.sleep, re.split
# from selenium import webdriver  # for running the driver on websites

# Google search page class declarations

GENDER_DIV = "EA yP"
INPUT_ID = "lst-ib"
INPUT_NAME = "q"
LI_CLASS = "g"

SIGNIN_A = "gb_70"


class GoogleSearchUnit(browser_unit.BrowserUnit):

    def __init__(self, browser, log_file, unit_id, treatment_id, headless=False, proxy=None):

        browser_unit.BrowserUnit.__init__(
            self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy
        )

    def search_and_collect(self, query_file, searchdelay=20, pages=2):

        s = 0  # PM: guessed that it starts at 0; was undefined before
        fo = open(query_file, "r")

        for line in fo:     # For all queries in the list, obtain search results on Google
            q = line.strip()
            page = 1
            self.print("search query: ", q)
            try:
                self.driver.get("http://www.google.com/")

                time.sleep(1)

                query_box = self.driver.find_element_by_id(INPUT_ID)
                query_box.clear()
                query_box.send_keys(q)
                query_box.send_keys(Keys.RETURN)

                time.sleep(1)

                self.log('treatment', 'google search', q)

            except Exception as e:
                self.log('error', 'google search', q)
                self.driver.save_screenshot(str(self.unit_id) + '_search' + str(s) + '.jpg')
                s += 1

                raise FormException(unit=self, site="http://www.google.com/", msg=e)

            while page <= pages:

                tim = str(datetime.now())
                results = self.driver.find_elements_by_css_selector("div.g div.rc")
                self.print("num results: ", len(results))

                for result in results:

                    t = result.find_element_by_css_selector("h3 a").get_attribute('innerHTML')

                    l = (result
                             .find_element_by_css_selector("div.s div div cite")
                             .get_attribute('innerHTML'))

                    b = (result
                             .find_element_by_css_selector("div.s div span.st")
                             .get_attribute('innerHTML'))

                    r = strip_tags(tim+"@|"+t+"@|"+l+"@|"+b).encode("utf8")

                    self.log('measurement', 'search_result', r)

                self.driver.find_element_by_id("pnnext").click()

                time.sleep(1)

                page += 1

            time.sleep(searchdelay)

        fo.close()

    def search_and_click(self, query_file, clickdelay=20, clickcount=5):

        fo = open(query_file, "r")

        for line in fo:     # For all queries in the list, obtain search results on Google
            s = 0
            r = 0
            q = line.strip()

            self.print("search query: ", q)

            try:
                self.driver.get("http://www.google.com/")

                time.sleep(1)

                input_box = self.driver.find_element_by_name(INPUT_NAME)

                input_box.clear()
                input_box.send_keys(q)
                input_box.send_keys(Keys.RETURN)

                self.log('treatment', 'google search', q)

            except Exception as e:
                self.print(e)

                self.log('error', 'google search', q)
                self.driver.save_screenshot(str(self.unit_id)+'_search'+str(s)+'.jpg')
                s += 1

            for y in range(0, clickcount):  # How many search results to visit

                try:

                    results = self.driver.find_elements_by_css_selector("a h3")
                    if y == 0:
                        self.print("num results: ", len(results))

                    if len(results) == 0:
                        self.print("Could not find any google search results to follow.")
                        raise Exception("no links found to visit")

                    results[y].click()

                    time.sleep(1)

                    self.print("visited (%d/%d): " % (y+1, clickcount), self.driver.current_url)

                    link = self.driver.current_url

                    self.driver.back()
                    self.log('treatment', 'visit page', link)

                    # sys.stdout.write(".")
                    # sys.stdout.flush()

                    r += 1
                    s = r + 0

                except Exception as e:
                    self.print(e)

                    self.log('error', 'visiting', 'google searchresults')
                    s += 1

                time.sleep(clickdelay)

        fo.close()
