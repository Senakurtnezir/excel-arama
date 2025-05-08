from flask import Flask, request, render_template
import pandas as pd
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Bellekte veri tutmak için global bir değişken
uploaded_data = None

# Dosya uzantısı kontrol fonksiyonu
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xlsx'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global uploaded_data
    if request.method == 'POST':
        file = request.files['excel_file']
        if file and allowed_file(file.filename):
            df = pd.read_excel(file, engine='openpyxl')
            uploaded_data = df
            message = 'Dosya başarıyla yüklendi.'
        else:
            message = 'Lütfen sadece .xlsx uzantılı dosya yükleyin.'
        return render_template('index.html', message=message)
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    global uploaded_data
    if uploaded_data is None:
        return render_template('index.html', message='Önce bir dosya yükleyin.')

    query = request.form['query'].lower()

    def match(row):
        combined = ' '.join(map(str, row)).lower()
        return all(part in combined for part in query.split())

    results = uploaded_data[uploaded_data.apply(match, axis=1)]

    if results.empty:
        return render_template('index.html', message='Sonuç bulunamadı.')
    else:
        html_table = results.to_html(classes='table table-bordered table-striped', index=False)
        return render_template('index.html', tables=html_table)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
