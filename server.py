import os
import stat
from datetime import datetime
import zipfile
from flask import Flask, flash, request, redirect, url_for, render_template, send_file, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)
storage_path = 'storage'
clipboard_path = 'clipboard/text.txt'
clipboard_dir = clipboard_path.rsplit('/', 1)[0]
package_path = 'package/files.zip'
package_dir = package_path.rsplit('/', 1)[0]


def is_valid(filename):
    return '.' in filename and len(filename.rsplit('.', 1)[1]) > 0


@app.route('/')
def index():
    files = os.listdir(storage_path)
    return render_template("index.html", storage=storage_path, files=files, os=os, datetime=datetime, stat=stat)


@app.route('/view/<file>')
def view(file):
    return send_from_directory(storage_path, file)


@app.route('/download/<file>')
def download(file):
    return send_file(f'{storage_path}/{file}', as_attachment=True)


@app.route('/download_all')
def download_all():
    if os.path.exists(package_path):
        os.remove(package_path)
    with zipfile.ZipFile(package_path, 'w') as z:
        for file in os.listdir(storage_path):
            z.write(f'{storage_path}/{file}', file)
    return send_file(package_path, as_attachment=True)


@app.route('/delete/<file>')
def delete(file):
    os.remove(f'{storage_path}/{file}')
    return redirect(url_for('index'))


@app.route('/delete_all')
def delete_all():
    for file in os.listdir(storage_path):
        os.remove(f'{storage_path}/{file}')
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
                file.save(os.path.join(storage_path, filename))
                counter += 1
        if counter > 0:
            return redirect(url_for('index'))
    return render_template('upload.html')


@app.route('/clipboard', methods=['GET', 'POST'])
def clipboard():
    if request.method == 'POST':
        input = request.form['input'].strip()
        if input != '':
            strList = input.split('\r')
            strList.insert(0, '\n')
            with open(clipboard_path, 'a', encoding='utf-8') as f:
                f.writelines(strList)
        return redirect(request.url)
    with open(clipboard_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) > 0:
            lines.remove('\n')
    return render_template('clipboard.html', lines=lines)


@app.route('/clear')
def clear():
    with open(clipboard_path, 'w', encoding='utf-8') as f:
        f.write('')
    return redirect(url_for('clipboard'))


os.makedirs(storage_path, exist_ok=True)
os.makedirs(clipboard_dir, exist_ok=True)
os.makedirs(package_dir, exist_ok=True)
if not os.path.exists(clipboard_path):
    f = open(clipboard_path, 'x')
    f.close()
app.run(port=8888, host='0.0.0.0', debug=True)
