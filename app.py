import sqlite3
import google.generativeai as genai
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Հովհաննես AI", page_icon="🤖", layout="wide"
)

# --- ՏՎՅԱԼՆԵՐԻ ԲԱԶԱ (SQLite) ---
conn = sqlite3.connect("chats_database.db", check_same_thread=False)
cursor = conn.cursor()

# Ստեղծում ենք աղյուսակներ չատերի և հաղորդագրությունների համար
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

# Բեռնում ենք բոլոր չատերը
cursor.execute("SELECT chat_id, title FROM chats ORDER BY chat_id DESC")
all_chats = cursor.fetchall()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = (
        all_chats[0][0] if all_chats else None
    )

# Ցույց ենք տալիս չատերի ցուցակը
for chat_id, title in all_chats:
    btn_label = f"💬 {title[:25]}..." if len(title) > 25 else f"💬 {title}"
    if st.sidebar.button(
        btn_label, key=f"chat_{chat_id}", use_container_width=True
    ):
        st.session_state.current_chat_id = chat_id
        st.rerun()

# --- MAIN CHAT WINDOW ---
st.title("🤖 Հովհաննես AI")

uploaded_file = st.file_uploader(
    "Ուղարկիր նկար (ըստ ցանկության)...", type=["jpg", "jpeg", "png"]
)
image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Բեռնված նկարը", use_column_width=True)

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

# Հարցի ստացում
if prompt := st.chat_input("Գրիր քո հարցը այստեղ..."):
    # Եթե նոր չատ է, ստեղծում ենք բազայում
    if st.session_state.current_chat_id is None:
        cursor.execute(
            "INSERT INTO chats (title) VALUES (?)", (prompt,)
        )
        conn.commit()
        st.session_state.current_chat_id = cursor.lastrowid

    # Պահպանում ենք հարցը
    cursor.execute(
        "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
        (st.session_state.current_chat_id, "user", prompt),
    )
    conn.commit()

    with st.chat_message("user"):
        st.markdown(prompt)

    # Պատասխանի ստացում
    with st.chat_message("assistant"):
        with st.spinner("Հովհաննեսը մտածում է..."):
            if image:
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)

            st.markdown(response.text)

            # Պահպանում ենք պատասխանը
            cursor.execute(
                "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                (st.session_state.current_chat_id, "assistant", response.text),
            )
            conn.commit()
            st.rerun()
