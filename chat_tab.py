import streamlit as st
import openai


def run_chat():
    st.markdown("### 💬 Chat dengan AI")
    st.write("Gunakan fitur ini untuk berkomunikasi dengan model AI (OpenAI). Pastikan kamu memiliki `OPENAI_API_KEY` yang valid.")

    # Opsi mengambil API key dari Streamlit secrets atau input pengguna
    api_key = None
    if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        api_key = st.text_input("Masukkan OpenAI API key (atau simpan di Streamlit secrets)", type="password", key="openai_key_input")

    if not api_key:
        st.info("Masukkan API key untuk mulai chat atau simpan key di Streamlit secrets sebagai OPENAI_API_KEY.")
        return

    openai.api_key = api_key

    # Inisialisasi session state untuk menyimpan percakapan
    if "chat_messages" not in st.session_state:
        # pesan pertama berisi instruksi sistem opsional
        st.session_state["chat_messages"] = [
            {"role": "system", "content": "Kamu adalah asisten yang membantu pengguna menjawab pertanyaan teknis dan non-teknis."}
        ]

    # Pilihan model sederhana
    model = st.selectbox("Pilih model", ["gpt-3.5-turbo"], index=0)

    # Input pesan dari pengguna
    user_input = st.text_input("Ketik pesan untuk AI dan tekan tombol Kirim:", key="chat_user_input")

    col1, col2 = st.columns([1, 3])
    if col1.button("Kirim", key="chat_send_button"):
        if user_input and user_input.strip():
            # tambahkan pesan user ke percakapan
            st.session_state["chat_messages"].append({"role": "user", "content": user_input})

            # panggil OpenAI
            with st.spinner("AI sedang merespon..."):
                try:
                    resp = openai.ChatCompletion.create(
                        model=model,
                        messages=st.session_state["chat_messages"],
                        max_tokens=800,
                        temperature=0.7,
                    )
                    assistant_content = resp.choices[0].message["content"]
                    st.session_state["chat_messages"].append({"role": "assistant", "content": assistant_content})
                except Exception as e:
                    st.error(f"Gagal memanggil API OpenAI: {e}")

    # Tampilkan percakapan
    st.markdown("---")
    st.subheader("Percakapan")
    for msg in st.session_state["chat_messages"]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            st.caption(f"[system] {content}")
        elif role == "user":
            st.markdown(f"**Kamu:** {content}")
        else:
            st.markdown(f"**AI:** {content}")
