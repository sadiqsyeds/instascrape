from flask import Flask, request, render_template, send_file
import instaloader
import os
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")
CORS(app)

def download_images_and_videos(username, download_path):
    # Create an instance of Instaloader
    loader = instaloader.Instaloader(
        download_videos=True,  # Enable video downloads
        download_video_thumbnails=False,  # Disable video thumbnails
        download_geotags=False,  # Exclude geotags
        save_metadata=False,  # Exclude metadata
        post_metadata_txt_pattern=""  # Do not include captions
    )

    try:
        print(f"Downloading images and videos from @{username}'s profile...")

        # Load the profile
        profile = instaloader.Profile.from_username(loader.context, username)

        # Loop through the posts in the profile
        for post in profile.get_posts():
            if post.is_video or post.typename == "GraphImage":
                loader.download_post(post, target=download_path)

        print(f"Download completed for @{username}! Check the folder.")
        return {"status": "success", "message": f"Download completed for @{username}.", "download_path": download_path}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/download', methods=['POST'])
def download():
    username = request.form.get('username')

    if not username:
        return {"status": "error", "message": "Username is required."}, 400

    download_path = os.path.join(os.getcwd(), f"downloads/{username}")
    os.makedirs(download_path, exist_ok=True)

    result = download_images_and_videos(username, download_path)
    if result['status'] == 'success':
        # Provide the download as a zip file
        zip_path = f"{download_path}.zip"
        os.system(f"zip -r {zip_path} {download_path}")
        return send_file(zip_path, as_attachment=True, download_name=f"{username}_content.zip")
    else:
        return result

if __name__ == "__main__":
    app.run(debug=False)
