from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import pandas
from dotenv import load_dotenv

#load .env file
load_dotenv()
PATH = os.getenv("PATH")
#FOLDER_PATH is the path of the directory containing main.py
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
#adblocker/ublock extension path
PATH_TO_EXTENSION = os.path.join(FOLDER_PATH, "Adblocker", "cfhdojbkjhnklbpkdaibdccddilifddb", "1.59.0_11")
#ig downloader website ("https://snapinsta.app/")
DOWNLOADER = os.getenv("DOWNLOADER")
DOWNLOADS_PATH = os.path.join(FOLDER_PATH, "Downloads")

class Download_Post:
    def __init__(self):
        self.collected_posts = os.path.join(FOLDER_PATH, "collected_posts", "collected_posts.csv")
        self.collected_posts2 = os.path.join(FOLDER_PATH, "collected_posts", "collected_posts2.csv")
        #Load adblocker extension
        chrome_options = Options()
        chrome_options.add_argument('load-extension=' + PATH_TO_EXTENSION)
        prefs = {"download.default_directory": DOWNLOADS_PATH}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options = chrome_options)

        self.shuffle_csv()
        #self.check_downloaded_column()
        data = pandas.read_csv(self.collected_posts, index_col = 0)

        # Check if 'download_path' column exists; if not, create it with empty values
        if 'download_path' not in data.columns:
            data['download_path'] = ''

        total_downloaded = 0
        num_rows = len(data)
        for index, row in data.iterrows():
            print(f"Iterating over row {total_downloaded+1}/{num_rows}")
            if row['downloaded'] == 0:
                print(f"Post in row {index} was not downloaded. Downloading it...")
                self.download_post(row['url'])
                download = self.get_last_download()
                print(f"Downloaded file: {download}")
                data.at[index, 'downloaded'] = 1
                data.at[index, 'download_path'] = download
                #Updateing csv every step in case of crash
                data.to_csv(self.collected_posts, index=True)
            else:
                print(f"Post in row {index} already downloaded. Skipping download step...")
            total_downloaded += 1
        print(f"Download run finished. {total_downloaded} files downloaded. Info about these are now in collected_posts.csv")
        #copy dataframe to self.collected_posts2. if it's not on file, create the file
        data.to_csv(self.collected_posts2, index=True, header=not os.path.exists(self.collected_posts2))
        time.sleep(3)
        self.driver.quit()

    def shuffle_csv(self):
        df = pandas.read_csv(self.collected_posts)
        # Shuffle the DataFrame rows
        df = df.sample(frac=1).reset_index(drop=True)
        # Write the shuffled DataFrame back to a file
        df.to_csv(self.collected_posts, index=False)
        print(f"Shuffled file saved to {self.collected_posts}")

    def check_downloaded_column(self):
        df = pandas.read_csv(self.collected_posts)
        # Add new column to the DataFrame. This new column called "downlaoded" will be 1 if file was downlaoded already or 0 if it was not downloaded yet
        df["downloaded"] = [0] * len(df)  # Creates a column with 0 values for each row
        df.to_csv(self.collected_posts, index=False)

    def download_post(self, url):
        self.driver.get(DOWNLOADER)
        textbox = self.driver.find_element(By.NAME, "url")
        textbox.click()
        textbox.send_keys(url)
        textbox.send_keys(Keys.RETURN)
        time.sleep(10)
        #TODO instead of sleep, wait for element
        #try closing a pop-up from the download website("https://snapinsta.app/")
        try:
            self.driver.find_element(By.ID, 'close-modal').click()
        except:
            pass
        time.sleep(10)
        download = self.driver.find_element(By.CLASS_NAME, 'download-bottom')
        download.click()
        time.sleep(5)

    #GET LAST DOWNLOAD FILE USING SELENIUM
    def get_last_download(self):
        most_recent_file = None
        most_recent_time = 0

        # iterate over the files in the directory using os.scandir
        for entry in os.scandir(DOWNLOADS_PATH):
            if entry.is_file():
                # get the modification time of the file using entry.stat().st_mtime_ns
                mod_time = entry.stat().st_mtime_ns
                if mod_time > most_recent_time:
                    # update the most recent file and its modification time
                    most_recent_file = entry.name
                    most_recent_time = mod_time
        return most_recent_file
