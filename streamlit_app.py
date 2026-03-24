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
st.title("🛡️ ClóScaoil Engine (v3.1-PRODUCTION)")
st.caption("Manannán Digitization Lab | Surgical OCR Correction & Heuristic Intelligence")

# Initialize Engine
@st.cache_resource
def get_fixer():
    config_path = os.path.join(os.getcwd(), "config", "corrections_dict.json")
    if not os.path.exists(config_path):
        st.error(f"Configuration file not found at {config_path}")
        return None
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    return OCRFixer(config_path, api_key=api_key)

fixer = get_fixer()

# Sidebar Configuration
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

# Main Interface Tabs
tab1, tab2 = st.tabs(["🧪 Single Page Lab", "🚀 Batch Production"])

with tab1:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("📥 Raw OCR Input")
        raw_text = st.text_area(
            "Paste OCR text for processing...", 
            height=400, 
            key="lab_input",
            placeholder="e.g., [l.30]: #\n7 d'dubairt sé... 'manannán' d'éirig..."
        )

    # Logic Execution (Single Page)
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
        processed_text, anomalies, requires_audit = fixer.process_text(
            raw_text, 
            expand_abbreviations=expand_abbr, 
            strict_mode=strict_mode
        )
        
        # Image Sourcing Logic
        page_num = 0
        m = re.search(r'\[l\.(\d+)\]: #', raw_text)
        if m: page_num = int(m.group(1))
        
        # Simplified find logic for Lab
        # Using the helper if we moved it, but let's just do it here for now
        page_str = str(page_num).zfill(3)
        img_path = None
        for name in [f"page_{page_str}.jpg", f"page_{page_str}.png", f"{page_num}.jpg", f"{page_num}.png"]:
            path = os.path.join(scan_dir, name)
            if os.path.exists(path):
                img_path = path
                break
        
        image_bytes = None
        if img_path:
            with col1:
                st.image(img_path, caption=f"Matched Scan: Page {page_num}", use_container_width=True)
                with open(img_path, "rb") as f:
                    image_bytes = f.read()
        else:
            with col1:
                uploaded_file = st.file_uploader(f"📤 Upload Scan (Page {page_num})", type=["jpg", "png"])
                if uploaded_file:
                    image_bytes = uploaded_file.getvalue()
                    st.image(image_bytes, caption=f"Uploaded Scan: Page {page_num}", use_container_width=True)

        final_output_text = st.session_state.vision_corrected_text or processed_text

        # Gating
        if requires_audit and not st.session_state.vision_corrected_text:
            with col1:
                st.warning("⚠️ High Error Density: Many words fail linguistic validation.")
                if image_bytes:
                    if st.button("🔍 Trigger Gemini Visual Audit"):
                        with st.spinner("Analyzing with Gemini 1.5 Pro..."):
                            corrected = fixer.vision_auditor.perform_visual_audit(image_bytes, processed_text)
                            st.session_state.vision_corrected_text = corrected
                            st.rerun()

        if st.session_state.vision_corrected_text:
            with col1:
                if st.button("🔄 Reset to Heuristic Output"):
                    st.session_state.vision_corrected_text = None
                    st.rerun()
        
        with col2:
            st.subheader("🚀 Output Preview")
            if not strict_mode:
                display_text = final_output_text.replace("==", "")
            else:
                import re
                display_text = re.sub(r"==([^=]+)==", r"<mark>\1</mark>", final_output_text)
                display_text = display_text.replace("==", "")
            st.markdown(display_text, unsafe_allow_html=True)
            
            # Anomaly Log (Dashboard within the Lab view)
            if anomalies:
                st.divider()
                st.subheader("📋 Session Analysis")
                for a in anomalies:
                    if a['type'] == 'auto_fixed':
                        st.info(f"**Auto-Fixed:** {a['word']} ➔ {a['fix']}")
                    elif a['type'] == 'harmony_violation':
                        st.error(f"**Harmony Violation:** {a['word']}")
    else:
        with col2:
            st.info("Awaiting input to generate linguistic analysis.")

with tab2:
    st.header("📦 Batch Production Pipeline")
    st.info("Process an entire directory of manuscript chapters with automated Vision Audit policies.")
    
    batch_col1, batch_col2 = st.columns(2)
    with batch_col1:
        batch_input = st.text_input("Input Directory", value=os.path.join(os.getcwd(), "caibidlí"), key="batch_in")
        batch_output = st.text_input("Output Directory", value=os.path.join(os.getcwd(), "production"), key="batch_out")
    
    with batch_col2:
        audit_policy = st.selectbox("Vision Audit Policy", ["manual", "always"], 
                                  help="'always' triggers Gemini Vision automatically if noise > 5.")
        if st.button("▶️ Start Batch Run", type="primary"):
            from ocr_fixer import BatchProcessor
            processor = BatchProcessor(fixer)
            with st.status("Processing Batch...", expanded=True) as status:
                results = processor.process_directory(batch_input, batch_output, scan_dir=scan_dir, audit_policy=audit_policy)
                status.update(label="Batch Complete!", state="complete")
                st.success(f"Processed {len(results)} pages into '{batch_output}'")
                st.dataframe(results)

    st.divider()
    st.header("🏆 Golden Copy Finalizer")
    gold_target = st.text_input("Golden Copy Filename", value="Manannan_Complete_Edition.txt")
    if st.button("✨ Generate Golden Copy"):
        if os.path.exists(batch_output):
            final_path = fixer.generate_golden_copy(batch_output, gold_target)
            st.balloons()
            st.success(f"Golden Copy created: {final_path}")
            with open(final_path, "r", encoding="utf-8") as f:
                st.download_button("📥 Download Golden Copy", f.read(), file_name=gold_target)
        else:
            st.error("Please run the Batch Process first to populate the production folder.")
# Footer
st.divider()
st.markdown(f"<p style='text-align: center; color: grey;'>ClóScaoil Engine Version {OCRFixer.VERSION} | Phase D: Production Mode</p>", unsafe_allow_html=True)
