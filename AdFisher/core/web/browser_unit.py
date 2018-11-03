from __future__ import print_function
import time
import re                       # time.sleep, re.split
import sys                      # some prints
import os
import platform                 # for running  os, platform specific function calls
from selenium import webdriver  # for running the driver on websites
from datetime import datetime   # for tagging log with datetime

# from xvfbwrapper import Xvfb                 # for creating artificial display to run experiments
# from selenium.webdriver.common.proxy import *  # for proxy settings
from selenium.webdriver.common.proxy import Proxy, ProxyType
from html.parser import HTMLParser


CONFIGURED_FOR_HEADLESS = False
try:
    from xvfbwrapper import Xvfb

    if not Xvfb().xvfb_exists():
        raise Exception("xvfbwrapper installed but xvfb is not. Try 'sudo apt-get install xvfb'.")

    print("Headless testing using Xvfb available.")

    CONFIGURED_FOR_HEADLESS = True
except Exception:
    pass


CONFIGURED_FOR_HEADED = "DISPLAY" in os.environ

if not (CONFIGURED_FOR_HEADED or CONFIGURED_FOR_HEADLESS):
    raise Exception("Not configured for headed or headless. \n" +
                    "To run headless: install xvfb and python package xvfbwrapper .\n" +
                    "To run headed: run with gui and configure DISPLAY variable.")


class MLStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class FormException(Exception):

    def __init__(self, unit, site, msg):
        Exception.__init__(self, unit, msg)

        self.unit = unit
        self.site = site
        self.msg = msg

    def __str__(self):
        return ("The website %s did not contain the expected elements. It is likely that %s is outdated and needs to be updated to reflect changes in website formatting. %s" % (str(self.site), str(self.unit.__class__.__name__), str(self.msg)))


class BrowserUnit:
    def __init__(self, browser, log_file, unit_id, treatment_id, headless=False, proxy=None):

        self.headless = headless

        if headless:
            from xvfbwrapper import Xvfb

            self.vdisplay = Xvfb(width=1280, height=720)
            self.vdisplay.start()

            # if(not self.vdisplay.start()):
            #     fo = open(log_file, "a")
            #     fo.write(str(datetime.now())+"||"+'error'+"||"+'Xvfb failure'+"||"+'failed to start'+"||"+str(unit_id)+"||"+str(treatment_id) + '\n')
            #     fo.close()
            #     sys.exit(0)

        if proxy is not None:

            sproxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy,
                'ftpProxy': proxy,
                'sslProxy': proxy,
                'noProxy': ''  # set this value as desired
                })

        else:
            sproxy = Proxy({
                'proxyType': ProxyType.MANUAL
            })

        if browser == 'firefox':

            if platform.system() == 'Darwin':
                self.driver = webdriver.Firefox(proxy=sproxy)

            elif platform.system() == 'Linux':
                self.driver = webdriver.Firefox(proxy=sproxy)

            else:
                self.print("Unidentified Platform")
                sys.exit(0)

            # self.driver.implicitly_wait(20)

        elif browser == 'chrome':

            self.print("Expecting chromedriver at path specified in core/web/browser_unit")

            if platform.system() == 'Darwin':
                chromedriver = "../core/web/chromedriver/chromedriver_mac"

            elif platform.system() == 'Linux':
                chromedriver = "../core/web/chromedriver/chromedriver_linux"

            else:
                self.print("Unidentified Platform")
                sys.exit(0)

            os.environ["webdriver.chrome.driver"] = chromedriver
            chrome_option = webdriver.ChromeOptions()
            if proxy is not None:
                chrome_option.add_argument("--proxy-server="+proxy)
            self.driver = webdriver.Chrome(
                executable_path=chromedriver, chrome_options=chrome_option
            )

        else:
            self.print("Unsupported Browser")
            sys.exit(0)

        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.driver.set_page_load_timeout(40)
        self.accept_next_alert = True
        self.log_file = log_file
        self.unit_id = unit_id
        self.treatment_id = treatment_id

    def quit(self):
        if(self.headless):
            self.vdisplay.stop()

        self.driver.quit()

    def wait(self, seconds):
        time.sleep(seconds)

    def print(self, *kargs):
        print("unit %d (treatment %d):\t" % (self.unit_id, self.treatment_id), *kargs)

    def log(self, linetype, linename, msg):
        # linetype = ['treatment', 'measurement', 'event', 'error', 'meta']
        """Maintains a log of visitations"""
        fo = open(self.log_file, "a")
        fo.write(
            str(datetime.now()) + "||" + linetype + "||" + linename + "||" + str(msg) + "||" + \
            str(self.unit_id) + "||" + str(self.treatment_id) + '\n'
        )
        fo.close()

    def interpret_log_line(self, line):
        """Interprets a line of the log, and returns six components For lines containing
        meta-data, the unit_id and treatment_id is -1
        """
        chunks = re.split("\|\|", line)
        tim = chunks[0]
        linetype = chunks[1]
        linename = chunks[2]
        value = chunks[3].strip()
        if len(chunks) > 5:
            unit_id = chunks[4]
            treatment_id = chunks[5].strip()
        else:
            unit_id = -1
            treatment_id = -1
        return tim, linetype, linename, value, unit_id, treatment_id

    def wait_for_others(self):
        """Makes instance with SELF.UNIT_ID wait while others train"""

        fo = open(self.log_file, "r")
        line = fo.readline()
        tim, linetype, linename, value, unit_id, treatment_id = self.interpret_log_line(line)
        instances = int(value)
        fo.close()

        fo = open(self.log_file, "r")
        for line in fo:
            tim, linetype, linename, value, unit_id, treatment_id = self.interpret_log_line(line)
            if(linename == 'block_id start'):
                round = int(value)

#       print("round, instances: ", round, instances)

        fo.close()
        clear = False
        count = 0

        while(not clear):

            time.sleep(5)
            count += 1

            if(count > 500):
                self.log('event', 'wait_for_others timeout', 'breaking out')
                break

            c = [0]*instances
            curr_round = 0
            fo = open(self.log_file, "r")

            for line in fo:

                tim, linetype, linename, value, unit_id, treatment_id = \
                  self.interpret_log_line(line)

                if(linename == 'block_id start'):
                    curr_round = int(value)

                if(round == curr_round):

                    if value == 'training-start':
                        c[int(unit_id)-1] += 1

                    if value == 'training-end':
                        c[int(unit_id)-1] -= 1

            fo.close()
            clear = True

            for i in range(0, instances):
                if c[i] == 0:
                    clear = clear and True
                else:
                    clear = False

    def visit_sites(self, site_file, delay=5):
        """Visits all pages in site_file"""
        fo = open(site_file, "r")
        for line in fo:
            chunks = re.split("\|\|", line)
            site = "http://"+chunks[0].strip()
            self.print("heading over to: ", site)
            try:
                self.driver.set_page_load_timeout(40)
                self.driver.get(site)
                time.sleep(delay)
                self.log('treatment', 'visit website', site)

                # pref = get_ad_pref(self.driver)
                # self.log("pref"+"||"+str(treatment_id)+"||"+"@".join(pref), self.unit_id)

            except Exception:
                self.log('error', 'website timeout', site)

    def collect_sites_from_alexa(self, alexa_link, output_file="sites.txt", num_sites=5):
        """Collects sites from Alexa and stores them in file_name"""
        fo = open(output_file, "w")
        fo.close()
        self.driver.get(alexa_link)
        count = 0
        while(count < num_sites):
            els = self.driver.find_elements_by_css_selector(
                "li.site-listing div.desc-container p.desc-paragraph a"
            )
            for el in els:
                if(count < num_sites):
                    t = el.get_attribute('innerHTML').lower()
                    fo = open(output_file, "a")
                    fo.write(t + '\n')
                    fo.close()
                    count += 1
            self.driver.find_element_by_css_selector("a.next").click()

    def fail_format(self, e):
        raise FormException(unit=self,
                            site=self.driver.current_url,
                            msg=e)
