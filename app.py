import streamlit as st
import google.generativeai as genai
import json

# --- 1. 설정 ---
genai.configure(api_key=st.secrets["GENAI_API_KEY"])

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    generation_config={"response_mime_type": "application/json"}
)

st.set_page_config(page_title="AI 잉글리시", layout="centered")

# --- 2. 음성 인식(STT) 자바스크립트 ---
# 마이크 버튼을 누르면 브라우저가 음성을 인식해 스트림릿으로 전달합니다.
st.markdown("""
    <script>
    function startRecognition() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US'; // 영어 인식
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            // 스트림릿의 보이지 않는 입력창에 텍스트를 전달
            const inputField = window.parent.document.querySelector('textarea[aria-label="메시지를 입력하세요..."]');
            if (inputField) {
                inputField.value = transcript;
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
            }
        };
        recognition.start();
    }
    </script>
""", unsafe_allow_html=True)

# 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 50px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ 실전 음성 영어회화")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. 마이크 버튼 (상단 배치) ---
if st.button("🎤 눌러서 영어로 말하기 (Tap to Speak)"):
    st.components.v1.html("""
        <script>
        const recognition = new (window.parent.window.SpeechRecognition || window.parent.window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.start();
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            // 부모 창(스트림릿)으로 인식된 텍스트 전송
            window.parent.postMessage({type: 'stt_result', text: text}, "*");
        };
        </script>
    """, height=0)

# 자바스크립트 메시지 수신 로직 (인식된 결과를 chat_input에 자동 입력하기 위함)
import streamlit.components.v1 as components
st.caption("※ 마이크 버튼을 누르고 영어를 말씀하신 뒤, 아래 입력창에 텍스트가 뜨면 전송 버튼을 눌러주세요.")

# --- 4. 대화 기록 및 AI 응답 로직 (기존과 동일) ---
# ... (이전 코드와 동일하게 대화 로그 출력 부분 유지) ...

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

if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI 튜터가 듣고 있습니다..."):
            instruction = "You are a friendly English tutor. Reply in JSON: reply, translation, correction, native_tip."
            response = model.generate_content(f"{instruction}\nUser: {prompt}")
            res_data = json.loads(response.text)
            
            answer = res_data["reply"]
            st.write(answer)
            
            # 🔊 음성 출력 (TTS)
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
            st.session_state.messages.append({"role": "assistant", "content": answer, "data": res_data})
            st.rerun()
