from __future__ import print_function
import time
import sys                     # some prints
from datetime import datetime  # for tagging log with datetime
from . import google_ads       # interacting with Google ads and Ad Settings

# import re                        # time.sleep, re.split
# from selenium import webdriver   # for running the driver on websites
# from selenium.webdriver.common.keys import Keys    # to press keys on a webpage
# import browser_unit
# import google_search              # interacting with Google Search

from .browser_unit import strip_tags


class GoogleNewsUnit(google_ads.GoogleAdsUnit):

    def __init__(self, browser, log_file, unit_id, treatment_id, headless=False, proxy=None):

        google_ads.GoogleAdsUnit.__init__(
            self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy
        )

    def get_headlines(self):
        """Get headlines from Google News"""

        self.driver.set_page_load_timeout(60)
        self.driver.get("http://news.google.com")

        tim = str(datetime.now())

        self.print("Fetching headlines")
        topdivs = self.driver.find_elements_by_xpath("//article//h3")

        self.print("Articles in headlines: ", len(topdivs))

        if len(topdivs) == 0:
            raise Exception(
                "Could not find any news stories in the page. Formatting of Google News might have changed."
            )

        # sys.stdout.write(".")
        # sys.stdout.flush()

        for (i, div) in enumerate(topdivs):
            this_topdiv = div.find_element_by_xpath("./ancestor::article[1]")

            title = (this_topdiv
                     .find_element_by_xpath(".//h3//span")
                     .get_attribute('innerHTML'))

            ago = (this_topdiv
                   .find_element_by_css_selector("time")
                   .get_attribute("innerHTML"))

            agency = "unknown"
            try:
                agency = this_topdiv.find_element_by_xpath("div[2]//a").get_attribute("innerHTML")
            except Exception:
                pass

            agency = strip_tags(agency)

            heading = "Headlines"

            self.print("article %d/%d:" % (i+1, len(topdivs)), title, ago, agency)
            news = strip_tags(tim + "@|" + heading + "@|" + title + "@|" + agency + "@|" + ago)
            # .encode("utf8")

            self.log('measurement', 'news', news)

        self.print("Done getting top stories")

    def get_allbutsuggested(self):  # Slow execution
        raise Exception("This method is outdated and will not work with current google news.")

        """Get all news articles (except suggested stories) from Google News"""

        self.driver.set_page_load_timeout(60)
        self.driver.get("http://news.google.com")

        tim = str(datetime.now())

        divs = self.driver.find_elements_by_xpath(".//td[@class='lt-col']/div/div/div")
        topdivs = divs[1].find_elements_by_css_selector(
            "div.section-list-content div div.blended-wrapper.blended-wrapper-first.esc-wrapper"
        )  # warning: never used
        tds = self.driver.find_elements_by_xpath(".//td[@class='esc-layout-article-cell']")

        self.print("# articles: ", len(tds))
        # sys.stdout.write(".")
        # sys.stdout.flush()

        for td in tds:

            title = td.find_element_by_xpath(
                ".//div[@class='esc-lead-article-title-wrapper']/h2/a/span"
            ).get_attribute('innerHTML')

            tds1 = td.find_elements_by_xpath(
                ".//div[@class='esc-lead-article-source-wrapper']/table/tbody/tr/td"
            )
            agency = tds1[0].find_element_by_xpath(".//span").get_attribute("innerHTML")

            ago = tds1[1].find_element_by_xpath(
                ".//span[@class='al-attribution-timestamp']"
            ).get_attribute("innerHTML")
            # self.print(agency, ago)

            body = td.find_element_by_xpath(
                ".//div[@class='esc-lead-snippet-wrapper']"
            ).get_attribute('innerHTML')

            heading = "Top News"

            try:
                heading = td.find_element_by_xpath(
                    "../../../../../../../../../div[@class='section-header']/div/div/h2/a/span"
                ).get_attribute('innerHTML')
            except Exception:
                pass

            if "Suggested" in heading:
                self.print("Skipping Suggested news")
                continue

            # self.print("entering")
            news = strip_tags(
                tim+"@|"+heading+"@|"+title+"@|"+agency+"@|"+ago+"@|"+body
            ).encode("utf8")

            self.log('measurement', 'news', news)

    def get_news(self, type, reloads, delay):
        """Get news articles from Google"""

        rel = 0

        while rel <= reloads:  # number of reloads on sites to capture all news
            time.sleep(delay)

            try:
                s = datetime.now()

                if(type == 'headlines'):
                    self.get_headlines()

                elif(type == 'all'):
                    self.get_allbutsuggested()

                else:
                    input("No such news category found: %s!" % type)

                e = datetime.now()

                self.log('measurement', 'loadtime', str(e - s))

            except Exception as e:
                print(e)

                self.log('error', 'collecting', 'news')
                pass

            rel = rel + 1

    def read_articles(self, count=5, agency=None, keyword=None, category=None, time_on_site=20):
        """Click on articles from an agency, or having a certain keyword, or under a category"""

        self.driver.set_page_load_timeout(60)
        self.driver.get("http://news.google.com")
        tim = str(datetime.now()) # warning: not used

        i = 0
        for i in range(0, count):
            links = []
            if agency is not None:
                links.extend(self.driver.find_elements_by_xpath(
                        ".//div[@class='esc-lead-article-source-wrapper'][contains(.,'"+agency+"')]/.."
                ))

            if keyword is not None:
                links.extend(self.driver.find_elements_by_xpath(
                    ".//td[@class='esc-layout-article-cell'][contains(.,'"+keyword+"')]"
                ))

            if category is not None:
                header = self.driver.find_element_by_xpath(
                    ".//div[@class='section-header'][contains(.,'"+category+"')]"
                )
                links.extend(header.find_elements_by_xpath(
                    "../div/div/div/div/div/table/tbody/tr/td[@class='esc-layout-article-cell']")
                )

            if i == 0:
                self.print("# links found:", len(links))

            if i >= len(links):
                break

            links[i].find_element_by_xpath(
                "div[@class='esc-lead-article-title-wrapper']/h2/a/span"
            ).click()

            # sys.stdout.write(".")
            # sys.stdout.flush()

            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)

                if not(self.driver.title.strip() == "Google News"):
                    time.sleep(time_on_site)
                    site = self.driver.current_url
                    self.log('treatment', 'read news', site)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
