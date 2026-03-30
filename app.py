import streamlit as st
import google.generativeai as genai
import json

# --- 설정 ---
genai.configure(api_key=st.secrets["GENAI_API_KEY"])

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    generation_config={"response_mime_type": "application/json"}
)

st.set_page_config(page_title="AI 잉글리시", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📱 한 손에 영어회화")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화창 출력 (enumerate를 사용하여 고유 번호 i를 부여합니다)
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "data" in msg:
            d = msg["data"]
            col1, col2 = st.columns(2)
            with col1:
                # key=f"trans_{i}" 처럼 고유한 키를 지정하여 중복을 피합니다.
                with st.expander("🇰🇷 번역", key=f"trans_{i}"):
                    st.caption(d["translation"])
            with col2:
                if d["correction"]:
                    with st.expander("🔧 교정", key=f"corr_{i}"):
                        st.caption(d["correction"])
            
            st.warning(f"💡 **Native Pick:** {d['native_tip']}")

# 입력창
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        instruction = "You are a friendly English tutor. Reply in JSON: reply, translation, correction, native_tip."
        response = model.generate_content(f"{instruction}\nUser: {prompt}")
        res_data = json.loads(response.text)
        
        st.write(res_data["reply"])
        st.info(f"📍 **Tip:** {res_data['native_tip']}")
        
        # 새로운 메시지에도 고유 ID가 부여되도록 세션에 저장
        st.session_state.messages.append({"role": "assistant", "content": res_data["reply"], "data": res_data})
        
        # 화면 즉시 갱신
        st.rerun()
