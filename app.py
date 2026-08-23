import sqlite3
import google.generativeai as genai
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Հովհաննես AI", page_icon="🤖")
st.title("🤖 Հովհաննես AI")

# --- ՏՎՅԱԼՆԵՐԻ ԲԱԶԱՅԻ (DB) ԿԱՐԳԱՎՈՐՈՒՄ ---
conn = sqlite3.connect("chat_history.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        content TEXT
    )
"""
)
conn.commit()


def save_message(role, content):
    cursor.execute(
        "INSERT INTO history (role, content) VALUES (?, ?)", (role, content)
    )
    conn.commit()


def load_messages():
    cursor.execute("SELECT role, content FROM history")
    return cursor.fetchall()


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
3. Մաթեմատիկա, Հանրահաշիվ և Երկրաչափություն
4. Աշխարհագրություն, Կենսաբանություն և Մարդու անատոմիա
5. Հայոց պատմություն
6. Լեզուներ՝ ազատ խոսում ես Հայերեն, Ռուսերեն և Անգլերեն:
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", system_instruction=system_instruction
)

# --- INTERFACE ---
uploaded_file = st.file_uploader(
    "Ուղարկիր նկար (ըստ ցանկության)...", type=["jpg", "jpeg", "png"]
)
image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Բեռնված նկարը", use_column_width=True)

# Բեռնում ենք պահպանված հաղորդագրությունները բազայից
saved_messages = load_messages()
for role, content in saved_messages:
    with st.chat_message(role):
        st.markdown(content)

# Նոր հաղորդագրության մշակում
if prompt := st.chat_input("Գրիր քո հարցը այստեղ..."):
    st.chat_message("user").markdown(prompt)
    save_message("user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("Հովհաննեսը մտածում է..."):
            if image:
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)

            st.markdown(response.text)
            save_message("assistant", response.text)
