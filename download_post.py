import instaloader
import os
import glob
import pandas
from dotenv import load_dotenv


#load .env file
load_dotenv()
PATH = os.getenv("PATH")
#FOLDER_PATH is the path of the directory containing main.py
FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
DOWNLOADER = os.getenv("DOWNLOADER")
DOWNLOADS_PATH = os.path.join(FOLDER_PATH, "Downloads")

class Download_Post:
    def __init__(self):
        self.collected_posts = os.path.join(FOLDER_PATH, "collected_posts", "collected_posts.csv")
        self.collected_posts2 = os.path.join(FOLDER_PATH, "collected_posts", "collected_posts2.csv")
        #self.shuffle_csv()

        data = pandas.read_csv(self.collected_posts, index_col = 0)

        # Check if 'download_path' column exists; if not, create it with empty values
        if 'download_path' not in data.columns:
            data['download_path'] = ''

        total_downloaded = 0
        num_rows = len(data)
        for index, row in data.iterrows():
            print(f"\nIterating over row {total_downloaded+1}/{num_rows}")
            if row['downloaded'] == 0:
                print(f"Post in row {index} was not downloaded. Downloading it...")
                downloaded_files = self.download_post(row['url'])
                if downloaded_files:
                    print("Downloaded files:", downloaded_files)
                else:
                    print("No matching files found.")

                #print(f"Downloaded file: {download}")
                data.at[index, 'downloaded'] = len(downloaded_files)
                data.at[index, 'download_path'] = downloaded_files
                #Updateing csv every step in case of crash
                data.to_csv(self.collected_posts, index=True)
            else:
                print(f"Post in row {index} already downloaded. Skipping download step...")
            total_downloaded += 1
        print(f"\n-----\nDownload run finished. {total_downloaded} files downloaded. Info about these are now in collected_posts.csv")
        #copy dataframe to self.collected_posts2. if it's not on file, create the file
        data.to_csv(self.collected_posts2, index=True, header=not os.path.exists(self.collected_posts2))

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
        #Split url = "https://www.instagram.com/p/DGHXRrTxXUa/" to get DGHXRrTxXUa
        shortcodesplit = url.split("/")
        post_shortcode = shortcodesplit[4]
        print(f"URL: {url} and shortcode: {post_shortcode}")

        # Create an Instaloader instance
        L = instaloader.Instaloader(
            save_metadata=False,  # Skip metadata JSON
            download_pictures=True,  # Skip downloading images
            download_video_thumbnails=False,  # Skip video thumbnails
            download_geotags=False,  # Skip geotags
            post_metadata_txt_pattern=''  # Skip captions
        )

        # Set custom filename pattern
        L.filename_pattern = "{profile}_{date_utc}"

        # Custom download folder
        custom_download_folder = "Downloads"

        post = instaloader.Post.from_shortcode(L.context, post_shortcode)

        # Download the post. There is a print statement within this method. Cannot mute it. it will print "Downloads\post"
        L.download_post(post, target=custom_download_folder)

        # Construct filename pattern based on profile and UTC date
        filename_pattern = f"{post.owner_username}_{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}*"

        # Search for all matching files in the Downloads folder
        matching_files = glob.glob(os.path.join(custom_download_folder, filename_pattern))

        # Remove "Downloads/" from file paths
        return [os.path.basename(f) for f in matching_files] if matching_files else None
