import streamlit as st
import google.generativeai as genai
import json

# --- 1. 설정 ---
genai.configure(api_key=st.secrets["GENAI_API_KEY"])

# 최신 모델명으로 고정
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config={"response_mime_type": "application/json"}
)

st.set_page_config(page_title="AI 잉글리시", layout="centered")

# 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📱 한 손에 영어회화")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. 대화 기록 출력 ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "data" in msg:
            d = msg["data"]
            col1, col2 = st.columns(2)
            with col1:
                with st.expander("🇰🇷 번역", key=f"trans_{i}"):
                    st.caption(d["translation"])
            with col2:
                if d["correction"]:
                    with st.expander("🔧 교정", key=f"corr_{i}"):
                        st.caption(d["correction"])
            st.warning(f"💡 **Native Pick:** {d['native_tip']}")

# --- 3. 입력창 및 AI 응답 로직 ---
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 화면에 사용자 메시지 즉시 표시
    with st.chat_message("user"):
        st.write(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("AI 튜터가 답변 작성 중..."):
            instruction = "You are a friendly English tutor. Reply in JSON: reply, translation, correction, native_tip."
            response = model.generate_content(f"{instruction}\nUser: {prompt}")
            res_data = json.loads(response.text)
            
            answer = res_data["reply"]
            st.write(answer)
            
            # --- 🔊 음성 재생 스크립트 ---
            # 문장 내 따옴표 에러 방지를 위해 가공
            safe_answer = answer.replace('"', "'").replace('\n', ' ')
            tts_script = f"""
                <script>
                var msg = new SpeechSynthesisUtterance("{safe_answer}");
                msg.lang = 'en-US';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
                </script>
            """
            st.components.v1.html(tts_script, height=0)
            
            st.info(f"📍 **Tip:** {res_data['native_tip']}")
            
            # 데이터 저장
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer, 
                "data": res_data
            })
            
            # 대화가 겹치지 않게 새로고침
            st.rerun()
