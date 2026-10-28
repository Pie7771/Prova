import os
import urllib.parse
from datetime import datetime
from PIL import Image
import streamlit as st

# Configurazione della pagina Streamlit (ottimizzata anche per mobile)
st.set_page_config(
    page_title="Gestionale Fisioterapia", page_icon="🩺", layout="wide"
)

# Cartella per salvare le immagini degli esami caricati
UPLOAD_DIR = "allegati_pazienti"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------------------------------------------
# SISTEMA DI AUTENTICAZIONE / LOGIN
# -------------------------------------------------------------------
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False


def login():
  st.title("🔐 Accedi al Gestionale Fisioterapia")
  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Accedi", use_container_width=True):
      # In fase di produzione qui verificheremo con la tabella User e password criptate
      if username == "admin" and password == "fisio123":
        st.session_state["logged_in"] = True
        st.session_state["user"] = username
        st.rerun()
      else:
        st.error("Username o password errati!")


if not st.session_state["logged_in"]:
  login()
  st.stop()

# -------------------------------------------------------------------
# SIDEBAR / MENU PRINCIPALE
# -------------------------------------------------------------------
st.sidebar.title("🩺 PhysioApp")
st.sidebar.write(f"Utente collegato: **{st.session_state['user']}**")
if st.sidebar.button("Logout"):
  st.session_state["logged_in"] = False
  st.rerun()

menu = st.sidebar.radio(
    "Menu",
    [
        "📋 Elenco Pazienti",
        "➕ Nuovo Paziente",
        "🔍 Scheda Clinica & Valutazione",
        "💬 Modulo WhatsApp",
    ],
)

# -------------------------------------------------------------------
# MOCK DATABASE (In-Memory per testare l'interfaccia)
# -------------------------------------------------------------------
if "pazienti_db" not in st.session_state:
  st.session_state["pazienti_db"] = [
      {
          "id": 1,
          "nome": "Mario",
          "cognome": "Rossi",
          "telefono": "+393401234567",
          "codice_fiscale": "RSSMRA80A01H501Z",
          "professione": "Impiegato / Runner amatoriale",
          "farmaci": "Brufen 600mg al bisogno",
          "pregressi": "Episodio di lombalgia acuta 2 anni fa",
          "motivo_visita": "Gonalgia destra post-corsa",
          "vas": 7,
          "distretto": "Ginocchio",
          "test_ortopedici": "Lachman: Negativo | McMurray: Positivo doloroso",
          "esami_strumentali": "RMN Ginocchio Dx evidenzia lesione menisco mediale",
          "visite_specialistiche": (
              "Visita ortopedica consiglia trattamento conservativo"
          ),
          "immagini": [],
          "link_esterno": "https://drive.google.com/drive/folders/demo",
      }
  ]

# -------------------------------------------------------------------
# 1. ELENCO PAZIENTI
# -------------------------------------------------------------------
if menu == "📋 Elenco Pazienti":
  st.title("📋 Elenco Pazienti")

  ricerca = st.text_input("🔍 Cerca per Nome o Cognome:")
  pazienti_filtrati = [
      p
      for p in st.session_state["pazienti_db"]
      if ricerca.lower() in f"{p['nome']} {p['cognome']}".lower()
  ]

  for idx, p in enumerate(pazienti_filtrati):
    with st.expander(
        f"👤 {p['nome']} {p['cognome']} - Tel: {p['telefono']} | VAS: {p['vas']}/10"
    ):
      col1, col2 = st.columns(2)
      with col1:
        st.write(f"**Codice Fiscale:** {p['codice_fiscale']}")
        st.write(f"**Professione/Sport:** {p['professione']}")
        st.write(f"**Motivo Visita:** {p['motivo_visita']}")
        st.write(f"**Farmaci assunti:** {p['farmaci']}")
      with col2:
        st.write(f"**Problemi passati simili:** {p['pregressi']}")
        st.write(f"**Esami strumentali:** {p['esami_strumentali']}")
        st.write(f"**Visite specialistiche:** {p['visite_specialistiche']}")

# -------------------------------------------------------------------
# 2. NUOVO PAZIENTE & INVII WHATSAPP
# -------------------------------------------------------------------
elif menu == "➕ Nuovo Paziente":
  st.title("➕ Inserisci Nuovo Paziente")

  with st.form("form_nuovo_paziente"):
    col1, col2 = st.columns(2)
    with col1:
      nome = st.text_input("Nome *")
      cognome = st.text_input("Cognome *")
      telefono = st.text_input("Telefono (con prefisso, es. +39345...) *")
    with col2:
      cf = st.text_input("Codice Fiscale")
      professione = st.text_input("Professione / Sport praticato")

    st.subheader("Anamnesi & Valutazione Iniziale")
    motivo = st.text_area("Motivo della visita / Sintomatologia")
    vas = st.slider("Scala VAS del Dolore (0-10)", 0, 10, 5)

    col_a, col_b = st.columns(2)
    with col_a:
      farmaci = st.text_area("Farmaci assunti al momento")
      pregressi = st.text_area("Problemi simili in passato")
    with col_b:
      esami = st.text_area("Referti esami strumentali (RX, RMN, ecc.)")
      visite = st.text_area("Visite specialistiche effettuate")

    distretto = st.selectbox(
        "Distretto Corporeo Principale",
        ["Rachide Cervicale", "Spalla", "Rachide Lombare", "Anca", "Ginocchio", "Caviglia/Piede", "Altro"]
    )
    test_ortopedici = st.text_area("Test Ortopedici Eseguiti ed Esito")

    # CARICAMENTO IMMAGINI ESAMI
    st.subheader("🖼️ Caricamento Allegati & Immagini (RX / RMN / Referti)")
    uploaded_files = st.file_uploader(
        "Scegli una o più immagini di esami",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )
    link_esterno = st.text_input(
        "Link esterno opzionale per RMN (es. Google Drive/PACS):"
    )

    submit = st.form_submit_button("Salva Paziente")

    if submit and nome and cognome:
      salvati_file = []
      if uploaded_files:
        for file in uploaded_files:
          file_path = os.path.join(UPLOAD_DIR, f"{nome}_{cognome}_{file.name}")
          with open(file_path, "wb") as f:
            f.write(file.getbuffer())
          salvati_file.append(file_path)

      nuovo_p = {
          "id": len(st.session_state["pazienti_db"]) + 1,
          "nome": nome,
          "cognome": cognome,
          "telefono": telefono,
          "codice_fiscale": cf,
          "professione": professione,
          "farmaci": farmaci,
          "pregressi": pregressi,
          "motivo_visita": motivo,
          "vas": vas,
          "distretto": distretto,
          "test_ortopedici": test_ortopedici,
          "esami_strumentali": esami,
          "visite_specialistiche": visite,
          "immagini": salvati_file,
          "link_esterno": link_esterno,
      }
      st.session_state["pazienti_db"].append(nuovo_p)
      st.success(f"Paziente {nome} {cognome} salvato con successo!")

# -------------------------------------------------------------------
# 3. SCHEDA CLINICA & VISUALIZZATORE IMMAGINI
# -------------------------------------------------------------------
elif menu == "🔍 Scheda Clinica & Valutazione":
  st.title("🔍 Visualizzatore Cartella Clinica & Immagini")

  nomi_pazienti = [
      f"{p['nome']} {p['cognome']}" for p in st.session_state["pazienti_db"]
  ]
  scelta = st.selectbox("Seleziona Paziente:", nomi_pazienti)

  if scelta:
    paziente = next(
        p
        for p in st.session_state["pazienti_db"]
        if f"{p['nome']} {p['cognome']}" == scelta
    )

    st.subheader(f"Scheda di {paziente['nome']} {paziente['cognome']}")

    tab1, tab2, tab3 = st.tabs(
        ["📝 Valutazione Iniziale", "🖼️ Immagini RMN / Lastre", "💬 WhatsApp Fast"]
    )

    with tab1:
      col1, col2 = st.columns(2)
      with col1:
        st.info(f"**VAS Dolore:** {paziente['vas']}/10")
        st.write(f"**Motivo della Visita:** {paziente['motivo_visita']}")
        st.write(f"**Distretto Corporeo:** {paziente['distretto']}")
        st.write(f"**Test Ortopedici:**\n{paziente['test_ortopedici']}")
      with col2:
        st.write(f"**Farmaci:** {paziente['farmaci']}")
        st.write(f"**Problemi Simili Passati:** {paziente['pregressi']}")
        st.write(
            f"**Referti Esami Strumentali:** {paziente['esami_strumentali']}"
        )
        st.write(
            f"**Visite Specialistiche:** {paziente['visite_specialistiche']}"
        )

    with tab2:
      st.write("### 🖼️ Immagini Ingestite nel Gestionale")
      if paziente["immagini"]:
        for img_path in paziente["immagini"]:
          if os.path.exists(img_path):
            image = Image.open(img_path)
            st.image(
                image,
                caption=os.path.basename(img_path),
                use_container_width=True,
            )
      else:
        st.warning(
            "Nessuna immagine caricata direttamente per questo paziente."
        )

      if paziente["link_esterno"]:
        st.markdown(
            f"🔗 **Link esterno RMN/PACS:** [{paziente['link_esterno']}]({paziente['link_esterno']})"
        )

    with tab3:
      st.write("### 📲 Invia Modulo Anamnesi su WhatsApp")
      st.write(
          "Invia al paziente un messaggio precompilato con il link al modulo da compilare prima della visita."
      )

      link_modulo_preliminare = (
          "https://tui-app.com/modulo-anamnesi?id=" + str(paziente["id"])
      )
      testo_messaggio = (
          f"Buongiorno {paziente['nome']},\n\n"
          "Per preparare al meglio la tua prima visita di fisioterapia, ti chiedo la cortesia di compilare questo breve modulo preliminare:\n"
          f"{link_modulo_preliminare}\n\n"
          "Grazie e a presto in studio!"
      )

      testo_encoded = urllib.parse.quote(testo_messaggio)
      url_wa = f"https://wa.me/{paziente['telefono']}?text={testo_encoded}"

      st.markdown(
          f'<a href="{url_wa}" target="_blank">'
          '<button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-size:16px; border-radius:8px; cursor:pointer;">'
          "📲 Apri WhatsApp e Invia Modulo</button></a>",
          unsafe_allow_html=True,
      )

# -------------------------------------------------------------------
# 4. PAGINA DEDICATA WHATSAPP
# -------------------------------------------------------------------
elif menu == "💬 Modulo WhatsApp":
  st.title("💬 Invio Rapido Modulo Pre-Visita WhatsApp")
  st.write(
      "Usa questa funzione per mandare al volo il modulo preliminare a un nuovo contatto anche prima di inserirlo nell'anagrafica completa."
  )

  tel_rapido = st.text_input("Numero del paziente (es. +393401234567)")
  nome_rapido = st.text_input("Nome del paziente")

  if tel_rapido and nome_rapido:
    msg_rapido = (
        f"Buongiorno {nome_rapido},\n\n"
        "Ecco il modulo da compilare prima della nostra visita di fisioterapia:\n"
        "https://tui-app.com/modulo-preliminare\n\nGrazie!"
    )
    url_wa_rapido = (
        f"https://wa.me/{tel_rapido}?text={urllib.parse.quote(msg_rapido)}"
    )
    st.markdown(
        f'<a href="{url_wa_rapido}" target="_blank">'
        '<button style="background-color:#25D366; color:white; border:none; padding:12px 20px; font-size:16px; border-radius:8px; cursor:pointer;">'
        "📲 Spedisci su WhatsApp</button></a>",
        unsafe_allow_html=True,
    )

