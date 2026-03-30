import streamlit as st
import google.generativeai as genai
import json

# --- 설정 ---
genai.configure(api_key=st.secrets["GENAI_API_KEY"])

# 상단 모델 설정 부분을 이렇게 바꿔보세요
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config={"response_mime_type": "application/json"},
    # 시스템 명령을 아예 고정 (더 정확해집니다)
    system_instruction="You are a friendly English tutor. Reply in JSON: reply, translation, correction, native_tip."
)

# 하단 호출 부분은 심플하게 변경
if prompt := st.chat_input("메시지를 입력하세요..."):
    # ... (생략) ...
    with st.chat_message("assistant"):
        # 호출 시 instruction을 뺄 수 있어 에러 확률이 줄어듭니다.
        response = model.generate_content(prompt) 
        res_data = json.loads(response.text)

# 모바일 대응 설정
st.set_page_config(page_title="AI 잉글리시", layout="centered")

# --- 스타일링 (모바일 가독성) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📱 한 손에 영어회화")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화창 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "data" in msg:
            d = msg["data"]
            # 모바일에서는 탭이나 익스팬더가 깔끔합니다.
            col1, col2 = st.columns(2)
            with col1:
                with st.expander("🇰🇷 번역"):
                    st.caption(d["translation"])
            with col2:
                if d["correction"]:
                    with st.expander("🔧 교정"):
                        st.caption(d["correction"])
            
            # 원어민 표현은 눈에 띄게 하단에 배치
            st.warning(f"💡 **Native Pick:** {d['native_tip']}")

# 입력창 (스마트폰 키보드 대응)
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        instruction = "You are a friendly English tutor. Reply in JSON: reply, translation, correction, native_tip."
        response = model.generate_content(f"{instruction}\nUser: {prompt}")
        res_data = json.loads(response.text)
        
        st.write(res_data["reply"])
        
        # 즉시 피드백 노출
        st.info(f"📍 **Tip:** {res_data['native_tip']}")
        
        st.session_state.messages.append({"role": "assistant", "content": res_data["reply"], "data": res_data})
