import streamlit as st
import openai
import os
import json
import re


HISTORY_DIR = "chat_history"


def _safe_username(name: str) -> str:
    # sanitize for filesystem
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)[:64]


def _load_history(username: str):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    path = os.path.join(HISTORY_DIR, f"{_safe_username(username)}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _save_history(username: str, messages):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    path = os.path.join(HISTORY_DIR, f"{_safe_username(username)}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # non-fatal
        st.error(f"Gagal menyimpan history chat: {e}")


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

    # Determine user for chat history
    username = st.session_state.get("user", "anonymous")

    # Inisialisasi session state untuk menyimpan percakapan
    if "chat_messages" not in st.session_state:
        # try load from disk first
        loaded = _load_history(username)
        if isinstance(loaded, list) and len(loaded) > 0:
            st.session_state["chat_messages"] = loaded
        else:
            st.session_state["chat_messages"] = [
                {"role": "system", "content": "Kamu adalah asisten yang membantu pengguna menjawab pertanyaan teknis dan non-teknis."}
            ]

    # Controls: model and clear history
    cols = st.columns([3, 1])
    model = cols[0].selectbox("Pilih model", ["gpt-3.5-turbo"], index=0)
    if cols[1].button("Hapus history lokal"):
        st.session_state["chat_messages"] = [{"role": "system", "content": "Kamu adalah asisten yang membantu pengguna menjawab pertanyaan teknis dan non-teknis."}]
        try:
            path = os.path.join(HISTORY_DIR, f"{_safe_username(username)}.json")
            if os.path.exists(path):
                os.remove(path)
                st.success("History lokal dihapus.")
        except Exception as e:
            st.error(f"Gagal menghapus history: {e}")

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
                    # compat with response shape
                    assistant_content = None
                    if hasattr(resp.choices[0], 'message'):
                        assistant_content = resp.choices[0].message["content"]
                    else:
                        assistant_content = resp.choices[0].text

                    st.session_state["chat_messages"].append({"role": "assistant", "content": assistant_content})

                    # save history to disk
                    try:
                        _save_history(username, st.session_state["chat_messages"])
                    except Exception:
                        pass

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
