import os
import stat
from datetime import datetime
from flask import Flask, flash, request, redirect, url_for, render_template, send_file, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
storage = 'storage'
app.secret_key = os.urandom(24)


def is_valid(filename):
    return '.' in filename and len(filename.rsplit('.', 1)[1]) > 0


@app.route('/')
def index():
    files = os.listdir(storage)
    return render_template("index.html", storage=storage, files=files, os=os, datetime=datetime, stat=stat)


@app.route('/view/<file>')
def view(file):
    return send_from_directory(storage, file)


@app.route('/download/<file>')
def download(file):
    return send_file(f'{storage}/{file}', as_attachment=True)


@app.route('/delete/<file>')
def delete(file):
    os.remove(f'{storage}/{file}')
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('files')
        counter = 0
        for file in files:
            if file.filename == '':
                flash('No selected file')
                continue
            if file and is_valid(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(storage, filename))
                counter += 1
        if counter > 0:
            return redirect(url_for('index'))
    return render_template('upload.html')


@app.route('/clipboard', methods=['GET', 'POST'])
def clipboard():
    if request.method == 'POST':
        with open('clipboard/text.txt', 'w', encoding='utf-8') as f:
            print(request.form['input'].split('\r'))
            f.writelines(request.form['input'].split('\r'))
        return redirect(request.url)
    with open('clipboard/text.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return render_template('clipboard.html', lines=lines)


@app.route('/clear')
def clear():
    with open('clipboard/text.txt', 'w', encoding='utf-8') as f:
        f.write('')
    return redirect(url_for('clipboard'))


os.makedirs('storage', exist_ok=True)
os.makedirs('clipboard', exist_ok=True)
if not os.path.exists('clipboard/text.txt'):
    with open('clipboard/text.txt', 'x') as f:
        f.close()
app.run(port=8888, host='0.0.0.0', debug=True)
