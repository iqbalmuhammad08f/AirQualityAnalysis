# Proyek Analisis Data: Beijing Air Quality

Proyek analisis data kualitas udara Beijing menggunakan dataset PRSA dari 12 stasiun pemantauan udara selama periode Maret 2013 – Februari 2017.

## Project Structure

```
submission/
├── dashboard/
│   ├── dashboard.py       # Aplikasi Streamlit
│   └── main_data.csv      # Data bersih hasil notebook
├── data/
│   └── PRSA_Data_20130301-20170228/
│       └── *.csv          # 12 file CSV stasiun pemantauan
├── notebook.ipynb         # Notebook analisis data (sudah dieksekusi)
├── requirements.txt       # Daftar library Python
└── README.md              # File ini
```

## Setup Environment - Anaconda

```
conda create --name air-quality python=3.10
conda activate air-quality
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Setup Environment - venv (Windows)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run Streamlit App

```
streamlit run dashboard/dashboard.py
```

## Dataset

**Sumber**: [Air Quality Dataset](https://github.com/marceloreis/HTI)