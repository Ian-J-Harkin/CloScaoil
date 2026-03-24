import streamlit as st
import os
import json
from ocr_fixer import OCRFixer
from dotenv import load_dotenv

load_dotenv()

# Page Configuration - Premium Aesthetics
st.set_page_config(
    page_title="ClóScaoil Engine v2.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stTextArea textarea {
        background-color: #1a1c24 !important;
        color: #00ff41 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    .stMarkdown p, .stMarkdown span {
        font-size: 1.1rem;
    }
    mark {
        background-color: rgba(255, 75, 75, 0.3);
        color: white;
        border-radius: 4px;
        padding: 0 4px;
    }
</style>
""", unsafe_allow_html=True)

# Title & Description
st.title("🛡️ ClóScaoil Engine (v2.0)")
st.caption("Manannán Digitization Lab | Surgical OCR Correction & Heuristic Intelligence")

# Initialize Engine
@st.cache_resource
def get_fixer():
    config_path = os.path.join("config", "corrections_dict.json")
    if not os.path.exists(config_path):
        st.error(f"Configuration file not found at {config_path}")
        return None
    api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
    return OCRFixer(config_path, api_key=api_key)

fixer = get_fixer()

# Sidebar Configuration & Anomaly Dashboard
with st.sidebar:
    st.header("⚙️ Configuration")
    expand_abbr = st.toggle(
        "Expand Abbreviations", 
        value=False, 
        help="If enabled, Tironian Et (7 or >) becomes 'agus'. Otherwise, it becomes ⁊."
    )
    strict_mode = st.toggle(
        "Strict Linguistic Mode", 
        value=True, 
        help="Highlight words that violate Vowel Harmony patterns (e.g., broad vowel matched with slender vowel)."
    )
    
    st.divider()
    st.header("🔍 Anomaly Dashboard")
    # Placeholder for the dynamic anomaly list
    anomaly_placeholder = st.empty()

# Main Interface Layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📥 Raw OCR Input")
    raw_text = st.text_area(
        "Paste OCR text for processing...", 
        height=600, 
        placeholder="e.g., [l.30]: #\n7 d'dubairt sé... 'manannán' d'éirig..."
    )

# Logic Execution
if raw_text and fixer:
    # Process text using the engine we just verified
    processed_text, anomalies = fixer.process_text(
        raw_text, 
        expand_abbreviations=expand_abbr, 
        strict_mode=strict_mode
    )
    
    with col2:
        st.subheader("🚀 ClóScaoil Output")
        
        if not strict_mode:
            display_text = processed_text.replace("==", "")
        else:
            import re
            # Convert ==word== to <mark>word</mark> for all occurrences
            display_text = re.sub(r"==([^=]+)==", r"<mark>\1</mark>", processed_text)
            
        st.markdown(display_text, unsafe_allow_html=True)
        
    # Populate the Anomaly Sidebar Dashboard
    with anomaly_placeholder.container():
        harmony_violations = [a for a in anomalies if a['type'] == 'harmony_violation']
        ambiguous_matches = [a for a in anomalies if a['type'] == 'ambiguous']
        
        if harmony_violations:
            st.warning(f"⚠️ {len(harmony_violations)} Harmony Violations")
            for v in harmony_violations[:20]: # Show top 20 for performance
                with st.expander(f"Violation: {v['word']}"):
                    st.write(f"**Context:** _{v['context']}_")
                    st.write(f"**Line:** {v['line']}")
            if len(harmony_violations) > 20:
                st.info(f"Showing first 20 of {len(harmony_violations)} violations.")
        else:
            st.success("No Vowel Harmony violations detected.")

        if ambiguous_matches:
            st.divider()
            st.error(f"❓ {len(ambiguous_matches)} Ambiguous Matches")
            for m in ambiguous_matches:
                st.selectbox(
                    f"Resolve: {m['word']} (Line {m['line']})", 
                    m['options'], 
                    key=f"amb_{m['line']}_{m['word']}_{hash(m['context'])}"
                )
        
        # New: 🤖 Automated Resolutions section
        auto_fixed = [a for a in anomalies if a['type'] == 'auto_fixed']
        if auto_fixed:
            st.divider()
            st.header("🤖 Automated Resolutions")
            for f in auto_fixed:
                st.success(f"[Line {f['line']}]: Fixed '{f['word']}' -> '{f['fix']}'.")
else:
    with col2:
        st.info("Final output will be displayed here in real-time as you paste text.")
    with anomaly_placeholder:
        st.info("Awaiting input to generate linguistic analysis.")

# Footer
st.divider()
st.markdown(f"<p style='text-align: center; color: grey;'>ClóScaoil Engine Version {OCRFixer.VERSION} | Phase A Phase Complete</p>", unsafe_allow_html=True)
