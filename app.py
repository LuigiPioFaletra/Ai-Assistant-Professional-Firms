import streamlit as st
import requests
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def ask_ai(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 150
                }
            },
            timeout=600
        )
        return response.json()["response"].strip()
    except requests.exceptions.Timeout:
        return "Errore: il modello AI sta impiegando troppo tempo."
    except requests.exceptions.ConnectionError:
        return "Errore: Ollama non è in esecuzione. Avvia 'ollama run llama3'."
    except Exception as e:
        return f"Errore generico: {str(e)}"


def classify_request(user_text):
    text_lower = user_text.lower()

    # Rule-based classification (more reliable)
    if any(word in text_lower for word in ["fallimento", "fallimentare", "contenzioso", "causa", "tribunale"]):
        return "Legale"
    if any(word in text_lower for word in ["tasse", "dichiarazione", "iva", "fiscale", "tributi"]):
        return "Fiscale"

    # Fallback to AI
    prompt = f"""
    Classifica la richiesta in UNA SOLA categoria tra:
    Fiscale, Legale, Amministrativa.
    Rispondi SOLO con una parola.
    Richiesta: "{user_text}"
    """
    return ask_ai(prompt)


def generate_response(user_text, category):
    prompt = f"""
    Sei un assistente di uno studio professionale italiano.
    Scrivi una risposta al cliente rispettando TUTTE queste regole:
    - massimo 3 righe
    - linguaggio formale
    - diretto, concreto e sicuro
    - evita parole come "potremmo", "forse"
    - evita ripetizioni e frasi ridondanti
    - non fornire scadenze legali o istruzioni vincolanti
    - niente introduzioni lunghe
    - niente firme
    - niente spiegazioni inutili
    Rispondi SOLO in italiano.
    Categoria: {category}
    Richiesta: "{user_text}"
    """
    return ask_ai(prompt)


def assign_priority(user_text):
    text_lower = user_text.lower()
    if "urgente" in text_lower or "subito" in text_lower:
        return "Alta"
    elif "entro" in text_lower:
        return "Media"
    return "Normale"


st.set_page_config(page_title="Assistente AI", layout="centered")
st.title("Assistente AI per Studio Professionale")
user_text = st.text_area("Inserisci la richiesta del cliente:")
col1, col2 = st.columns(2)
with col1:
    process_button = st.button("Elabora richiesta")
with col2:
    if st.button("Reset"):
        st.rerun()
if process_button:
    if user_text.strip() == "":
        st.warning("Inserisci una richiesta.")
    else:
        with st.spinner("Elaborazione in corso..."):
            category = classify_request(user_text)
            if category not in ["Fiscale", "Legale", "Amministrativa"]:
                category = "Non classificata"
            category = category.strip().capitalize()
            priority = assign_priority(user_text)
            response = generate_response(user_text, category)
        st.subheader("Risultato")
        st.write(f"**Categoria:** {category}")
        st.write(f"**Priorità:** {priority}")
        st.write("**Risposta:**")
        if "Errore" in response:
            st.error(response)
        else:
            st.write(response)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n--- {timestamp} ---\n")
            f.write(f"Richiesta: {user_text}\n")
            f.write(f"Categoria: {category}\n")
            f.write(f"Priorità: {priority}\n")
            f.write(f"Risposta:\n{response}\n")
        st.success("Richiesta salvata correttamente")
