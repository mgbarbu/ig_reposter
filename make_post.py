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
from dotenv import load_dotenv
import ast
import ffmpeg
import pyperclip
import numpy as np

#load .env file
load_dotenv()
PATH = os.getenv("PATH")
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
COLLECTED_POSTS = os.path.join(FOLDER_PATH, "collected_posts" , "collected_posts.txt")
COOKIES_PATH = os.getenv("COOKIES_PATH")
DOWNLOADS_PATH = os.path.join(FOLDER_PATH, "Downloads")
MY_IG_USER = os.getenv("MY_IG_USER")
#TIME_TO_POST = [9,13,17,19]
#TIME_TO_POST = [9,10,12,19,20,21,22]
MIN_HOUR = 10
MAX_HOUR = 21
TIME_TO_POST = list(range(MAX_HOUR,MIN_HOUR-1,-1)) #hours from 21:00 to 10:00 reverse order
MINUTES_TO_SLEEP_FOR_UPLOAD = 2
POSTS_PER_DAY = len(TIME_TO_POST)

class Make_Post:
    def __init__(self):
        self.collected_posts = os.path.join(FOLDER_PATH, "collected_posts", "collected_posts.csv")
        self.collected_posts2 = os.path.join(FOLDER_PATH, "collected_posts", "collected_posts2.csv")
        self.data = pandas.read_csv(self.collected_posts)
        self.data2 = pandas.read_csv(self.collected_posts2)
        self.url = "https://www.instagram.com/"
        self.posts_total_count = self.data2.shape[0]
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

    def distribute_posts(self):
        num_slots = len(TIME_TO_POST)
        num_posts = self.posts_total_count

        schedule = {hour: 0 for hour in TIME_TO_POST}  # Initialize all slots with 0 posts

        if num_posts <= num_slots:
            times = np.linspace(21, 10, num_posts, dtype=int).tolist()
            for hour in times:
                schedule[hour] += 1
        else:
            base_posts = num_posts // num_slots  # Min posts per slot
            extra_posts = num_posts % num_slots  # Leftover posts

            for hour in TIME_TO_POST:
                schedule[hour] = base_posts  # Assign base posts
                if extra_posts > 0:
                    schedule[hour] += 1  # Distribute extra posts
                    extra_posts -= 1

        return {k: v for k, v in schedule.items() if v > 0}  # Remove empty hours//is a dictionary comprehension that filters out hours with 0 posts.


    def post_by_hour(self):
        #I want the posting script to run 4 times a day, 9, 13, 17, 21. Total number of post gathered will be divided by 4.
        current_time = datetime.now()
        current_hour = int(current_time.strftime("%H"))
        print(f"current_hour: {current_hour}")

        # #TODO only post if downloaded is not 0!
        # print("Checking if current hour is matching posting hour in list")
        # for index, hour in enumerate(TIME_TO_POST):
        #     if current_hour == hour:
        #         print(f"Current hour {current_hour} is matching posting hour in list.")
        #
        #         # NUMBER OF POSTS TO BE MADE
        #         posts_count = math.floor(self.posts_total_count / len(TIME_TO_POST))
        #         # all NaN values rows in the 'download_path' column
        #         nan_count = self.data['download_path'].isna().sum()
        #         #TODO Test this is statement
        #         if posts_count > (self.posts_total_count - nan_count):
        #             print(
        #                 f"There are {self.posts_total_count} posts that can be made, but {nan_count} are missing download path.\nThis run should have made {posts_count} posts, but will not try to make {self.posts_total_count - nan_count}")
        #             posts_count = nan_count
        #
        #         if index == len(TIME_TO_POST)-1:
        #             rows = self.data.shape[0]
        #             posts_count = rows
        #             print("Last hour in the list. Posting everything left...")
        #             print(f"Script will attempt to make {posts_count} posts this run.\n")
        #             #Last run so delete collected_posts2
        #             if os.path.exists(self.collected_posts2):
        #                 os.remove(self.collected_posts2)
        #                 print(f"{self.collected_posts2} was removed successfully.")
        #             else:
        #                 print(f"Tried to remove {self.collected_posts2} but file does not exist")
        #         else:
        #             print(f"Script will attempt to make {posts_count} posts this run. Posts remaining for next runs: {self.posts_total_count-(posts_count*(TIME_TO_POST.index(current_hour)+1))}\n")

        schedule = self.distribute_posts()
        print("----------------------------")
        print(schedule)

        if current_hour in schedule:
            posts_count = schedule[current_hour]

            filtered_data = self.data.head(posts_count).dropna(subset=["download_path"])
            if len(filtered_data)<posts_count:
                must_reshuffle = 1
                print(f"{posts_count} posts should be made, but {posts_count-len(filtered_data)} are missing download path. Script will attempt to make {len(filtered_data)} posts this run")
            else:
                must_reshuffle = 0

            #Iterate over the filtered data
            cur_count = 0
            for index, row in filtered_data.iterrows():
                cur_count+=1
                #file_path = os.path.join(DOWNLOADS_PATH, row['download_path'])
                post_list = self.ensure_list(row['download_path'])
                paste_path = ""
                #TODO try to post long video, if not then crop video to 59 sec?
                for slide in post_list:
                    #file_path = os.path.join(DOWNLOADS_PATH, slide)
                    #if it's mp4 (video) and not jpg -> trim video if >=60 secs to 59 seconds.
                    #if file_path[-1] == "4" :
                    #    clip_duration = self.get_video_duration(file_path)
                    #    if clip_duration >= 60:
                    #        self.trim_video(file_path, clip_duration)

                    paste_path += '"' + slide + '" '
                print(f"Post {cur_count}/{len(filtered_data)}")
                print(paste_path)
                successful_post = self.make_post(paste_path, row['caption'])

                #If post was not made (because download file on disk couldn't be found), add the row to the bottom of the csv file and remove the downloaded info. So that it will be downloaded again next run
                if not successful_post:
                    print("successful_post FALSE")
                    for slide in post_list:
                        file_path = os.path.join(DOWNLOADS_PATH, slide)
                        # if it's NOT mp4 (video) \skip trimming attempt.
                        if file_path[-1] != "4":
                            print("Post was not mp4. Skipping trim attempt")
                        else:
                            print("Attempting to trim videos to 59 seconds")
                            #Try to trim videos to 59 seconds, assuming post was not successful because of video length
                            try:
                                for slide in post_list:
                                    file_path = os.path.join(DOWNLOADS_PATH, slide)
                                    #if it's mp4 (video) and not jpg -> trim video if >=60 secs to 59 seconds.
                                    if file_path[-1] == "4" :
                                        clip_duration = self.get_video_duration(file_path)
                                        if clip_duration >= 60:
                                            self.trim_video(file_path, clip_duration)
                                    #No need to redo paste_path. Use the one before, as trimming version will overwrite the one before
                                    #paste_path += '"' + slide + '" '
                                print("Trim successful.")
                                print(f"Post {cur_count}/{len(filtered_data)}")
                                print(paste_path)
                                successful_post = self.make_post(paste_path, row['caption'])
                            except:
                                print("Trimming failed. Post unsuccessful for another reason. Possible that file was not found on disk.")
                            #If post still unsuccessful even after trim attempt
                            if not successful_post:
                                new_row = row.copy()
                                new_row['download_path'] = ""
                                new_row['downloaded'] = 0
                                self.data = pandas.concat([self.data, pandas.DataFrame([new_row])], ignore_index=True)
                                print("Row added at the end of the csv file, with an empty 'download_path' and 'downloaded' reset to 0. Next download run will redownload the post.\n")

            #Sleep for n minutes for uploads to complete
            for i in range(MINUTES_TO_SLEEP_FOR_UPLOAD):
                print(f"\nSleeping for {MINUTES_TO_SLEEP_FOR_UPLOAD-i} minutes for all uploads to complete...")
                print(f"Don't close the terminal,csv file will be cleaned up and media will be removed from disk next.")
                time.sleep(60)

            #Repeat loop to remove the files on disk.(assuming the uploads finished!!)
            for index, row in filtered_data.iterrows():
                #file_path = os.path.join(DOWNLOADS_PATH, row['download_path'])
                print("\nRemoving file on disk that has been uploaded: ")
                self.remove_file(row['download_path'])
                # Remove rows from csv file
                print("Removing row from csv file with info about uploaded post...")
                data_modified = self.data.iloc[1:]
                data_modified.to_csv(self.collected_posts, index=False)
                self.data = pandas.read_csv(self.collected_posts)
                print(f"Row removed, {self.data.shape[0]} rows remaining.")

            # Check if self.collected_posts (csv) has 0 rows. Delete both csv files if so
            print("\nChecking csv files and counting rows remaining...")
            self.remove_csv_files(self.collected_posts)
            #TODO So we remove the files and then reshuffle? change this reshuffle with adding the one empty line to the end of csv file
            if must_reshuffle == 1:
                print("Shuffling csv file because of rows with no download path...")
                self.shuffle_csv()
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

        #How many posts/slides are in this post?
        slides = file_path.split()
        slides_count = len(slides)
        if slides_count > 1:
            print(f"This post has {slides_count} slides")
        else:
            print(f"This post has {slides_count} slide")
        #Try finding the file on disk and posting.
        try:
            #First go to folder C:\Users\Mihai\Documents\GitHub\ig_reposter\Downloads\
            pyautogui.write(DOWNLOADS_PATH, interval=0.0)
            time.sleep(0.5)  # Adjust if needed
            pyautogui.hotkey('enter')
            time.sleep(1)

            #loop through all slides/posts
            for i in range(slides_count):
                print(f"Slide {i+1}/{slides_count}")
                pyautogui.write(slides[i], interval=0.0)
                time.sleep(0.5)  # Adjust if needed
                pyautogui.hotkey('enter')
                time.sleep(2)
                #if single post, break
                if slides_count==1:
                    break
                else:
                    #only open media gallery first time. It's kept open after
                    if i == 0:
                        element = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label="Open media gallery"]')
                        element[0].click()
                    #skip last post because it was already posted?
                    if i < slides_count-1:
                        element = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label="Plus icon"]')
                        self.driver.execute_script("arguments[0].scrollIntoView();", element[0])
                        element[0].click()
                        time.sleep(1)
                    else:
                        break

            #May or may not show that "videos are reels now", in case it does show, this clicks OK
            try:
                self.driver.find_element(By.XPATH, '//button[@class=" _acan _acap _acaq _acas _acav _aj1- _ap30"]').click()
                #self.driver.find_element(By.CLASS_NAME, "._acan._acap._acaq._acas._acav._aj1-._ap30").click()
            except:
                pass
            button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Select crop']")
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
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
            return True
        except:
            pyautogui.hotkey('esc')
            pyautogui.hotkey('esc')
            print("File not found on disk. Skipping posting step.")
            return False



    def remove_file(self,file_name):
        # Remove the file on disk
        file_name = self.ensure_list(file_name)
        for slide in file_name:
            file_path = os.path.join(DOWNLOADS_PATH, slide)
            try:
                os.remove(file_path)
                print(f"File {file_path} has been removed successfully.")
            except FileNotFoundError:
                print(f"File {file_path} does not exist.")
            except PermissionError:
                print(f"Permission denied: Cannot delete {file_path}.")
            except Exception as e:
                print(f"An error occurred: {e}")

    def remove_csv_files(self,posts_path):
        # Check if the file exists and has 0 rows
        if os.path.exists(posts_path):
            df = pandas.read_csv(posts_path)
            if df.empty:
                os.remove(posts_path)
                print(f"{posts_path} is empty so file was removed successfully.")
            else:
                print(f"{posts_path} still has rows (more clips to post); Not removing csv file on this run.")
        else:
            print("File does not exist.")


    def shuffle_csv(self):
        df = pandas.read_csv(self.collected_posts)
        # Shuffle the DataFrame rows
        df = df.sample(frac=1).reset_index(drop=True)
        # Write the shuffled DataFrame back to a file
        df.to_csv(self.collected_posts, index=False)
        print(f"Shuffled file saved to {self.collected_posts}")

    import ast

    def ensure_list(self,value):
        """Ensures value is a proper list, converting if needed."""
        if isinstance(value, str):
            # If it's a string that looks like a list, convert it
            try:
                parsed_value = ast.literal_eval(value)
                if isinstance(parsed_value, list):  # Ensure it's a list
                    return parsed_value
            except (SyntaxError, ValueError):
                pass
            return [value]  # If conversion fails, wrap it in a list

        return value if isinstance(value, list) else [value]  # Ensure it's always a list


    def get_video_duration(self,video_path):
        """Returns the duration of a video in seconds."""
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            print(f"Error getting duration: {e}")
            return None

    def trim_video(self, input_path, duration, trim_duration=59):
        """Trims the video in-place if it's 60 seconds or longer."""
        if duration and duration >= 60:
            temp_path = input_path + "_trimmed.mp4"  # Create a temp file
            print(f"Trimming video to {trim_duration} seconds...")

            # Trim and save as a temp file
            try:
                # Run the trimming command
                ffmpeg.input(input_path).output(temp_path, t=trim_duration).run(overwrite_output=True)

                # Wait for the temp file to be created
                while not os.path.exists(temp_path):
                    print("Waiting for video to be trimmed...")
                    time.sleep(3)  # Check every 3 seconds for the temp file

                # Once the temp file is created, replace the original file
                os.replace(temp_path, input_path)
                print(f"Trimmed video saved as: {input_path}")

            except Exception as e:
                print(f"Error trimming video: {e}")
        else:
            print("Video is already less than 60 seconds, no trimming needed.")
