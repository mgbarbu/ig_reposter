from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import pickle
import os
import emoji
import pandas
from dotenv import load_dotenv

#load .env file
load_dotenv()
PATH = os.getenv("PATH")
#FOLDER_PATH is the path of the directory containing main.py
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
COLLECTED_POSTS = os.path.join(FOLDER_PATH, "collected_posts","collected_posts.txt")
COOKIES_PATH = os.getenv("COOKIES_PATH")
MY_IG_USER = os.getenv("MY_IG_USER")

class Pilot:
    def __init__(self, url):
        self.url = url
        print(f"Opening page: {self.url}")
        self.page_name = url.split("/")[-2]
        print(f"\n-----\nCurrent IG page: {self.page_name}")
        lastpost = self.page_name + "_lastpost.txt"
        self.lastposttxt = os.path.join(FOLDER_PATH, "igpages_lastpost" , lastpost)
        self.collected_posts = os.path.join(FOLDER_PATH, "collected_posts" , "collected_posts.csv")
        self.driver = webdriver.Chrome()
        self.all_url = []
        self.all_captions = []


    def load_cookies(self):
        cookies = pickle.load(open(COOKIES_PATH, "rb"))
        self.driver.get(self.url)
        time.sleep(3)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        print(f"Loaded cookies. Signed in as {MY_IG_USER}")
        time.sleep(5)

    def click_post(self):
        print("Clicking posts. Skipping first 3 posts (pinned posts)...")
        # Click post
        post_4 = self.driver.find_element(By.CLASS_NAME, "_aagw")
        #scroll element into view. Had bugs without this on some pages.
        self.driver.execute_script("arguments[0].scrollIntoView();", post_4)
        post_4.click()
        #buttons = self.driver.find_elements(By.CSS_SELECTOR,'.x1lliihq.x1n2onr6.xh8yej3.x4gyw5p.x1ntc13c.x9i3mqj.x11i5rnm.x2pgyrj')
        #buttons[0].click()

    def skip_pinned_posts(self):
        # # Skip first post
        # time.sleep(5)
        # nextbtn = self.driver.find_element(By.CLASS_NAME, "_abl-")
        # nextbtn.click()
        # # Skip second and third posts (usually pinned posts)
        # for _ in range(2):
        #     time.sleep(5)
        #     nextbtn = self.driver.find_elements(By.CLASS_NAME, "_abl-")
        #     nextbtn[1].click()
        # print("Skipped first 3 pinned post")

        #Skip to 4th post.
        print("Clicking 4th post. Skipping first 3 posts (pinned posts)...")
        # Click post
        post_4 = self.driver.find_elements(By.CLASS_NAME, "_aagw")[3]
        #scroll element into view. Had bugs without this on some pages.
        self.driver.execute_script("arguments[0].scrollIntoView();", post_4)
        time.sleep(3)
        post_4.click()

    def get_caption(self):
        if self.page_name == "gym.mentality_":
            caption = "💪"
            print("Current IG page is gym.mentality_. Replacing their caption with muscle emoji: 💪")
        else:
            try:
                # TODO check this in multiple situations.using split in case it's an ig account in description page example: https://www.instagram.com/p/C8kSfwcSjOp/
                caption = self.driver.find_element(By.XPATH, "//h1[@dir = 'auto']").get_attribute("innerHTML").split("<")[0]
                print(f"Current caption is: {caption}")
                if self.page_name == "gymmemesjokes":
                    split_lines = caption.split("\n")
                    caption = split_lines[0]
                    print(f"Current IG page is gym.gymmemesjokes. Splitting caption to {caption}")
            except:
                caption = "💪"
                print("Empty caption. Saving caption as muscle emoji: 💪")
        #DECODING EMOJI: Convert emoji to text describing emoji.
        caption = emoji.demojize(caption)
        return caption

    def get_datetime(self):
        """gets datetime in datetime.datetime format NOT str"""
        time_element = self.driver.find_elements(By.TAG_NAME, 'time')
        datetime_str = time_element[0].get_attribute('datetime')
        #print(f"Time posted: {datetime_str}")
        #Convert to datetime objects
        datetimedt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        #print(f"Time posted: {datetimedt}")
        return datetimedt

    def datetime2str(self, datetime):
        """converts datetime to str"""
        return datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def str2datetime(self, datetime_str):
        """converts str to datetime"""
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    def save_urls(self):
        ###Read file from disk with the last link saved in the last run###
        is_on_disk = os.path.isfile(self.lastposttxt)
        print(f"is_on_disk: {is_on_disk}")
        new_posts = 1
        datetime = self.get_datetime()
        # Storing first post date time, to later output it in lastpost.txt
        first_post_datetime = datetime
        if not is_on_disk:
            print("There is no txt file on disk. This page could have been added to the list of IG pages recently. Saving forth post datetime posted as last post's datetime for next run")
            get_url = self.driver.current_url
            print("The current URL is: " + str(get_url))
            caption = self.get_caption()
            self.all_url.append(get_url)
            self.all_captions.append(caption)
            nextbtn = self.driver.find_elements(By.CLASS_NAME, "_abl-")
            #TODO wait for button
            time.sleep(2)
            nextbtn[1].click()

        else:
            print(f"Reading txt file: {self.lastposttxt}")
            file = open(self.lastposttxt, "r")
            lastpostdatetime = self.str2datetime(file.read())
            print(f"Last URL saved in last run's DATETIME is: {lastpostdatetime}")

            ###Save URLs of new posts
            get_url = self.driver.current_url
            print(f"---\nChecking is new posts since last run")
            if datetime <= lastpostdatetime:
                print("No new posts since last run!")
                new_posts = 0
            else:
                print("New posts found. Going through posts...")
                newpost = True
                while newpost:
                    time.sleep(5)
                    get_url = self.driver.current_url
                    print("The current URL is: " + str(get_url))
                    caption = self.get_caption()
                    datetime = self.get_datetime()
                    print(f"\nComparing current post datetime with lastpostdatetime\n{datetime}\nvs\n{lastpostdatetime}")
                    if datetime <= lastpostdatetime:
                        newpost = False
                        print("Current post datetime smaller or equal than lastpostdatetime. Finishing up on this page...")
                    else:
                        print("Saving new post.\n")
                        self.all_url.append(get_url)
                        self.all_captions.append(caption)
                        nextbtn = self.driver.find_elements(By.CLASS_NAME, "_abl-")
                        nextbtn[1].click()

            file.close()


        if new_posts:
            print("Following URL links have been collected: ")
            for index, url in enumerate(self.all_url):
                print(f"url: {url}, caption: {self.all_captions[index]}")
            print("Writing collected_posts.csv on file")

            is_on_disk = os.path.isfile(self.collected_posts)
            print(f"collected_posts.csv file found on disk: {is_on_disk}")
            gathered_data_dict = {
                "page": self.page_name,
                "url": self.all_url,
                "caption": self.all_captions,
                "downloaded": 0
            }
            gathered_data_frame = pandas.DataFrame(gathered_data_dict)
            if is_on_disk:
                #Get last index, append and increment index
                data = pandas.read_csv(self.collected_posts, index_col=0)
                max_index = data.index.max()
                gathered_data_frame.index = range(max_index + 1, max_index + 1 + len(gathered_data_frame))
                gathered_data_frame.to_csv(self.collected_posts, mode="a", index=True, header=False)
            else:
                gathered_data_frame.to_csv(self.collected_posts)

            print(f"Saving first URL link's datetime posted on disk: {first_post_datetime}")
            # Overwrite lastpost txt file with the first link's datetime gathered from above
            with open(self.lastposttxt, "w") as file:
                file.write(self.datetime2str(first_post_datetime))
            time.sleep(1)
            self.driver.quit()
            time.sleep(1)
        else:
            time.sleep(1)
            self.driver.quit()
            time.sleep(1)
