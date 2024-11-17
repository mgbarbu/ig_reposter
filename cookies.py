from selenium import webdriver
import time
import os
import pickle
from dotenv import load_dotenv

#load .env file
load_dotenv()
PATH = os.getenv("PATH")
#FOLDER_PATH is the path of the directory containing main.py
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.getenv("COOKIES_PATH")

class Cookies:
    def __init__(self):
        pass
        self.driver = webdriver.Chrome()

    def save_cookies(self, url, sec):
        self.driver.get(url)
        time.sleep(sec)
        pickle.dump(self.driver.get_cookies(), open(COOKIES_PATH, "wb"))
        self.driver.quit()

    def load_cookies(self, url=None):
        cookies = pickle.load(open(COOKIES_PATH, "rb"))
        # driver.delete.all.cookies()
        # have to be on a page before you can add any cookies, any page- does not matter what
        # If you have stored the cookie from domain example.com, these stored cookies can't be pushed through the webdriver session to any other different domanin e.g. example.edu. The stored cookies can be used only within example.com. Further, to automatically login an user in future, you need to store the cookies only once, and that's when the user have logged in. Before adding back the cookies you need to browse to the same domain from where the cookies were collected.
        url = "https://google.com" if url is None else url
        self.driver.get(url)
        time.sleep(5)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        time.sleep(5)

    def delete_cookies(self, domain=None):
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if domain is not None:
                if str(cookie("domain")) in domain:
                    cookies.remove(cookies)
                else:
                    self.driver.delete_all_cookies()
                    return
        # deleting everything and adding the modified cookie object
        self.driver.delete_all_cookies()
        for cookie in cookies:
            self.driver.add_cookie(cookie)

