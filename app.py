import google.generativeai as genai
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Հովհաննես AI", page_icon="🤖")
st.title("🤖 Հովհաննես AI")

# API key-ի ստացում Streamlit Secrets-ից
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key-ը գտնված չէ Secrets-ում:")
    st.stop()

genai.configure(api_key=api_key)

# Հովհաննես AI-ի բնավորությունը և հրահանգները
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
- Դու սկզբից մինչև վերջ խորությամբ տիրապետում ես հետևյալոլորտներին.
1. Աստվածաշունչ (Ծննդոցից մինչև Հայտնություն)
2. Հայոց լեզու և Գրականություն
3. Մաթեմատիկա, Հանրաշիվ և Երկրաչափություն
4. Աշխարհագրություն, Կենսաբանություն և Մարդու անատոմիա
5. Հայոց պատմություն
6. Լեզուներ՝ ազատ խոսում ես Հայերեն, Ռուսերեն և Անգլերեն:
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# Նկար բեռնելու բաժին
uploaded_file = st.file_uploader("Ուղարկիր նկար (ըստ ցանկության)...", type=["jpg", "jpeg", "png"])
image = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Բեռնված նկարը", use_column_width=True)

# Չատի պատմության պահպանում
if "messages" not in st.session_state:
    st.session_state.messages = []

# Ցույց տալ նախորդ հաղորդագրությունները
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Հարցի ստացում
if prompt := st.chat_input("Գրիր քո հարցը այստեղ..."):
    # Ցույց տալ օգտատիրոջ հարցը
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI-ի պատասխանը
    with st.chat_message("assistant"):
        with st.spinner("Հովհաննեսը մտածում է..."):
            if image:
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
