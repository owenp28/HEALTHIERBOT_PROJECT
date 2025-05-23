import streamlit as st
import json
import pandas as pd
import os
from dotenv import load_dotenv
import tempfile
import speech_recognition as sr

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
    try:
        # Try relative path from app directory
        with open("../chatbot_medical_dataset.json", "r") as f:
            chat_data = json.load(f)
    except FileNotFoundError:
        # Try from current directory
        with open("chatbot_medical_dataset.json", "r") as f:
            chat_data = json.load(f)
            
    try:
        # Try relative path from app directory
        df_symptom = pd.read_csv("../disease symptom prediction/symptom_Description.csv")
    except FileNotFoundError:
        # Try from current directory
        df_symptom = pd.read_csv("disease symptom prediction/symptom_Description.csv")
        
    return chat_data, df_symptom

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

# UI Streamlit
chat_data, df_symptom = load_datasets()
st.title("🤖 HealthierBot")
menu = st.sidebar.selectbox("Pilih Fitur", ["ChatBot Kesehatan"])

# ChatBot Kesehatan
if menu == "ChatBot Kesehatan":
    st.header("💬 ChatBot Kesehatan")
    
    # API key input
    with st.sidebar.expander("OpenAI API Settings", expanded=False):
        api_key = st.text_input("OpenAI API Key (opsional)", type="password")
        st.caption("Jika tidak diisi, bot akan menggunakan dataset lokal")
        use_openai = st.checkbox("Gunakan OpenAI API", value=False)
    
    # Speech input option
    use_speech = st.checkbox("Gunakan input suara")
    
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
                    
                    # Process the transcribed input
                    if user_input and user_input != "Maaf, audio tidak dapat dikenali" and user_input != "Maaf, layanan tidak tersedia":
                        # Display user message
                        with st.chat_message("user"):
                            st.write(user_input)
                        
                        # Add user message to chat history
                        st.session_state.chat_history.append({"role": "user", "content": user_input})
                        
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
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Get user input via text
    if not use_speech:
        user_input = st.chat_input("Tanyakan sesuatu tentang kesehatan...")
        
        if user_input:
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
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
