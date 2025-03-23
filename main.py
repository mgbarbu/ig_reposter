import time
from cookies import Cookies
from page_pilot import Pilot
from download_post import Download_Post
from make_post import Make_Post
from dotenv import load_dotenv
import os

#load .env file
load_dotenv()
PATH = os.getenv("PATH")
COOKIES_PATH = os.getenv("COOKIES_PATH")
with open("pages_to_repost_from.txt", "r") as file:
    PAGES = [line.strip() for line in file if line.strip() and not line.startswith("#")]


#----------------------------------------------------------------------------------------
#STEP1: Initialising cookies class. Saving and loading cookies that contain login info.
#cookies = Cookies()
#Initial load of the domain that we want to save cookies for. Arguments are URL and seconds on the page for login. After that cookies will be saved in COOKIES_PATH from cookies.py
#cookies.save_cookies("https://www.instagram.com", 60)

#Test if the saved cookies worked.
#cookies.load_cookies("https://www.instagram.com")
#----------------------------------------------------------------------------------------


#STEP2 get posts, download and repost.
def get_posts(ig_pages):
    for page in ig_pages:
        pilot = Pilot(page)
        pilot.load_cookies()
        print("Cookies loaded successfully. Signed in.")
        #pilot.click_post()
        pilot.skip_pinned_posts()
        pilot.save_urls()

        print("Exiting page_pilot script on this page. Quitting chrome...")

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only show errors

#STEP1
#get_posts(PAGES)
#STEP2
#download_post = Download_Post()
#STEP 3
make_post = Make_Post()



#TODO
#Post in row 22 was not downloaded. Downloading it...
#Downloaded file: Snapinsta.app_467398041_3912144995722175_8844759426286239304_n_1080.jpg
#C:\Users\Mihai\Documents\GitHub\ig_reposter\download_post.py:50: FutureWarning: Setting an item of incompatible dtype is deprecated and will raise an error in a future version of pandas. Value 'Snapinsta.app_467398041_3912144995722175_8844759426286239304_n_1080.jpg' has dtype incompatible with float64, please explicitly cast to a compatible dtype first.
#  data.at[index, 'download_path'] = download
#Iterating over row 3/19

#TODO NEW WITH INSTA LOADER
#Music when page pilot? song for pictureS?
#Skip pinned posts by datetime?

#Wait until page says your reel has been shared? and then open new tab for new post?
#What if download link is no longer valid? If file was missing from disk and it will be redownloaded but then the post was deleted? How will the download script react and should we clean the whole row?
#What if last saved post has multiple posts: 24,gym.meme.nation,https://www.instagram.com/p/DG1BHgHRJPI/?img_index=1,Gym fixes everything :flexed_biceps:,8,"['gym.meme.nation_2025-03-05_18-52-34_1.jpg', 'gym.meme.nation_2025-03-05_18-52-34_2.jpg', 'gym.meme.nation_2025-03-05_18-52-34_3.jpg', 'gym.meme.nation_2025-03-05_18-52-34_4.jpg', 'gym.meme.nation_2025-03-05_18-52-34_5.jpg', 'gym.meme.nation_2025-03-05_18-52-34_6.jpg', 'gym.meme.nation_2025-03-05_18-52-34_7.jpg', 'gym.meme.nation_2025-03-05_18-52-34_8.jpg']"


#"C:\Users\Mihai\Documents\GitHub\ig_reposter\Downloads\bigdfit_era_2025-03-03_12-58-34_1.mp4" "C:\Users\Mihai\Documents\GitHub\ig_reposter\Downloads\bigdfit_era_2025-03-03_12-58-34_2.mp4"
#File not found on disk. Skipping posting step.
#successful_post FALSE
#Row added at the end of the csv file, with an empty 'download_path' and 'downloaded' reset to 0.
#DACA CLIPURILE SUNT PREA LUNGI ZICE SUCCESSUL POST FALSE SI MAI DOWNLOADEAZA O DATA DATA VIITOARE> DISABLE THIS

#rethink reshuffle logic
#need to get date posted instead of last post in case post is deleted
#what is pinned posts are deleted? then last post will be 2nd for example and it will be skipped to 4th and go on infinite
#should i still move the nan empty download_path to end ain download_post?
#mute sound when posting and then unmute? or mute chrome
#instead of time.sleep() waitforelement or try: especially in download_post.py. could save a lot of time
#In make_post instead of reshuffle, add post to bottom
#There is a chance when the post is downloaded, and the path is saved, that the post was not downloaded yet, and the last path saved is the one of the previous post? Should we still wait a few seconds or rather get all items in that folder after all downloads were made and sort chronologically? If it crashes, process would have to be restarted this way
#There is a chance that last post was deleted? So it will keep going through all the posts. Make a limit in case of that? Or check the link first?? If still available run normally: https://www.instagram.com/p/DCRymJRMYM9/
#After last post of the day, run get_posts and download post
#What if I didn't get to post all the posts a day before. Adding more posts to csv will be fine, but I don't want to redownload everything... Create an exception for this in download_post
#Send me an email at the end of the day with the dictionary containing the url and caption (to double check if caption was taken correctly)
#How to approach a post of 2 pictures and music? https://www.instagram.com/p/C7zFTGaoD6X/?img_index=1 It has img_index in url so look into that
#What if the post was deleted? example: https://www.instagram.com/p/C9leWgvuzBk/ ?  and this could be the post saved as lastpost.txt
#CHeck this post: 9,memeslibrary.official,https://www.instagram.com/p/DC5U2A1zvRJ/   it has a hastag as caption, but I think i removed the caption so there is no caption to be posted. this errors, at the post where I paster the caption a pop up windows appears asking if I want to discard my changes