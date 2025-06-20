import streamlit as st
import json
import pandas as pd
import os

# Page configuration - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="HealthierBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# HealthierBot - Asisten Kesehatan Medis"
    }
)

# Set custom color theme - using a triadic color scheme
primary_color = "#4287f5"    # Blue
secondary_color = "#f542a1"  # Pink
accent_color = "#42f5b3"     # Mint

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        font-family: 'Roboto', sans-serif;
    }
    h1, h2, h3 {
        color: #333333;
    }
    .stButton>button {
        background-color: """ + primary_color + """;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: """ + secondary_color + """;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .info-box {
        background-color: #e8f4f8;
        border-left: 5px solid """ + primary_color + """;
        padding: 1rem;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .symmetric-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
    }
    .symmetric-item {
        flex: 1;
    }
</style>
""", unsafe_allow_html=True)

# Load datasets
@st.cache_data
def load_datasets():
    try:
        # Try relative path from app directory
        with open("../chatbot_medical_dataset.json", "r", encoding='utf-8') as f:
            chat_data = json.load(f)
    except FileNotFoundError:
        # Try from current directory
        with open("chatbot_medical_dataset.json", "r", encoding='utf-8') as f:
            chat_data = json.load(f)
            
    try:
        # Try relative path from app directory
        df_symptom = pd.read_csv("../disease symptom prediction/symptom_Description.csv")
    except FileNotFoundError:
        # Try from current directory
        df_symptom = pd.read_csv("disease symptom prediction/symptom_Description.csv")
    
    # Sample food database with calories (per 100g)
    food_data = {
        'Nasi Putih': {'kalori': 130, 'protein': 2.7, 'karbohidrat': 28, 'lemak': 0.3},
        'Ayam Dada': {'kalori': 165, 'protein': 31, 'karbohidrat': 0, 'lemak': 3.6},
        'Telur': {'kalori': 155, 'protein': 13, 'karbohidrat': 1.1, 'lemak': 11},
        'Tempe': {'kalori': 193, 'protein': 19, 'karbohidrat': 9.4, 'lemak': 11},
        'Tahu': {'kalori': 76, 'protein': 8, 'karbohidrat': 1.9, 'lemak': 4.8},
        'Sayur Bayam': {'kalori': 23, 'protein': 2.9, 'karbohidrat': 3.6, 'lemak': 0.4},
        'Apel': {'kalori': 52, 'protein': 0.3, 'karbohidrat': 14, 'lemak': 0.2},
        'Pisang': {'kalori': 89, 'protein': 1.1, 'karbohidrat': 23, 'lemak': 0.3},
        'Ikan Salmon': {'kalori': 208, 'protein': 22, 'karbohidrat': 0, 'lemak': 13},
        'Kentang': {'kalori': 77, 'protein': 2, 'karbohidrat': 17, 'lemak': 0.1}
    }
        
    return chat_data, df_symptom, food_data

def save_chat_history():
    """Menyimpan history chat ke file"""
    history_file = "chat_history.json"
    try:
        with open(history_file, "w", encoding='utf-8') as f:
            json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Gagal menyimpan history chat: {str(e)}")

def load_chat_history():
    """Memuat history chat dari file"""
    history_file = "chat_history.json"
    try:
        with open(history_file, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"Gagal memuat history chat: {str(e)}")
        return []

# Function untuk memberikan saran diet
def get_diet_recommendation(berat_badan, tinggi_badan, usia, jenis_kelamin, aktivitas, tujuan):
    # Menghitung BMI
    tinggi_m = tinggi_badan / 100
    bmi = berat_badan / (tinggi_m * tinggi_m)
    
    # Menghitung BMR (Basal Metabolic Rate) dengan rumus Harris-Benedict
    if jenis_kelamin == "Pria":
        bmr = 88.362 + (13.397 * berat_badan) + (4.799 * tinggi_badan) - (5.677 * usia)
    else:
        bmr = 447.593 + (9.247 * berat_badan) + (3.098 * tinggi_badan) - (4.330 * usia)
    
    # Faktor aktivitas
    aktivitas_faktor = {
        "Sangat Jarang": 1.2,
        "Ringan": 1.375,
        "Sedang": 1.55,
        "Aktif": 1.725,
        "Sangat Aktif": 1.9
    }
    
    # Total kebutuhan kalori
    total_kalori = bmr * aktivitas_faktor[aktivitas]
    
    # Menyesuaikan dengan tujuan
    if tujuan == "Menurunkan Berat Badan":
        total_kalori *= 0.8  # Defisit 20%
    elif tujuan == "Menambah Berat Badan":
        total_kalori *= 1.2  # Surplus 20%
    
    # Membuat rekomendasi berdasarkan BMI
    if bmi < 18.5:
        status = "Berat badan kurang"
        saran = "Fokus pada makanan bergizi tinggi dan protein untuk membangun massa otot."
    elif bmi < 25:
        status = "Berat badan normal"
        saran = "Pertahankan pola makan seimbang dengan variasi makanan yang beragam."
    elif bmi < 30:
        status = "Berat badan berlebih"
        saran = "Kurangi asupan kalori dan tingkatkan aktivitas fisik."
    else:
        status = "Obesitas"
        saran = "Konsultasikan dengan dokter atau ahli gizi untuk program penurunan berat badan yang aman."
    
    return {
        'bmi': round(bmi, 2),
        'status': status,
        'kalori_harian': round(total_kalori),
        'saran': saran
    }

# Function untuk mendiagnosis gejala sederhana
def diagnose_symptoms(selected_symptoms):
    common_conditions = {
        'Demam': ['demam', 'menggigil', 'sakit kepala', 'lemas'],
        'Flu': ['demam', 'hidung tersumbat', 'bersin', 'batuk', 'sakit tenggorokan'],
        'Migrain': ['sakit kepala berdenyut', 'mual', 'sensitif cahaya', 'sensitif suara'],
        'Maag': ['nyeri perut', 'mual', 'kembung', 'tidak nafsu makan'],
        'Alergi': ['bersin', 'gatal', 'ruam kulit', 'mata berair']
    }
    
    possible_conditions = []
    for condition, symptoms in common_conditions.items():
        matching_symptoms = len(set(selected_symptoms) & set(symptoms))
        if matching_symptoms >= 2:  # Jika minimal 2 gejala cocok
            possible_conditions.append(condition)
    
    return possible_conditions

# Function to get response based on medical dataset
def get_response_from_dataset(prompt, chat_data):
    prompt = prompt.lower()
    best_response = "Maaf, saya tidak memiliki informasi tentang hal tersebut. Silakan konsultasikan dengan dokter."
    
    # Check for disease information
    for item in chat_data:
        if "prompt" in item and "response" in item:
            if prompt in item["prompt"].lower() or item["prompt"].lower() in prompt:
                return item["response"]
            
            # Check for keywords
            keywords = ["apa", "bagaimana", "mengobati", "gejala", "penyakit", "sakit"]
            for keyword in keywords:
                if keyword in prompt and keyword in item["prompt"].lower():
                    return item["response"]
    
    return best_response

# Initialize chat history in session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    # Load chat history at startup
    st.session_state.chat_history = load_chat_history()

# Load all datasets
chat_data, df_symptom, food_data = load_datasets()

# UI Streamlit
st.title("🤖 HealthierBot")
st.markdown("<p style='font-size: 1.2em; color: #666;'>Asisten kesehatan digital untuk informasi medis dan gaya hidup sehat</p>", unsafe_allow_html=True)

# Sidebar with menu
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/healthcare-and-medical.png", width=80)
    st.markdown("### Menu Utama")
    menu = st.selectbox("Pilih Fitur", ["ChatBot Kesehatan", "Saran Diet", "Kalkulator Kalori", "Diagnosis Sederhana"])

# ChatBot Kesehatan
if menu == "ChatBot Kesehatan":
    st.header("💬 ChatBot Kesehatan")
    
    # History controls in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("Pengaturan History Chat")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Hapus History", use_container_width=True):
                st.session_state.chat_history = []
                save_chat_history()
                st.success("History chat berhasil dihapus!")
        
        with col2:
            show_history = st.checkbox("Tampilkan History", value=True)
        
        if len(st.session_state.chat_history) > 0:
            if st.download_button(
                "Unduh History Chat",
                data=json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=2),
                file_name="chat_history.json",
                mime="application/json",
                use_container_width=True
            ):
                st.success("History chat berhasil diunduh!")
    
        # API key input
        st.markdown("---")
        with st.expander("OpenAI API Settings", expanded=False):
            api_key = st.text_input("OpenAI API Key (opsional)", type="password")
            st.caption("Jika tidak diisi, bot akan menggunakan dataset lokal")
            use_openai = st.checkbox("Gunakan OpenAI API", value=False)
    
    # Display chat history if enabled
    if show_history and len(st.session_state.chat_history) > 0:
        st.subheader("History Chat")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Get user input via text
    user_input = st.chat_input("Tanyakan sesuatu tentang kesehatan...")
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        save_chat_history()
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Berpikir..."):
                if use_openai and api_key:
                    try:
                        from openai import OpenAI
                        client = OpenAI(api_key=api_key)
                        
                        messages = [
                            {"role": "system", "content": "Kamu adalah HealthierBot, asisten kesehatan yang membantu memberikan informasi medis. Kamu memberikan informasi yang akurat dan mudah dipahami. Kamu BUKAN dokter dan selalu menyarankan pengguna untuk berkonsultasi dengan profesional medis untuk diagnosis dan pengobatan."}
                        ]
                        
                        # Add chat history
                        for message in st.session_state.chat_history[:-1]:
                            messages.append({"role": message["role"], "content": message["content"]})
                        
                        # Add current prompt
                        messages.append({"role": "user", "content": user_input})
                        
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7
                        )
                        
                        ai_response = response.choices[0].message.content
                    except Exception as e:
                        ai_response = f"Tidak dapat menggunakan OpenAI API: {str(e)}\n\n"
                        ai_response += get_response_from_dataset(user_input, chat_data)
                else:
                    ai_response = get_response_from_dataset(user_input, chat_data)
                
                st.write(ai_response)
        
        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        save_chat_history()

elif menu == "Saran Diet":
    st.header("🥗 Saran Diet dan Makanan Seimbang")
    st.markdown('<div>Dapatkan rekomendasi diet berdasarkan data fisik dan tujuan Anda</div>', unsafe_allow_html=True)
    
    # Create two equal columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Data Fisik")
        berat_badan = st.number_input("Berat Badan (kg)", min_value=30.0, max_value=200.0, value=60.0, step=0.5, format="%.1f")
        tinggi_badan = st.number_input("Tinggi Badan (cm)", min_value=100.0, max_value=250.0, value=165.0, step=0.5, format="%.1f")
        usia = st.number_input("Usia (tahun)", min_value=15, max_value=100, value=25)
    
    with col2:
        st.markdown("#### Preferensi")
        jenis_kelamin = st.radio("Jenis Kelamin", ["Pria", "Wanita"])
        aktivitas = st.select_slider("Tingkat Aktivitas", 
                               options=["Sangat Jarang", "Ringan", "Sedang", "Aktif", "Sangat Aktif"],
                               value="Sedang",
                               help="Sangat Jarang: Hampir tidak berolahraga\nRingan: Olahraga 1-3 kali seminggu\nSedang: Olahraga 3-5 kali seminggu\nAktif: Olahraga 6-7 kali seminggu\nSangat Aktif: Olahraga berat setiap hari")
        tujuan = st.selectbox("Tujuan Diet", ["Menurunkan Berat Badan", "Mempertahankan Berat Badan", "Menambah Berat Badan"])

    if st.button("Dapatkan Saran Diet", use_container_width=True):
        hasil = get_diet_recommendation(berat_badan, tinggi_badan, usia, jenis_kelamin, aktivitas, tujuan)
        
        st.subheader("Hasil Analisis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div>', unsafe_allow_html=True)
            st.metric("BMI", f"{hasil['bmi']}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div>', unsafe_allow_html=True)
            st.metric("Status", hasil['status'])
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div>', unsafe_allow_html=True)
            st.metric("Kebutuhan Kalori Harian", f"{hasil['kalori_harian']} kkal")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div>{hasil["saran"]}</div>', unsafe_allow_html=True)
        
        st.subheader("Rekomendasi Makanan")
        st.write("Berikut adalah contoh makanan sehat yang bisa Anda konsumsi:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Sarapan:")
            st.markdown("- Oatmeal dengan buah")
            st.markdown("- Telur + roti gandum")
            st.markdown("- Yogurt dengan granola")
        
        with col2:
            st.markdown("##### Makan Siang/Malam:")
            st.markdown("- Nasi + ayam dada + sayuran")
            st.markdown("- Ikan + kentang + sayuran")
            st.markdown("- Tempe/tahu + sayuran")

elif menu == "Kalkulator Kalori":
    st.header("🍽️ Kalkulator Kalori Makanan")
    st.markdown('<div>Hitung kandungan nutrisi dari makanan yang Anda konsumsi</div>', unsafe_allow_html=True)
    
    # Tampilkan daftar makanan yang tersedia
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_food = st.selectbox("Pilih Jenis Makanan", list(food_data.keys()))
    
    with col2:
        portion = st.number_input("Porsi (gram)", min_value=1, value=100, step=10)
    
    if st.button("Hitung Kalori", use_container_width=True):
        food_info = food_data[selected_food]
        kalori = (food_info['kalori'] * portion) / 100
        protein = (food_info['protein'] * portion) / 100
        karbohidrat = (food_info['karbohidrat'] * portion) / 100
        lemak = (food_info['lemak'] * portion) / 100
        
        st.subheader(f"Informasi Nutrisi untuk {selected_food} ({portion}g)")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div>', unsafe_allow_html=True)
            st.metric("Kalori", f"{round(kalori, 1)} kkal")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div>', unsafe_allow_html=True)
            st.metric("Protein", f"{round(protein, 1)}g")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div>', unsafe_allow_html=True)
            st.metric("Karbohidrat", f"{round(karbohidrat, 1)}g")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div>', unsafe_allow_html=True)
            st.metric("Lemak", f"{round(lemak, 1)}g")
            st.markdown('</div>', unsafe_allow_html=True)
    
        st.markdown('<div>Catatan: Nilai gizi di atas adalah perkiraan dan dapat bervariasi tergantung pada cara pengolahan dan kualitas bahan makanan.</div>', unsafe_allow_html=True)

elif menu == "Diagnosis Sederhana":
    st.header("🏥 Diagnosis Sederhana")
    st.markdown('<div>Perhatian: Fitur ini hanya memberikan informasi awal dan BUKAN pengganti konsultasi dengan dokter!</div>', unsafe_allow_html=True)
    
    symptoms = [
        'demam', 'menggigil', 'sakit kepala', 'lemas',
        'hidung tersumbat', 'bersin', 'batuk', 'sakit tenggorokan',
        'sakit kepala berdenyut', 'mual', 'sensitif cahaya', 'sensitif suara',
        'nyeri perut', 'kembung', 'tidak nafsu makan',
        'gatal', 'ruam kulit', 'mata berair'
    ]
    
    st.markdown("#### Pilih gejala yang Anda alami:")
    
    # Create a more organized layout for symptoms selection
    col1, col2 = st.columns(2)
    
    with col1:
        selected_symptoms_1 = st.multiselect(
            "Gejala umum:",
            options=sorted(symptoms[:9]),
            help="Pilih satu atau lebih gejala yang Anda rasakan"
        )
    
    with col2:
        selected_symptoms_2 = st.multiselect(
            "Gejala spesifik:",
            options=sorted(symptoms[9:]),
            help="Pilih satu atau lebih gejala yang Anda rasakan"
        )
    
    # Combine selected symptoms
    selected_symptoms = selected_symptoms_1 + selected_symptoms_2
    
    if selected_symptoms:
        if st.button("Analisis Gejala", use_container_width=True):
            possible_conditions = diagnose_symptoms(selected_symptoms)
            
            if possible_conditions:
                st.subheader("Kemungkinan Kondisi:")
                for condition in possible_conditions:
                    st.markdown(f"- **{condition}**")
                
                st.markdown("""
                <div>
                <strong>Catatan penting:</strong><br>
                1. Diagnosis ini hanya berdasarkan gejala umum dan BUKAN diagnosis medis resmi<br>
                2. Jika gejala berlanjut atau memburuk, segera konsultasikan dengan dokter<br>
                3. Diagnosis ini tidak menggantikan pemeriksaan medis profesional
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Tidak dapat menentukan diagnosis berdasarkan gejala yang dipilih. Silakan konsultasikan dengan dokter untuk pemeriksaan lebih lanjut.")
