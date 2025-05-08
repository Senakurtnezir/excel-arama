from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploaded_data = None


# Globalde dataframe tutacağız
df = None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global uploaded_data  # bu satırı ekle
    if request.method == 'POST':
        file = request.files['excel_file']
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            uploaded_data = df  # burada veriyi bellekte tutuyoruz
            message = 'Dosya başarıyla yüklendi.'
        else:
            message = 'Lütfen sadece .xlsx uzantılı dosya yükleyin.'
        return render_template('index.html', message=message)
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    global uploaded_data 
    query = request.form['query'].lower()
    if uploaded_data is None:
        return render_template('index.html', message='Önce bir dosya yüklemelisiniz.')

    # Tüm hücreleri birleştirip arama yap
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
