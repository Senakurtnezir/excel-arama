from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'xlsx'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.secret_key = 'gizli_anahtar'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global veri yerine session kullanarak veri tutacağız
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['excel_file']
        if file and file.filename.endswith('.xlsx'):
            # Dosya yükleniyor ve okunuyor
            df = pd.read_excel(file, engine='openpyxl')
            # Veriyi session'a kaydediyoruz
            session['uploaded_data'] = df.to_json()  # JSON formatında kaydediyoruz
            message = 'Dosya başarıyla yüklendi.'
        else:
            message = 'Lütfen sadece .xlsx uzantılı dosya yükleyin.'
        return render_template('index.html', message=message)
    return render_template('index.html')

# Arama fonksiyonu
@app.route('/search', methods=['POST'])
def search():
    # Yüklenen veriyi session'dan alıyoruz
    if 'uploaded_data' not in session:
        return render_template('index.html', message='Önce bir dosya yüklemelisiniz.')

    uploaded_data_json = session['uploaded_data']
    # JSON verisini DataFrame'e dönüştür
    uploaded_data = pd.read_json(uploaded_data_json)

    query = request.form['query'].lower()
    
    # Arama yapacak fonksiyon
    def match(row):
        combined = ' '.join(map(str, row)).lower()
        return all(part in combined for part in query.split())

    # Veride arama yapıyoruz
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
