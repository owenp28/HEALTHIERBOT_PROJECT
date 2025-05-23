import streamlit as st
import json
import pandas as pd
import os
from dotenv import load_dotenv
import tempfile
import speech_recognition as sr
from datetime import datetime
import pytz

# Load environment variables
load_dotenv()

# Page configuration
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

# Function to transcribe audio
def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="id-ID")
            return text.lower()
        except sr.UnknownValueError:
            return "Maaf, audio tidak dapat dikenali"
        except sr.RequestError:
            return "Maaf, layanan tidak tersedia"

# Load datasets
@st.cache_data
def load_datasets():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Load chat dataset
    chat_data_path = os.path.join(base_path, "chatbot_medical_dataset.json")
    try:
        with open(chat_data_path, "r", encoding='utf-8') as f:
            chat_data = json.load(f)
    except FileNotFoundError:
        st.error(f"File tidak ditemukan: {chat_data_path}")
        chat_data = []
    
    # Load symptom dataset
    symptom_path = os.path.join(base_path, "disease symptom prediction", "symptom_Description.csv")
    try:
        df_symptom = pd.read_csv(symptom_path)
    except FileNotFoundError:
        st.error(f"File tidak ditemukan: {symptom_path}")
        df_symptom = pd.DataFrame()
    
    return chat_data, df_symptom

def get_response_from_dataset(prompt, chat_data):
    prompt = prompt.lower()
    best_response = "Maaf, saya tidak memiliki informasi tentang hal tersebut. Silakan konsultasikan dengan dokter."
    
    for item in chat_data:
        if "prompt" in item and "response" in item:
            if prompt in item["prompt"].lower() or item["prompt"].lower() in prompt:
                return item["response"]
            
            keywords = ["apa", "bagaimana", "mengobati", "gejala", "penyakit", "sakit"]
            if any(keyword in prompt and keyword in item["prompt"].lower() for keyword in keywords):
                return item["response"]
    
    return best_response

def process_response(user_input, current_chat, use_openai, api_key, chat_data):
    if use_openai and api_key:
        try:
            import openai
            openai.api_key = api_key

            messages = [
                {"role": "system", "content": "Kamu adalah HealthierBot, asisten kesehatan yang membantu memberikan informasi medis. Kamu memberikan informasi yang akurat dan mudah dipahami. Kamu BUKAN dokter dan selalu menyarankan pengguna untuk berkonsultasi dengan profesional medis untuk diagnosis dan pengobatan."}
            ]
            messages.extend(current_chat["messages"])

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message['content']
        except Exception as e:
            return f"Tidak dapat menggunakan OpenAI API: {str(e)}\n\n" + get_response_from_dataset(user_input, chat_data)
    return get_response_from_dataset(user_input, chat_data)

def save_chat_history(history):
    try:
        with open("chat_history.json", "w", encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")

def load_chat_history():
    try:
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r", encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
    return {"chats": [], "current_chat_id": None}

def create_new_chat():
    timestamp = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S WIB")
    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = load_chat_history()
    st.session_state.chat_history["chats"].append({
        "id": chat_id,
        "timestamp": timestamp,
        "messages": []
    })
    st.session_state.chat_history["current_chat_id"] = chat_id
    save_chat_history(st.session_state.chat_history)

def get_current_chat():
    if 'chat_history' in st.session_state and st.session_state.chat_history["current_chat_id"]:
        for chat in st.session_state.chat_history["chats"]:
            if chat["id"] == st.session_state.chat_history["current_chat_id"]:
                return chat
    return None

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = load_chat_history()
    if not st.session_state.chat_history["chats"]:
        create_new_chat()

# UI Streamlit
chat_data, df_symptom = load_datasets()
st.title("🤖 HealthierBot")

# Sidebar
with st.sidebar:
    st.button("💬 Chat Baru", on_click=create_new_chat)
    
    st.subheader("Riwayat Chat")
    for chat in reversed(st.session_state.chat_history["chats"]):
        if st.button(f"📝 {chat['timestamp']}", key=chat['id']):
            st.session_state.chat_history["current_chat_id"] = chat['id']
            st.rerun()
    
    if st.button("🗑️ Hapus Semua Riwayat"):
        st.session_state.chat_history = {"chats": [], "current_chat_id": None}
        save_chat_history(st.session_state.chat_history)
        create_new_chat()
        st.rerun()

# Main chat interface
current_chat = get_current_chat()
if current_chat:
    st.subheader(f"Chat - {current_chat['timestamp']}")
    
    with st.sidebar.expander("OpenAI API Settings", expanded=False):
        api_key = st.text_input("OpenAI API Key (opsional)", type="password")
        st.caption("Jika tidak diisi, bot akan menggunakan dataset lokal")
        use_openai = st.checkbox("Gunakan OpenAI API", value=False)
    
    use_speech = st.checkbox("Gunakan input suara")
    
    # Display chat messages
    for message in current_chat["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Handle user input (speech or text)
    user_input = None
    
    if use_speech:
        st.info("Unggah file audio (.wav) untuk dikonversi menjadi teks")
        audio_file = st.file_uploader("Unggah file audio", type=["wav"])
        
        if audio_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_path = tmp_file.name
            
            st.audio(tmp_path, format="audio/wav")
            
            if st.button("Transkripsi & Kirim"):
                with st.spinner("Mentranskripsikan audio..."):
                    user_input = transcribe_audio(tmp_path)
                    st.success(f"Transkripsi: {user_input}")
    else:
        user_input = st.chat_input("Tanyakan sesuatu tentang kesehatan...")
    
    if user_input and user_input not in ["Maaf, audio tidak dapat dikenali", "Maaf, layanan tidak tersedia"]:
        # Add and display user message
        current_chat["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get and display bot response
        with st.chat_message("assistant"):
            with st.spinner("Berpikir..."):
                ai_response = process_response(user_input, current_chat, use_openai, api_key, chat_data)
                st.write(ai_response)
                current_chat["messages"].append({"role": "assistant", "content": ai_response})
        
        # Save updated chat history
        save_chat_history(st.session_state.chat_history)
