# requires the selenium chromedriver be installed
# https://chromedriver.chromium.org/downloads

# login info can be specified via argument or via key file formatted like so:
# for account @mybot

# {
#   "mybot" : {
#     "email" : "mybot@email.ru",
#     "pass"  : "ihateAPIs"
#   }
# }

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import os
import json
import pickle

class SeleniumSession:

    def __init__(self, user, driverpath="C:/Program Files (x86)/bin/chromedriver.exe", chromepath=None, headless=False):
        self.user = user
        self.driverpath = driverpath
        self.driver = None
        self.chromepath = chromepath
        self.headless = headless
        os.environ["webdriver.chrome.driver"] = driverpath


    def login(self, email=None, passw=None, keyfile="twitter.json"):
        options = Options()
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(service=webdriver.chrome.service.Service(executable_path=self.driverpath), options=options)
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()

        print("Opening twitter")
        self.driver.get("https://twitter.com")

        # you have to open the page before you can add the cookies
        try:
            print("Loading cookies")
            cookies = pickle.load(open(self.user + "_cookies.pkl", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except:
            print("Couldn't load cookies")

        # now refresh page
        self.driver.get("https://twitter.com/login")
        time.sleep(3) # wait for redirect

        if "home" in self.driver.current_url:
            print("Cookies worked! Skipping login")
            return

        if email is None or passw is None:
            with open(keyfile) as f:
                keys = json.load(f)
                if email is None:
                    email = keys[self.user]["email"]
                if passw is None:
                    passw = keys[self.user]["pass"]

        try:
            email_field = self.driver.find_element(By.NAME, "text")
        except NoSuchElementException:
            # no login page, that means our cookie worked
            print("Cookies worked! Skipping login")
            return

        email_field.clear()
        time.sleep(1)
        print("Typing email")
        email_field.send_keys(email)
        time.sleep(1)
        next_button = self.driver.find_element(By.XPATH, "//*[text()[contains(., 'Next')]]")
        print("Clicking next")
        next_button.click()
        time.sleep(1)

        # we may get a suspicious activity prompt
        # if so, we need to enter our username
        try:
            user_field = self.driver.find_element(By.NAME, "text")
            user_field.clear()
            time.sleep(1)
            user_field.send_keys(self.user)
            time.sleep(1)
            next_button = self.driver.find_element(By.XPATH, "//*[text()[contains(., 'Next')]]")
            next_button.click()
            time.sleep(1)
        except NoSuchElementException:
            pass

        password_field = self.driver.find_element(By.NAME, "password")
        password_field.clear()
        time.sleep(1)
        password_field.send_keys(passw)
        time.sleep(1)

        next_button = self.driver.find_element(By.XPATH, "//*[@data-testid='LoginForm_Login_Button']")
        next_button.click()
        time.sleep(5)
        # save cookies to a file so we can try to use them again when we restart
        try:
            print(str(self.driver.get_cookies()))
            pickle.dump(self.driver.get_cookies(), open(self.user + "_cookies.pkl", "wb"))
        except Exception as err:
            err.print
            # file is use probably?
            print("Couldn't save cookies")

    def get_latest_tweets(self, user):
        print("Looking for latest tweet from user", user)
        url = f"https://twitter.com/{user}/"

        index = 0
        tweetlinks = []

        self.driver.get(url)
        time.sleep(5)
        tweets = self.driver.find_elements(By.XPATH, "//*[@data-testid='tweet']")
        if tweets:
            tweets[-1].location_once_scrolled_into_view # try scroll down to force more tweets to load
        time.sleep(5)
        tweets = self.driver.find_elements(By.XPATH, "//*[@data-testid='tweet']")

        print(f"found {len(tweets)} tweets")
        if len(tweets) == 0:
            self.driver.save_screenshot("shot.png")
            return []

        for tweet in tweets:
            parent_testid = tweet.find_element(By.XPATH, "./..").get_attribute("data-testid")
            if parent_testid is not None and "placementTracking" in parent_testid:
                #print("skipping ad")
                continue
            for link in tweet.find_elements(By.TAG_NAME, "time"):
                timestamp = link.get_attribute("datetime")
                tweetlink = link.find_element(By.XPATH, "./..").get_attribute("href")
                if tweetlink is not None:
                    print(tweetlink)
                    tweetlinks.append((tweetlink, timestamp))


        tweetlinks.reverse() # reverse order so its chronological
        #print(tweetlinks)
        return list(dict.fromkeys(tweetlinks)) # remove duplicates
