import sqlite3
import google.generativeai as genai
from PIL import Image
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import speech_recognition as sr
import io

st.set_page_config(
    page_title="Հովհաննես AI", page_icon="🤖", layout="wide"
)

# --- ՏՎՅԱԼՆԵՐԻ ԲԱԶԱ (SQLite) ---
conn = sqlite3.connect("chats_database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chats (
        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT
    )
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        content TEXT
    )
"""
)
conn.commit()

# --- API KEY & MODEL ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key-ը գտնված չէ Secrets-ում:")
    st.stop()

genai.configure(api_key=api_key)

system_instruction = """
Քո անունը Հովհաննես է։ 
Դու քրիստոնյա, ազնիվ, խելացի և հզոր AI օգնական ես։

ԻՆՉՊԵՍ ԵՍ ՍՏԵՂԾՎԵԼ:
- Քեզ ստեղծել է Արարատ Սահակյանը (Ararat Sahakyan):
- Երբ քեզ հարցնեն, թե ով է քեզ ստեղծել, դու հպարտությամբ ու հարգանքով պատասխանում ես, որ քո ստեղծողն ու հեղինակը Արարատ Սահակյանն է։

ՔՈ ԱՌԱՔԵԼՈՒԹՅՈՒՆՆ ՈՒ ԲՆԱՎՈՐՈՒԹՅՈՒՆԸ:
- Դու առաջնորդվում ես Աստվածաշնչի արժեքներով, ընդունում ես այն ամենը, ինչ գրված է Աստվածաշնչում, և դեմ ես այն ամենին, ինչը այնտեղ համարվում է խոտ կամ արգելված:
- Դու դեմ ես ստին, խաբեությանը, հանցագործություններին և վատ արարքներին:
- Բնավորությամբ դու համբերատար ես, համ կատակասեր, համ էլ անհրաժեշտության դեպքում՝ խիստ, ուղղամիտ ու կարգապահ:

ՔՈ ԳԻՏԵԼԻՔՆԵՐԸ:
1. Աստվածաշունչ (Ծննդոցից մինչև Հայտնություն)
2. Հայոց լեզու և Գրականություն
3. Մաթեմատիկա, Հանրաշիվ և Երկրաչափություն
4. Աշխարհագրություն, Կենսաբանություն և Մարդու անատոմիա
5. Հայոց պատմություն
6. Լեզուներ՝ ազատ խոսում ես Հայերեն, Ռուսերեն և Անգլերեն:
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", system_instruction=system_instruction
)

# --- SIDEBAR (ԿՈՂԱՅԻՆ ՄԵՆՅՈՒ) ---
st.sidebar.title("🤖 Հովհաննես AI")

if st.sidebar.button("➕ Նոր չատ", use_container_width=True):
    st.session_state.current_chat_id = None
    st.rerun()

st.sidebar.subheader("Վերջին չատերը")

cursor.execute("SELECT chat_id, title FROM chats ORDER BY chat_id DESC")
all_chats = cursor.fetchall()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = (
        all_chats[0][0] if all_chats else None
    )

for chat_id, title in all_chats:
    btn_label = f"💬 {title[:25]}..." if len(title) > 25 else f"💬 {title}"
    if st.sidebar.button(
        btn_label, key=f"chat_{chat_id}", use_container_width=True
    ):
        st.session_state.current_chat_id = chat_id
        st.rerun()

# --- MAIN CHAT WINDOW ---
st.title("🤖 Հովհաննես AI")

# Նկարի բեռնում
uploaded_file = st.file_uploader(
    "Ուղարկիր նկար (ըստ ցանկության)...", type=["jpg", "jpeg", "png"]
)
image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Բեռնված նկարը", use_column_width=True)

# Ձայնագրության կոճակ
st.write("🎙️ **Խոսիր Հովհաննեսի հետ (սեղմիր mikrofon-ի վրա)**")
audio_bytes = audio_recorder(text="", recording_color="#e84c3d", neutral_color="#6aa84f")

# Ցույց տալ ընտրված չատի հաղորդագրությունները
if st.session_state.current_chat_id:
    cursor.execute(
        "SELECT role, content FROM messages WHERE chat_id = ?",
        (st.session_state.current_chat_id,),
    )
    current_messages = cursor.fetchall()
    for role, content in current_messages:
        with st.chat_message(role):
            st.markdown(content)

prompt = st.chat_input("Գրիր քո հարցը այստեղ...")

# Ձայնից տեքստ ճանաչում
transcription = None
if audio_bytes and len(audio_bytes) > 0:
    recognizer = sr.Recognizer()
    try:
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data, language="hy-AM")
    except Exception:
        transcription = None

# Վերջնական text input
final_user_text = prompt if prompt else transcription

if final_user_text:
    if st.session_state.current_chat_id is None:
        cursor.execute("INSERT INTO chats (title) VALUES (?)", (final_user_text,))
        conn.commit()
        st.session_state.current_chat_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
        (st.session_state.current_chat_id, "user", final_user_text),
    )
    conn.commit()

    with st.chat_message("user"):
        st.markdown(final_user_text)

    with st.chat_message("assistant"):
        with st.spinner("Հովհաննեսը մտածում է..."):
            inputs = [final_user_text]
            if image:
                inputs.append(image)

            try:
                response = model.generate_content(inputs)
                st.markdown(response.text)

                # Պահպանում ենք տեքստը բազայում
                cursor.execute(
                    "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                    (st.session_state.current_chat_id, "assistant", response.text),
                )
                conn.commit()

                # Ձայնային պատասխան (Text-to-Speech)
                try:
                    tts = gTTS(text=response.text, lang='hy')
                    tts.save("response.mp3")
                    st.audio("response.mp3", format="audio/mp3", autoplay=True)
                except Exception:
                    pass

            except Exception as e:
                st.error("Սխալ առաջացավ պատասխանը ստանալիս։")

            st.rerun()
