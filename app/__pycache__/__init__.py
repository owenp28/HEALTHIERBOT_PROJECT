import pandas as pd

def load_symptom_data(file_path):
    df = pd.read_csv(file_path)
    return df

def get_disease_description(disease_name, df):
    description = df[df['Disease'] == disease_name]['Description'].values
    if len(description) > 0:
        return description[0]
    else:
        return "Deskripsi tidak ditemukan."
