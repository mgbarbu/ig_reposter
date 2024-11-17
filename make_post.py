from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import pickle
import emoji
import pandas
import math
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
import os
import pyperclip
from dotenv import load_dotenv

#load .env file
load_dotenv()
PATH = os.getenv("PATH")
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
COLLECTED_POSTS = os.path.join(FOLDER_PATH, "collected_posts" , "collected_posts.txt")
COOKIES_PATH = os.getenv("COOKIES_PATH")
DOWNLOADS_PATH = os.path.join(FOLDER_PATH, "Downloads")
MY_IG_USER = os.getenv("MY_IG_USER")
#TIME_TO_POST = [9,13,17,19]
TIME_TO_POST = [11,14,22,23]
MINUTES_TO_SLEEP_FOR_UPLOAD = 3
POSTS_PER_DAY = len(TIME_TO_POST)

class Make_Post:
    def __init__(self):
        self.collected_posts = os.path.join(FOLDER_PATH, "collected_posts", "collected_posts.csv")
        self.data = pandas.read_csv(self.collected_posts)
        self.url = "https://www.instagram.com/"
        self.posts_total_count = self.data.shape[0]
        print(f"Total posts on collected_posts.csv: {self.posts_total_count}")

        self.driver = webdriver.Chrome()
        self.load_cookies()
        self.post_by_hour()

    def load_cookies(self):
        cookies = pickle.load(open(COOKIES_PATH, "rb"))
        self.driver.get(self.url)
        time.sleep(3)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        print(f"Loaded cookies. Signed in as {MY_IG_USER}")
        time.sleep(5)


    def post_by_hour(self):
        #I want the posting script to run 4 times a day, 9, 13, 17, 21. Total number of post gathered will be divided by 4.
        current_time = datetime.now()
        current_hour = int(current_time.strftime("%H"))
        print(f"current_hour: {current_hour}")
        posts_count = math.floor(self.posts_total_count/POSTS_PER_DAY)
        #TODO only post if downloaded is not 0!
        print("Checking if current hour is matching posting hour in list")
        for index, hour in enumerate(TIME_TO_POST):
            if current_hour == hour:
                print(f"Current hour {current_hour} is matching posting hour in list.")
                if index == len(TIME_TO_POST)-1:
                    print("Last hour in the list. Posting everything left...")
                    print(f"Script will attempt to make {self.posts_total_count} posts this run.")
                    rows = self.data.shape[0]
                    posts_count = rows
                else:
                    print(f"Script will attempt to make {posts_count} posts this run. Posts remaining for next runs: {self.posts_total_count-posts_count}")

                #get first n download_path and caption from csv file, where n is posts_count = the floor number of total posts/posts I want to make per day
                paths = self.data["download_path"].head(posts_count).tolist()
                caption_to_post = self.data["caption"].head(posts_count).tolist()

                for index,path in enumerate(paths):
                    file_path = os.path.join(DOWNLOADS_PATH, path)
                    print(f"Post {index+1}/{len(paths)}")
                    self.make_post(file_path,caption_to_post[index])

                #Sleep for n minutes for uploads to complete
                for i in range(MINUTES_TO_SLEEP_FOR_UPLOAD):
                    print(f"\nSleeping for {MINUTES_TO_SLEEP_FOR_UPLOAD-i} minutes for all uploads to complete...")
                    print(f"Don't close the terminal,csv file will be cleaned up and media will be removed from disk next.")
                    time.sleep(60)

                # Repeat loop to remove the files on disk.(assuming the uploads finished!!)
                for path in paths:
                    file_path = os.path.join(DOWNLOADS_PATH, path)
                    print("\nRemoving files on disk that have been uploaded: ")
                    self.remove_file(file_path)


                #Remove rows from csv file
                print("\nRemoving rows from csv file with info about uploaded posts...")
                data_modified = self.data.iloc[posts_count:]
                data_modified.to_csv(self.collected_posts, index=False)

                # Check if self.collected_posts (csv) has 0 rows. Delete both csv files if so
                print("\nChecking csv files and counting rows remaining...")
                self.remove_csv_files(self.collected_posts)
                self.driver.quit()

    def make_post(self,file_path,caption):
        #open new tab and switch to it
        # Open a new tab
        self.driver.execute_script("window.open('');")
        time.sleep(2)  # Optional: Add delay to visually confirm
        # Switch to the latest (new) tab
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # Open a URL in the new tab
        self.driver.get("https://www.instagram.com/")

        #GET CSS NAMES TO MAKE A POST AND STUFF
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, "[aria-label='New post']").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Post']").click()
        time.sleep(1)
        #self.driver.find_element(By.CLASS_NAME, " _acan _acap _acas _aj1- _ap30").click()
        self.driver.find_element(By.XPATH,'//button[@class=" _acan _acap _acas _aj1- _ap30"]').click()
        time.sleep(1)

        pyautogui.write(file_path, interval=0.0)
        time.sleep(0.5)  # Adjust if needed
        pyautogui.hotkey('enter')
        time.sleep(2)
        #May or may not show that "videos are reels now", in case it does show, this clicks OK
        try:
            self.driver.find_element(By.XPATH, '//button[@class=" _acan _acap _acaq _acas _acav _aj1- _ap30"]').click()
            #self.driver.find_element(By.CLASS_NAME, "._acan._acap._acaq._acas._acav._aj1-._ap30").click()
        except:
            pass
        self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Select crop']").click()
        time.sleep(2)
        #self.driver.find_element(By.XPATH, "//*[contains(text(), 'Original')]").click()
        self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Photo outline icon']").click()
        time.sleep(1)
        self.driver.find_element(By.CLASS_NAME, "_ac7b._ac7d").click()
        time.sleep(1)
        self.driver.find_element(By.CLASS_NAME, "_ac7b._ac7d").click()
        time.sleep(1)
        caption = emoji.emojize(caption)
        #print(caption)
        pyperclip.copy(caption)
        #self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Write a caption...']").send_keys(caption)
        input_field = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Write a caption...']")
        input_field.click()
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)
        # Clear the clipboard
        pyperclip.copy("")  # Set clipboard to empty string
        self.driver.find_element(By.CLASS_NAME, "_ac7b._ac7d").click()
        print(f"Making new post with caption: {caption}")
        print("\n")
        time.sleep(1)


    def remove_file(self,file_path):
        # Remove the file on disk
        try:
            os.remove(file_path)
            print(f"File {file_path} has been removed successfully.")
        except FileNotFoundError:
            print(f"File {file_path} does not exist.")
        except PermissionError:
            print(f"Permission denied: Cannot delete {file_path}.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def remove_csv_files(self,csv_file_path):
        # Check if the file exists and has 0 rows
        if os.path.exists(csv_file_path):
            df = pandas.read_csv(csv_file_path)
            if df.empty:
                os.remove(csv_file_path)
                print(f"{csv_file_path} is empty so file was removed successfully.")
            else:
                print(f"{csv_file_path} still has rows (more clips to post); Not removing csv file on this run.")
        else:
            print("File does not exist.")