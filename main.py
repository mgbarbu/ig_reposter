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
        pilot.click_post()
        pilot.skip_pinned_posts()
        pilot.save_urls()

        print("Exiting page_pilot script on this page. Quitting chrome...")

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only show errors

#STEP1
#get_posts(PAGES)
#STEP2
#download_post = Download_Post()
#STEP3
#make_post = Make_Post()


#TODO
#There is a chance that last post was deleted? So it will keep going through all the posts. Make a limit in case of that? Or check the link first?? If still available run normally: https://www.instagram.com/p/DCRymJRMYM9/
#After last post of the day, run get_posts and download post
#What if I didn't get to post all the posts a day before. Adding more posts to csv will be fine, but I don't want to redownload everything... Create an exception for this in download_post
#Send me an email at the end of the day with the dictionary containing the url and caption (to double check if caption was taken correctly)
#How to approach a post of 2 pictures and music? https://www.instagram.com/p/C7zFTGaoD6X/?img_index=1 It has img_index in url so look into that
#What if the post was deleted? example: https://www.instagram.com/p/C9leWgvuzBk/ ?  and this could be the post saved as lastpost.txt