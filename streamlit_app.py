import streamlit as st
from google import genai

# 使用するモデル（エラーが出たらここを変更）
MODEL = "gemini-3-flash-preview"

# タイトルと説明
st.title("💬 Chatbot")
st.write(
    "GoogleのGeminiを使ったシンプルなチャットボットです。"
    "使うにはGemini APIキーが必要です（[Google AI Studio](https://aistudio.google.com/apikey) で取得できます）。"
)

# APIキーの取得：Secretsに登録してあればそれを使い、なければ画面で入力
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
if not gemini_api_key:
    gemini_api_key = st.text_input("Gemini API Key", type="password")

if not gemini_api_key:
    st.info("Gemini APIキーを入力してください。", icon="🗝️")
else:
    # Geminiクライアントを作成
    client = genai.Client(api_key=gemini_api_key)

    # 会話履歴をセッションに保存
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # これまでの会話を表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 入力欄
    if prompt := st.chat_input("メッセージを入力してください"):

        # ユーザーの入力を保存・表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini用に履歴を変換（Geminiでは assistant ではなく "model" という役割名）
        contents = [
            {
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [{"text": m["content"]}],
            }
            for m in st.session_state.messages
        ]

        # ストリーミングで応答を生成
        def stream_response():
            for chunk in client.models.generate_content_stream(
                model=MODEL,
                contents=contents,
            ):
                if chunk.text:
                    yield chunk.text

        # 応答を表示して保存
        with st.chat_message("assistant"):
            response = st.write_stream(stream_response())
        st.session_state.messages.append({"role": "assistant", "content": response})
