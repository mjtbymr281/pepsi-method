import os
import subprocess
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Railway will look for the environment variable you set in the dashboard
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# --- HTML UI ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Pepsi's Method</title></head>
<body style="background:#0b0813; color:white; font-family:sans-serif; text-align:center; padding-top:50px;">
    <h1>Pepsi's Method</h1>
    <form method="post" enctype="multipart/form-data" action="/process">
        <input type="file" name="file" accept="video/*" required><br><br>
        <input type="text" name="discord_id" placeholder="Your Discord User ID" required><br><br>
        <button type="submit">Process Video</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_video():
    file = request.files['file']
    discord_id = request.form.get('discord_id')
    
    # Save the file to the temp directory
    input_path = f"/tmp/{file.filename}"
    output_path = f"/tmp/out_{file.filename}"
    file.save(input_path)
    
    # Run FFmpeg (This will work because you added it to the Aptfile!)
    cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", "scale=1920:1080", "-c:v", "libx264", output_path]
    subprocess.run(cmd)
    
    # Upload to file.io
    with open(output_path, 'rb') as f:
        r = requests.post('https://file.io/?expires=1d', files={'file': f})
        download_url = r.json().get('link')
    
    # Send to Discord
    requests.post(WEBHOOK_URL, json={"content": f"🔔 <@{discord_id}> Done! {download_url}"})
    
    return "<h3>Success! Check Discord.</h3>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
