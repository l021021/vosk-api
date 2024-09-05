from flask import Flask, request, render_template, redirect, url_for
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = "d:\\"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('reco.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return redirect(request.url)
    file = request.files['audio']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'recording.wav')
        file.save(file_path)
        return 'File saved successfully'
#

if __name__ == '__main__':
    app.run(debug=True)
