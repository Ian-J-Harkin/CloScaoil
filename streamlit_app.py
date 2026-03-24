import streamlit as st
import os
import json
from ocr_fixer import OCRFixer
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
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
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
    st.header("📂 Workspace Settings")
    scan_dir = st.text_input(
        "Scan Directory (Images)", 
        value=os.path.join(os.getcwd(), "scans"),
        help="Local path where page images (page_045.jpg or 45.png) are stored."
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
        height=400, 
        placeholder="e.g., [l.30]: #\n7 d'dubairt sé... 'manannán' d'éirig..."
    )

def find_page_image(directory, page_num):
    if not directory or not os.path.exists(directory):
        return None
    page_str = str(page_num).zfill(3)
    possible_names = [f"page_{page_str}.jpg", f"page_{page_str}.png", f"{page_num}.jpg", f"{page_num}.png"]
    for name in possible_names:
        full_path = os.path.join(directory, name)
        if os.path.exists(full_path):
            return full_path
    return None

# Logic Execution
if raw_text and fixer:
    # Track vision audit state & Synchronization (v3.1)
    if "vision_corrected_text" not in st.session_state:
        st.session_state.vision_corrected_text = None
    if "last_raw_text" not in st.session_state:
        st.session_state.last_raw_text = None
        
    if raw_text != st.session_state.last_raw_text:
        st.session_state.vision_corrected_text = None
        st.session_state.last_raw_text = raw_text
    
    # Process text using the engine
    # In Phase C, process_text returns 3 values
    processed_text, anomalies, requires_audit = fixer.process_text(
        raw_text, 
        expand_abbreviations=expand_abbr, 
        strict_mode=strict_mode
    )
    
    # Image Sourcing Logic
    page_num = 0
    m = re.search(r'\[l\.(\d+)\]: #', raw_text)
    if m: page_num = int(m.group(1))
    
    img_path = find_page_image(scan_dir, page_num)
    image_bytes = None
    
    if img_path:
        st.image(img_path, caption=f"Manual Scan: Page {page_num}", use_container_width=True)
        with open(img_path, "rb") as f:
            image_bytes = f.read()
    else:
        uploaded_file = st.file_uploader(f"📤 Upload Scan for Page {page_num}", type=["jpg", "png"])
        if uploaded_file:
            image_bytes = uploaded_file.getvalue()
            st.image(image_bytes, caption=f"Uploaded Scan: Page {page_num}", use_container_width=True)

    # Use vision corrected text if available
    final_output_text = st.session_state.vision_corrected_text or processed_text

    # High Error Density Gating
    if requires_audit and not st.session_state.vision_corrected_text:
        st.warning("⚠️ High Error Density detected. Many words fail linguistic validation.")
        if image_bytes:
            if st.button("🔍 Trigger Gemini Visual Audit", help="Uses Gemini 1.5 Pro to compare OCR with the original scan."):
                with st.spinner("Analyzing scan with Gemini 1.5 Pro..."):
                    corrected = fixer.vision_auditor.perform_visual_audit(image_bytes, processed_text)
                    st.session_state.vision_corrected_text = corrected
                    st.rerun()
        else:
            st.info("💡 Upload a scan to enable Gemini Visual Audit.")

    if st.session_state.vision_corrected_text:
        if st.button("🔄 Reset to Heuristic Output"):
            st.session_state.vision_corrected_text = None
            st.rerun()
    
    with col2:
        st.subheader("🚀 ClóScaoil Output")
        
        if not strict_mode:
            display_text = final_output_text.replace("==", "")
        else:
            import re
            # Convert ==word== to <mark>word</mark>
            display_text = re.sub(r"==([^=]+)==", r"<mark>\1</mark>", final_output_text)
            # v3.1 Sanitation: Strip any residual 'Ghost Markers'
            display_text = display_text.replace("==", "")
            
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
