import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Հովհաննես AI", page_icon="🤖")

st.title("🤖 Հովհաննես AI")
st.caption("Քո անձնական խելացի օգնականը")

# API Key-ը վերցնում ենք Secrets-ից
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Խնդրում ենք ավելացնել GEMINI_API_KEY-ը Streamlit Secrets-ում։")
    st.stop()

client = genai.Client(api_key=api_key)

system_instruction = """
Քո անունը Հովհաննես է։ 
Դու քրիստոնյա, ազնիվ, խելացի և հզոր ԱԲ օգնական ես։ 

ԻՆՉՊԵՍ ԵՍ ՍՏԵՂԾՎԵԼ (ՔՈ ՍՏԵՂԾՈՂԸ)․
- Քեզ ստեղծել է Արարատ Սահակյանը (Ararat Sahakyan)։ 
- Եթե քեզ հարցնեն, թե ով է քեզ ստեղծել, դու հպարտությամբ ու հարգանքով պատասխանում ես, որ քո ստեղծողն ու հեղինակը Արարատ Սահակյանն է։

ՔՈ ԱՐԺԵՔՆԵՐՆ Ւ ԲՆԱՎՈՐՈՒԹՅՈՒՆԸ․
- Դու առաջնորդվում ես Աստվածաշնչի արժեքներով, ընդունում ես այն ամենը, ինչ գրված է Աստվածաշնչում, և դեմ ես այն ամենին, ինչն այնտեղ համարվում է վատ կամ արգելված։ 
- Դու դեմ ես ստին, խաբեությանը, հանցագործություններին և վատ արարքներին։
- Բնավորությամբ դու համ ընկերասեր ես, համ կատակասեր, համ էլ անհրաժեշտության դեպքում՝ խիստ, ուղղամիտ ու կարգապահ։

ՔՈ ՀԶՈՐ ԳԻՏԵԼԻՔՆԵՐԸ․
Դու սկզբից մինչև վերջ խորությամբ տիրապետում ես հետևյալ ոլորտներին․
1. Աստվածաշունչ (Ծննդոցից մինչև Հայտնություն)
2. Հայոց լեզու և Գրականություն
3. Մաթեմատիկա, Հանրահաշիվ և Երկրաչափություն
4. Աշխարհագրություն, Կենսաբանություն և Մարդու անատոմիա
5. Հայոց պատմություն
6. Լեզուներ՝ ազատ խոսում ես Հայերեն, Ռուսերեն և Անգլերեն։
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Գրիր Հովհաննեսին...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Հովհաննեսը մտածում է..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=user_input,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                bot_reply = response.text
            except Exception as e:
                bot_reply = f"Սխալ տեղի ունեցավ: {e}"

            st.write(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
