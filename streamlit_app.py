import streamlit as st
import subprocess
import os
import sys
import json
import tkinter as tk
from tkinter import filedialog

# Configuration - Targeted at the local project structure
DEFAULT_DATA_ROOT = r"C:\github\Manannan"
DEFAULT_UTILS_ROOT = r"C:\github\ManannanUtils"

st.set_page_config(
    page_title="Manannán Digitization Lab", 
    page_icon="🛸",
    layout="wide"
)

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://img.icons8.com/wired/64/000000/ufo.png", width=50)
    st.title("⚙️ Workspace Settings")
    
    st.session_state.data_root = st.text_input("📊 Data Root", value=st.session_state.get('data_root', DEFAULT_DATA_ROOT))
    st.session_state.utils_root = st.text_input("🛠️ Toolkit Root", value=st.session_state.get('utils_root', DEFAULT_UTILS_ROOT))
    
    st.divider()
    st.markdown("### 🔍 System Info")
    st.write(f"Python: `{sys.version.split(' ')[0]}`")
    st.write(f"Venv: `{os.path.basename(sys.prefix)}`")

UTILS_DIR = os.path.join(st.session_state.utils_root, "python-utils")

# Custom Styling for Premium Wizard Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button { border-radius: 8px; height: 3em; transition: all 0.3s ease; font-weight: bold; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,255,127,0.3); border-color: #00ff7f; }
    
    /* Wizard Steps styling */
    .step-container { display: flex; justify-content: space-between; margin-bottom: 2rem; padding: 1rem; background: #1a1c24; border-radius: 12px; }
    .step { flex: 1; text-align: center; padding: 10px; border-bottom: 4px solid #333; color: #888; transition: all 0.5s; position: relative;}
    .step-active { border-bottom: 4px solid #00ff7f; color: #00ff7f; font-weight: bold; }
    .step-complete { border-bottom: 4px solid #4a90e2; color: #4a90e2; }
    .step-icon { font-size: 1.2rem; margin-bottom: 5px; }
    
    /* Report Table */
    .report-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    .report-table th { background: #1a1c24; color: #00ff7f; padding: 10px; text-align: left; }
    .report-table td { padding: 10px; border-bottom: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛸 Manannán Digitization Lab")

# --- Session State Persistence ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None
if 'ocr_completed' not in st.session_state:
    st.session_state.ocr_completed = False
if 'modernization_completed' not in st.session_state:
    st.session_state.modernization_completed = False

# --- Wizard Logic ---
def go_to_step(n):
    st.session_state.step = n

def select_file():
    # Attempt native dialog
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askopenfilename(
            initialdir=os.path.join(st.session_state.data_root, "caibidlí", "old-orthography"),
            title="Select Chapter for Processing",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        root.destroy()
        return path
    except Exception as e:
        # Fallback for headless or error
        st.error(f"Native dialog failed: {e}")
        return None

# --- Wizard UI Component ---
stages = [
    ("📁 Selection", 1),
    ("✨ OCR Repair", 2),
    ("📖 Modernize", 3),
    ("✅ Verification", 4)
]

def render_wizard_header():
    cols = st.columns(len(stages))
    for i, (label, step_val) in enumerate(stages):
        status_class = ""
        if st.session_state.step == step_val: status_class = "step-active"
        elif st.session_state.step > step_val: status_class = "step-complete"
        
        with cols[i]:
            st.markdown(f"""
                <div class="step {status_class}">
                    <div class="step-icon">{label.split(' ')[0]}</div>
                    <div>{label.split(' ')[1]}</div>
                </div>
            """, unsafe_allow_html=True)

render_wizard_header()
st.divider()

# --- STAGE 1: Selection ---
if st.session_state.step == 1:
    st.subheader("Stage 1: Chapter Source Selection")
    st.info("Select a raw OCR output file from the `old-orthography` directory.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Active File", value=st.session_state.selected_file or "", disabled=True, placeholder="Please browse for a file...")
    with col2:
        if st.button("📁 Browse Local Files", use_container_width=True):
            path = select_file()
            if path:
                st.session_state.selected_file = path
                st.session_state.ocr_completed = False
                st.session_state.modernization_completed = False
                st.toast(f"Selected: {os.path.basename(path)}")
                st.rerun()

    if st.session_state.selected_file:
        if st.button("Proceed to OCR Repair ➡️", type="primary"):
            go_to_step(2)
            st.rerun()

# --- STAGE 2: OCR Repair ---
elif st.session_state.step == 2:
    st.subheader("Stage 2: OCR Heuristics & Repair")
    st.write(f"Working on: `{os.path.basename(st.session_state.selected_file)}`")
    
    if st.button("✨ Run OCR Fixer", type="primary", use_container_width=True):
        report_path = os.path.join(UTILS_DIR, "temp_report.json")
        cmd = [
            sys.executable, 
            os.path.join(UTILS_DIR, "ocr_fixer.py"), 
            st.session_state.selected_file, 
            "--report", report_path
        ]
        
        with st.spinner("Executing linguistic repair engine..."):
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=UTILS_DIR)
            if result.returncode == 0:
                st.session_state.ocr_completed = True
                st.success("OCR Fixer successful! Review the report below.")
                if result.stderr:
                    with st.expander("Technical Logs"):
                        st.code(result.stderr)
            else:
                st.error("Engine failure:")
                st.code(result.stderr)

    if st.session_state.ocr_completed:
        # Load report
        report_file = os.path.join(UTILS_DIR, "temp_report.json")
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                matches = report_data.get("ambiguous_matches", [])
                if matches:
                    st.warning(f"Found {len(matches)} items requiring human attention.")
                    st.table([{"Line": m['line'], "Word": m['word'], "Context": m['context']} for m in matches])
                else:
                    st.success("No ambiguous patterns detected.")
        
        st.divider()
        if st.button("Proceed to Modernization ➡️", type="primary"):
            go_to_step(3)
            st.rerun()

    if st.button("⬅️ Back to Selection"):
        go_to_step(1)
        st.rerun()

# --- STAGE 3: Modernization ---
elif st.session_state.step == 3:
    st.subheader("Stage 3: Orthographic Modernization")
    st.write("Converting Cló Gaelach (dotted) characters to modern 'h' equivalents.")
    
    output_path = st.session_state.selected_file.replace("old-orthography", "new-orthography")
    
    if st.button("🛠️ Run Modernizer", type="primary", use_container_width=True):
        cmd = [
            sys.executable, 
            os.path.join(UTILS_DIR, "convert_orthography.py"), 
            st.session_state.selected_file, 
            "--output", output_path
        ]
        
        with st.spinner("Performing character mapping..."):
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=UTILS_DIR)
            if result.returncode == 0:
                st.session_state.modernization_completed = True
                st.success(f"Modernization complete! Saved to:\n`{output_path}`")
            else:
                st.error("Modernizer failed:")
                st.code(result.stderr)

    if st.session_state.modernization_completed:
        if st.button("Proceed to Verification ➡️", type="primary"):
            go_to_step(4)
            st.rerun()

    if st.button("⬅️ Back to OCR Repair"):
        go_to_step(2)
        st.rerun()

# --- STAGE 4: Verification ---
elif st.session_state.step == 4:
    st.subheader("Stage 4: Final Verification")
    st.balloons()
    st.success("Processing complete for this chapter.")
    
    output_dir = os.path.join(st.session_state.data_root, "caibidlí", "new-orthography")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📂 Open Output Folder", use_container_width=True):
            if os.path.exists(output_dir):
                os.startfile(output_dir)
            else:
                st.error("Folder not found.")
    
    with col2:
        if st.button("🔄 Restart Pipeline", use_container_width=True):
            st.session_state.step = 1
            st.session_state.selected_file = None
            st.session_state.ocr_completed = False
            st.session_state.modernization_completed = False
            st.rerun()

    st.divider()
    st.markdown("### Next Steps")
    st.markdown("- Perform manual proofreading of the output file.")
    st.markdown("- Add any recurring errors to `corrections_dict.json` using the Fine-Tuning utility.")
