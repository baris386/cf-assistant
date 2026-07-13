import os
import requests
import random
from bs4 import BeautifulSoup
import streamlit as st
from dotenv import load_dotenv
from google import genai
import markdown

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Page Configuration
st.set_page_config(page_title="CF Assistant — CP Coach", page_icon="🤖", layout="wide")

# ================= KRYPHOS CYBER THEME (TOTAL RED BAN) =================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Cyberpunk Theme Background with Subtle Grid */
    .stApp {
        background-color: #060814 !important;
        background-image: 
            radial-gradient(at 10% 20%, rgba(0, 243, 255, 0.05) 0px, transparent 50%),
            radial-gradient(at 90% 80%, rgba(157, 0, 255, 0.05) 0px, transparent 50%),
            linear-gradient(rgba(6, 8, 20, 0.85), rgba(6, 8, 20, 0.95)),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px;
        background-attachment: fixed;
        color: #cbd5e1;
        font-family: 'Inter', sans-serif;
    }
    
    /* Screen bounds */
    .block-container {
        max-width: 1250px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Cyberpunk Titles */
    h1 {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #00f3ff 0%, #9d00ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        margin-bottom: 2rem !important;
        text-shadow: 0 0 20px rgba(0, 243, 255, 0.25);
    }
    
    h2 {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #00f3ff !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 1rem !important;
        margin-bottom: 1.2rem !important;
        border-left: 3px solid #9d00ff;
        padding-left: 10px;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
    }
    
    /* Glassmorphic inputs with cyber neon outline */
    .stTextInput>div>div>input {
        background-color: rgba(9, 12, 21, 0.75) !important;
        color: #00f3ff !important;
        border: 1px solid rgba(0, 243, 255, 0.25) !important;
        border-radius: 4px !important;
        padding: 12px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(8px);
        box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.5) !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #9d00ff !important;
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.4), inset 0 0 5px rgba(0, 0, 0, 0.5) !important;
        outline: none !important;
        background-color: rgba(9, 12, 21, 0.9) !important;
    }
    
    div[data-baseweb="input"] {
        background-color: transparent !important;
        border-image: none !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #9d00ff !important;
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.4) !important;
    }
    
    /* Cyber Slider default styles */
    div[data-testid="stSlider"] div[role="slider"] + div {
        background: linear-gradient(90deg, #00f3ff, #9d00ff) !important;
    }
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #9d00ff !important;
        border: 2px solid #060814 !important;
        box-shadow: 0 0 10px rgba(157, 0, 255, 0.8) !important;
    }
    div[data-testid="stSlider"] span {
        color: #00f3ff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.8rem !important;
    }
    div[data-testid="stSlider"] div {
        background-color: transparent !important;
    }
    div[data-testid="stSlider"] > div > div > div {
        background-color: rgba(26, 31, 44, 0.5) !important;
    }

    /* === CHAT SYSTEM === */
    .chat-container {
        max-height: 520px;
        overflow-y: auto;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        background: rgba(17, 22, 37, 0.4);
        border: 1px solid rgba(0, 243, 255, 0.15);
        border-radius: 8px;
        scrollbar-width: thin;
        scrollbar-color: #9d00ff rgba(17, 22, 37, 0.4);
        backdrop-filter: blur(10px);
    }
    
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: rgba(17, 22, 37, 0.4);
        border-radius: 4px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: #9d00ff;
        border-radius: 4px;
        box-shadow: 0 0 5px rgba(157, 0, 255, 0.5);
    }
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #00f3ff;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.8);
    }
    
    .chat-row {
        display: flex;
        width: 100%;
    }
    
    .user-row {
        justify-content: flex-end;
    }
    
    .assistant-row {
        justify-content: flex-start;
    }
    
    .chat-bubble {
        max-width: 80%;
        padding: 12px 16px;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        gap: 12px;
        align-items: flex-start;
    }
    
    .user-bubble {
        background-color: rgba(157, 0, 255, 0.15) !important;
        border: 1px solid rgba(157, 0, 255, 0.4) !important;
        border-bottom-right-radius: 4px;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(157, 0, 255, 0.1);
    }
    
    .assistant-bubble {
        background-color: rgba(0, 243, 255, 0.05) !important;
        border: 1px solid rgba(0, 243, 255, 0.2) !important;
        border-left: 4px solid #00f3ff !important;
        border-bottom-left-radius: 4px;
        color: #cbd5e1 !important;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.05);
    }

    .chat-avatar {
        font-size: 1.25rem;
        user-select: none;
        flex-shrink: 0;
        margin-top: 1px;
        filter: drop-shadow(0 0 5px rgba(0, 243, 255, 0.5));
    }
    
    .chat-message-content {
        flex-grow: 1;
        overflow-wrap: break-word;
        word-break: break-word;
    }

    .chat-message-content p {
        margin: 0 0 8px 0 !important;
    }
    .chat-message-content p:last-child {
        margin-bottom: 0 !important;
    }
    .chat-message-content code {
        background-color: #090c15 !important;
        color: #00f3ff !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 0.9em !important;
    }
    .chat-message-content pre {
        background-color: #090c15 !important;
        padding: 12px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(0, 243, 255, 0.1) !important;
        overflow-x: auto !important;
        margin: 8px 0 !important;
    }
    .chat-message-content pre code {
        background-color: transparent !important;
        color: #e6edf3 !important;
        padding: 0 !important;
        border-radius: 0 !important;
        font-size: 0.85em !important;
    }
    .chat-message-content ul, .chat-message-content ol {
        margin: 0 0 8px 0 !important;
        padding-left: 20px !important;
    }
    
    /* Cyber buttons styling */
    .stButton>button {
        background-color: rgba(10, 15, 30, 0.7) !important;
        color: #ffffff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 4px !important;
        padding: 8px 16px;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(8px);
        position: relative;
    }
    .stButton>button:hover {
        border-color: #9d00ff !important;
        color: #9d00ff !important;
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.4);
        background-color: rgba(157, 0, 255, 0.05) !important;
        transform: translateY(-2px);
    }
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Cyber Notifications style */
    div[data-testid="stAlert"], .stAlert {
        background-color: rgba(10, 15, 30, 0.75) !important;
        border: 1px solid rgba(0, 243, 255, 0.25) !important;
        border-left: 4px solid #00f3ff !important;
        color: #cbd5e1 !important;
        border-radius: 8px !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.1) !important;
        padding: 0.75rem 1rem !important;
    }
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div, div[data-testid="stAlert"] label {
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stAlert"] svg {
        color: #00f3ff !important;
        fill: #00f3ff !important;
    }

    /* Custom themed notices */
    .cyber-notice {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 0.45rem 0 1rem;
        font-size: 0.88rem;
        line-height: 1.55;
        backdrop-filter: blur(10px);
        border: 1px solid;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    .cyber-notice-icon {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        flex-shrink: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        font-size: 0.72rem;
        letter-spacing: 0;
    }
    .cyber-notice-body {
        flex: 1;
        color: #e2e8f0;
    }
    .cyber-notice-body strong {
        color: #00f3ff;
        font-weight: 600;
    }
    .cyber-notice-body a, .cyber-link {
        color: #00f3ff !important;
        text-decoration: none;
        font-weight: 600;
        border-bottom: 1px solid rgba(0, 243, 255, 0.35);
        transition: color 0.2s ease, border-color 0.2s ease;
    }
    .cyber-notice-body code {
        background: rgba(9, 12, 21, 0.8);
        color: #00f3ff;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85em;
        border: 1px solid rgba(0, 243, 255, 0.2);
    }
    .cyber-notice-body a:hover, .cyber-link:hover {
        color: #9d00ff !important;
        border-bottom-color: rgba(157, 0, 255, 0.55);
    }
    .cyber-notice-success {
        background: rgba(0, 243, 255, 0.07);
        border-color: rgba(0, 243, 255, 0.35);
        box-shadow: 0 0 18px rgba(0, 243, 255, 0.08);
    }
    .cyber-notice-success .cyber-notice-icon {
        background: rgba(0, 243, 255, 0.15);
        color: #00f3ff;
        border: 1px solid rgba(0, 243, 255, 0.4);
    }
    .cyber-notice-error {
        background: rgba(255, 77, 109, 0.08);
        border-color: rgba(255, 77, 109, 0.4);
        box-shadow: 0 0 18px rgba(255, 77, 109, 0.1);
    }
    .cyber-notice-error .cyber-notice-icon {
        background: rgba(255, 77, 109, 0.15);
        color: #ff4d6d;
        border: 1px solid rgba(255, 77, 109, 0.45);
    }
    .cyber-notice-warning {
        background: rgba(251, 191, 36, 0.08);
        border-color: rgba(251, 191, 36, 0.38);
        box-shadow: 0 0 18px rgba(251, 191, 36, 0.08);
    }
    .cyber-notice-warning .cyber-notice-icon {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.45);
    }
    .cyber-notice-info {
        background: rgba(157, 0, 255, 0.08);
        border-color: rgba(157, 0, 255, 0.35);
        box-shadow: 0 0 18px rgba(157, 0, 255, 0.08);
    }
    .cyber-notice-info .cyber-notice-icon {
        background: rgba(157, 0, 255, 0.15);
        color: #c084fc;
        border: 1px solid rgba(157, 0, 255, 0.45);
    }

    /* Solver action buttons */
    .solver-action-label {
        font-size: 0.78rem;
        color: #64748b;
        margin: 0.75rem 0 0.55rem;
        letter-spacing: 0.3px;
    }
    [data-testid="column"] .element-container:has(.cyber-action-hint) + .element-container [data-testid="stButton"] > button {
        background: linear-gradient(135deg, rgba(0, 243, 255, 0.14), rgba(0, 243, 255, 0.04)) !important;
        border: 1px solid rgba(0, 243, 255, 0.55) !important;
        color: #00f3ff !important;
        box-shadow: 0 0 14px rgba(0, 243, 255, 0.18) !important;
        text-transform: none !important;
        letter-spacing: 0.3px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        min-height: 44px !important;
    }
    [data-testid="column"] .element-container:has(.cyber-action-hint) + .element-container [data-testid="stButton"] > button:hover {
        background: rgba(0, 243, 255, 0.18) !important;
        border-color: #00f3ff !important;
        color: #ffffff !important;
        box-shadow: 0 0 22px rgba(0, 243, 255, 0.4) !important;
        transform: translateY(-2px);
    }
    [data-testid="column"] .element-container:has(.cyber-action-editorial) + .element-container [data-testid="stButton"] > button {
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.16), rgba(157, 0, 255, 0.05)) !important;
        border: 1px solid rgba(157, 0, 255, 0.55) !important;
        color: #c084fc !important;
        box-shadow: 0 0 14px rgba(157, 0, 255, 0.2) !important;
        text-transform: none !important;
        letter-spacing: 0.3px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        min-height: 44px !important;
    }
    [data-testid="column"] .element-container:has(.cyber-action-editorial) + .element-container [data-testid="stButton"] > button:hover {
        background: rgba(157, 0, 255, 0.22) !important;
        border-color: #9d00ff !important;
        color: #ffffff !important;
        box-shadow: 0 0 22px rgba(157, 0, 255, 0.45) !important;
        transform: translateY(-2px);
    }

    /* Cyber chat input styling */
    div[data-testid="stChatInput"] {
        background-color: rgba(17, 22, 37, 0.8) !important;
        border: 1px solid rgba(0, 243, 255, 0.3) !important;
        border-radius: 4px !important;
        padding: 4px 12px !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.15) !important;
        backdrop-filter: blur(8px);
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #ffffff !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stChatInput"] button {
        border-radius: 4px !important;
        background-color: #9d00ff !important;
        color: #ffffff !important;
        width: 36px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-left: 8px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 0 8px rgba(157, 0, 255, 0.5) !important;
    }
    div[data-testid="stChatInput"] button:hover {
        background-color: #00f3ff !important;
        color: #060814 !important;
        box-shadow: 0 0 12px rgba(0, 243, 255, 0.8) !important;
    }
    
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {
        display: none !important;
    }

    /* Hero & layout */
    .hero-banner {
        background: linear-gradient(135deg, rgba(0, 243, 255, 0.08) 0%, rgba(157, 0, 255, 0.08) 100%);
        border: 1px solid rgba(0, 243, 255, 0.2);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.75rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    }
    .hero-banner h1 {
        margin-bottom: 0.4rem !important;
        font-size: 2rem !important;
    }
    .hero-tagline {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
        line-height: 1.5;
    }
    .hero-tagline strong {
        color: #00f3ff;
    }

    /* Section cards */
    .section-card {
        background: rgba(17, 22, 37, 0.55);
        border: 1px solid rgba(0, 243, 255, 0.12);
        border-radius: 10px;
        padding: 1.1rem 1.25rem 0.85rem;
        margin-bottom: 0.65rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: border-color 0.25s ease;
    }
    .section-spacer {
        margin-bottom: 1.75rem;
    }
    .section-card:hover {
        border-color: rgba(157, 0, 255, 0.25);
    }
    .section-card .section-label {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #9d00ff;
        margin-bottom: 0.15rem;
    }
    .section-card .section-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #00f3ff;
        margin: 0 0 0.35rem 0;
        letter-spacing: 0.5px;
    }
    .section-card .section-desc {
        color: #64748b;
        font-size: 0.82rem;
        margin: 0 0 1rem 0;
        line-height: 1.45;
    }
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 243, 255, 0.08);
        border: 1px solid rgba(0, 243, 255, 0.25);
        border-radius: 6px;
        padding: 8px 14px;
        font-size: 0.88rem;
        color: #e2e8f0;
        margin-top: 0.5rem;
    }
    .stat-badge span {
        color: #00f3ff;
        font-weight: 700;
        font-family: 'Orbitron', sans-serif;
    }

    /* Chat panel */
    .chat-panel-header {
        background: rgba(17, 22, 37, 0.55);
        border: 1px solid rgba(0, 243, 255, 0.12);
        border-radius: 10px 10px 0 0;
        padding: 1.1rem 1.35rem;
        border-bottom: none;
        backdrop-filter: blur(10px);
        position: relative;
    }
    .chat-panel-header .section-label {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #9d00ff;
        margin-bottom: 0.15rem;
    }
    .chat-panel-header .section-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #00f3ff;
        margin: 0 0 0.25rem 0;
    }
    .chat-panel-header .section-desc {
        color: #64748b;
        font-size: 0.82rem;
        margin: 0;
    }
    .chat-container {
        border-radius: 0 0 10px 10px !important;
        margin-bottom: 0 !important;
    }
    .empty-chat {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 280px;
        text-align: center;
        color: #64748b;
        gap: 8px;
    }
    .empty-chat-icon {
        font-size: 2.5rem;
        opacity: 0.6;
        margin-bottom: 4px;
    }
    .empty-chat-title {
        font-family: 'Orbitron', sans-serif;
        color: #94a3b8;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
    }
    .empty-chat-hint {
        font-size: 0.82rem;
        color: #475569;
        max-width: 320px;
        line-height: 1.5;
    }

    /* Topic picker — compact multiselect */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
        background-color: rgba(9, 12, 21, 0.75) !important;
        border: 1px solid rgba(0, 243, 255, 0.25) !important;
        border-radius: 4px !important;
        min-height: 38px !important;
    }
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: rgba(157, 0, 255, 0.2) !important;
        border: 1px solid rgba(157, 0, 255, 0.45) !important;
        color: #e2e8f0 !important;
        font-size: 0.75rem !important;
    }
    /* Topic grid hint */
    .topic-hint {
        font-size: 0.78rem;
        color: #64748b;
        margin-bottom: 0.75rem;
    }

    /* Hide default streamlit headers in our custom layout */
    div[data-testid="stVerticalBlock"] > div:has(> div > .section-card) + div[data-testid="stHeader"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-banner">
        <h1>🤖 CF Assistant</h1>
        <p class="hero-tagline">
            Your competitive programming companion — sync your <strong>Codeforces</strong> profile,
            solve problems with guided hints, and get personalized recommendations.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- HELPER FUNCTIONS ---

def render_section_header(label, title, description):
    st.markdown(
        f"""
        <div class="section-card section-spacer">
            <div class="section-label">{label}</div>
            <div class="section-title">{title}</div>
            <p class="section-desc">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def show_notice(kind, message):
    icons = {
        "success": "OK",
        "error": "!!",
        "warning": "!",
        "info": "i",
    }
    st.markdown(
        f"""
        <div class="cyber-notice cyber-notice-{kind}">
            <span class="cyber-notice-icon">{icons.get(kind, "i")}</span>
            <div class="cyber-notice-body">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if not api_key:
    show_notice("error", "GEMINI_API_KEY not found. Please add it to your <code>.env</code> file.")
    st.stop()

client = genai.Client(api_key=api_key)

def get_solved_problems(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None, "User not found or CF API is down."
        data = response.json()
        if data["status"] != "OK":
            return None, "Error fetching user data."
        
        solved = set()
        for submission in data["result"]:
            if submission.get("verdict") == "OK":
                prob = submission.get("problem", {})
                contest_id = prob.get("contestId")
                index = prob.get("index")
                if contest_id and index:
                    solved.add(f"{contest_id}{index}")
        return solved, None
    except Exception as e:
        return None, f"API Connection error: {e}"

def fetch_filtered_problems(tags, min_rating, max_rating, solved_problems):
    if not tags:
        return []

    seen_ids = set()
    valid_problems = []

    for tag in tags:
        url = f"https://codeforces.com/api/problemset.problems?tags={tag}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue
            data = response.json()
            if data["status"] != "OK":
                continue

            for prob in data["result"]["problems"]:
                rating = prob.get("rating")
                contest_id = prob.get("contestId")
                index = prob.get("index")
                name = prob.get("name")

                if rating and contest_id and index:
                    prob_id = f"{contest_id}{index}"
                    if (
                        min_rating <= rating <= max_rating
                        and prob_id not in solved_problems
                        and prob_id not in seen_ids
                    ):
                        seen_ids.add(prob_id)
                        valid_problems.append({
                            "contestId": contest_id,
                            "index": index,
                            "name": name,
                            "rating": rating,
                        })
        except Exception:
            continue

    return valid_problems

def get_cf_problem(problem_id):
    problem_id = problem_id.strip().upper().replace("/", "")
    contest_id = "".join([c for c in problem_id if c.isdigit()])
    problem_letter = "".join([c for c in problem_id if c.isalpha()])
    
    if not contest_id or not problem_letter:
        return None, "Invalid format. Use '1920A'."
    
    # Try multiple URL patterns (Problemset and Contest)
    urls_to_try = [
        f"https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}",
        f"https://codeforces.com/contest/{contest_id}/problem/{problem_letter}"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            problem_statement = soup.find("div", {"class": "problem-statement"})
            
            if problem_statement:
                # Clean up the text by preserving structure but removing excessive whitespace
                return problem_statement.get_text(separator="\n"), url
        except Exception:
            continue
            
    return None, "Problem not found or statement could not be parsed. (Check if the ID is correct)"

# --- SYSTEM INSTRUCTION ---
SYSTEM_INSTRUCTION = (
    "You are an expert Competitive Programming (CP) coach. "
    "CRITICAL RULES:\n"
    "1. Respond exclusively in ENGLISH.\n"
    "2. STRICTLY FORBIDDEN from providing full source code.\n"
    "3. DO NOT use LaTeX or dollar signs ($) for complexities. Write them as plain text like O(N log N) or O(10 * log N).\n"
    "4. Provide logical observation hints or step-by-step editorial structures.\n"
)

# --- SPLIT SCREEN INTERFACE LAYOUT ---
col1, col2 = st.columns([1, 1.3])

# ================= LEFT SECTION (USER PROFILE & PROBLEM CONFIG) =================
with col1:
    render_section_header(
        "Step 1",
        "Codeforces Handle",
        "Connect your profile to track solved problems and filter recommendations.",
    )
    cf_handle = st.text_input(
        "Handle",
        placeholder="e.g. tourist",
        label_visibility="collapsed",
        help="Your Codeforces username",
    )
    
    if cf_handle:
        if "cf_handle" not in st.session_state or st.session_state["cf_handle"] != cf_handle:
            with st.spinner("Syncing your solved problems..."):
                solved_set, err = get_solved_problems(cf_handle)
                if err:
                    show_notice("error", err)
                else:
                    st.session_state["solved_problems"] = solved_set
                    st.session_state["cf_handle"] = cf_handle
        
        if "solved_problems" in st.session_state:
            count = len(st.session_state["solved_problems"])
            st.markdown(
                f'<div class="stat-badge">✅ Profile synced — <span>{count}</span> problems solved</div>',
                unsafe_allow_html=True,
            )

    render_section_header(
        "Step 2",
        "Problem Solver",
        "Enter a problem ID to load it and request hints or editorial guidance.",
    )
    prob_input = st.text_input(
        "Problem ID",
        placeholder="e.g. 1920A",
        label_visibility="collapsed",
        help="Contest ID + problem letter, e.g. 1920A",
    )
    
    if prob_input:
        cleaned_id = prob_input.strip().upper().replace("/", "")
        
        # Only fetch and reset if it's a NEW problem ID
        if "current_prob_id" not in st.session_state or st.session_state["current_prob_id"] != cleaned_id:
            if "solved_problems" in st.session_state and cleaned_id in st.session_state["solved_problems"]:
                show_notice("warning", "You have already solved this problem on Codeforces.")
                
            with st.spinner("Loading problem..."):
                prob_text, url_or_err = get_cf_problem(prob_input)
                
            if prob_text:
                st.session_state["current_problem"] = prob_text
                st.session_state["current_prob_id"] = cleaned_id
                st.session_state["current_prob_url"] = url_or_err
                st.session_state["hint_count"] = 0
                st.session_state["prob_error"] = None
            else:
                st.session_state["current_problem"] = None
                st.session_state["prob_error"] = url_or_err

        # Display results based on session state
        if st.session_state.get("current_problem"):
            show_notice(
                "success",
                f'Problem loaded — <a href="{st.session_state["current_prob_url"]}" target="_blank" class="cyber-link">Open on Codeforces ↗</a>',
            )
            
            st.markdown('<p class="solver-action-label">How should the coach help?</p>', unsafe_allow_html=True)
            choice_col1, choice_col2 = st.columns(2)
            with choice_col1:
                st.markdown('<div class="cyber-action-hint"></div>', unsafe_allow_html=True)
                if st.button("💡 Get a Hint", key="btn_get_hint", use_container_width=True):
                    current_count = st.session_state.get("hint_count", 0)
                    if current_count >= 5:
                        st.session_state.messages.append({"role": "user", "content": "Requested another hint."})
                        st.session_state.messages.append({"role": "assistant", "content": "⚠️ I've already provided 5 hints for this problem. You have all the information needed to solve it! Try to implement the logic now."})
                        st.rerun()
                    else:
                        st.session_state["hint_count"] = current_count + 1
                        st.session_state["ai_action"] = "hint"
            with choice_col2:
                st.markdown('<div class="cyber-action-editorial"></div>', unsafe_allow_html=True)
                if st.button("📖 Editorial Walkthrough", key="btn_editorial", use_container_width=True):
                    st.session_state["ai_action"] = "editorial"
        elif st.session_state.get("prob_error"):
            show_notice("error", st.session_state["prob_error"])

    render_section_header(
        "Step 3",
        "Problem Recommendations",
        "Select one or more topics and a rating range to get tailored picks.",
    )
    
    TOPIC_DICTIONARY = {
        "Greedy": "Greedy strategy", "DP": "Dynamic Programming", "Binary Search": "Binary Search",
        "Graphs": "Graph Theory", "Data Structures": "Advanced Structures", "Math": "Mathematics",
        "Strings": "String Algorithms", "Two Pointers": "Two Pointers technique", "Bitmasks": "Bitmask states",
        "Constructive": "Constructive algorithms", "Sortings": "Sorting logic", "Brute Force": "Brute force search",
        "Implementation": "Implementation problems", "Combinatorics": "Combinatorics", "Number Theory": "Number Theory",
        "Geometry": "Computational Geometry", "DFS and Similar": "DFS algorithms", "Trees": "Tree structures",
        "Divide and Conquer": "Divide and Conquer", "Probabilities": "Probability & Expectation", "Games": "Game theory",
        "Shortest Paths": "Shortest Path routing", "Ternary Search": "Ternary Search", "Dsu": "Disjoint Set Union",
        "Flows": "Network Flows", "Matching": "Graph Matchings", "String Suffix-structures": "Suffix structures",
        "Expression Parsing": "Expression Parsing", "Graph Matchings": "Graph Matchings", "Interactive": "Interactive tasks",
        "Matrices": "Matrix exponentiation", "Meet-in-the-middle": "Meet in the middle", "Hashing": "String hashing",
        "2-sat": "2-SAT problems", "Schedules": "Scheduling tasks", "Chinese Remainder Theorem": "CRT theorems"
    }

    if "selected_tags" not in st.session_state:
        if "selected_tag" in st.session_state:
            st.session_state["selected_tags"] = [st.session_state["selected_tag"]]
        else:
            st.session_state["selected_tags"] = ["Greedy"]
        
    topics_list = list(TOPIC_DICTIONARY.keys())

    st.markdown('<p class="topic-hint">Topics — select one or more:</p>', unsafe_allow_html=True)
    st.multiselect(
        "Topics",
        options=topics_list,
        key="selected_tags",
        placeholder="e.g. Greedy, DP, Graphs...",
        label_visibility="collapsed",
    )

    selected_tags = st.session_state["selected_tags"]

    if selected_tags:
        tag_summary = ", ".join(selected_tags[:4])
        if len(selected_tags) > 4:
            tag_summary += f" +{len(selected_tags) - 4} more"
        show_notice("info", f"<strong>{len(selected_tags)}</strong> tag(s) active: {tag_summary}")
    else:
        show_notice("warning", "No tags selected — pick at least one to get recommendations.")
    
    rec_rating_range = st.slider(
        "Rating range",
        min_value=800,
        max_value=3500,
        value=(1500, 2300),
        step=100,
        help="Only problems within this rating band will be recommended",
    )
    
    if st.button("🚀 Find 3 Recommended Problems", use_container_width=True):
        if not cf_handle:
            show_notice("error", "Please enter a Codeforces handle first.")
        elif not selected_tags:
            show_notice("warning", "Please select at least one topic tag.")
        else:
            st.session_state["ai_action"] = "recommend"
            st.session_state["rec_topics"] = [t.lower() for t in selected_tags]
            st.session_state["rec_min_rating"] = rec_rating_range[0]
            st.session_state["rec_max_rating"] = rec_rating_range[1]

# ================= RIGHT SECTION (AI CHAT WITH AUTO SCROLL) =================
with col2:
    st.markdown(
        """
        <div class="chat-panel-header">
            <div class="section-label">Live Session</div>
            <div class="section-title">AI Coach Chat</div>
            <p class="section-desc">Ask follow-up questions, request hints, or discuss your approach.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Render all chat messages inside a single container using flexbox bubbles
    chat_html = '<div class="chat-container">'
    if not st.session_state.messages:
        chat_html += (
            '<div class="empty-chat">'
            '<div class="empty-chat-icon">💬</div>'
            '<div class="empty-chat-title">No messages yet</div>'
            '<p class="empty-chat-hint">Load a problem and request a hint, get recommendations, or type a question below to start.</p>'
            '</div>'
        )
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        # Convert markdown to HTML
        content_html = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        
        if role == "user":
            chat_html += (
                f'<div class="chat-row user-row">'
                f'<div class="chat-bubble user-bubble">'
                f'<div class="chat-message-content">{content_html}</div>'
                f'<span class="chat-avatar">👤</span>'
                f'</div>'
                f'</div>'
            )
        else:
            chat_html += (
                f'<div class="chat-row assistant-row">'
                f'<div class="chat-bubble assistant-bubble">'
                f'<span class="chat-avatar">🤖</span>'
                f'<div class="chat-message-content">{content_html}</div>'
                f'</div>'
                f'</div>'
            )
    chat_html += '</div>'
    
    # Auto-scroll to the bottom of the container
    chat_html += (
        '<script>'
        'setTimeout(function() {'
        '    var chatContainers = window.parent.document.querySelectorAll(".chat-container");'
        '    chatContainers.forEach(function(container) {'
        '        container.scrollTop = container.scrollHeight;'
        '    });'
        '}, 100);'
        '</script>'
    )
    st.markdown(chat_html, unsafe_allow_html=True)
            
    if "ai_action" in st.session_state:
        action = st.session_state["ai_action"]
        prompt = None
        display_text = ""
        
        if action in ["hint", "editorial"] and "current_problem" in st.session_state:
            problem_content = st.session_state["current_problem"]
            hint_num = st.session_state.get("hint_count", 1)
            prompt = (
                f"Provide Hint {hint_num} for this problem. No full code:\n\n{problem_content}" 
                if action == "hint" else 
                f"Explain the editorial approach step by step. No full code:\n\n{problem_content}"
            )
            display_text = f"Requested problem hint #{hint_num}." if action == "hint" else "Requested problem editorial."
        
        elif action == "recommend":
            solved_list = st.session_state.get("solved_problems", set())
            rec_topics = st.session_state.get("rec_topics", [])
            matched_pool = fetch_filtered_problems(
                rec_topics,
                st.session_state["rec_min_rating"],
                st.session_state["rec_max_rating"],
                solved_list
            )
            
            chosen_problems = random.sample(matched_pool, min(len(matched_pool), 3))
            topics_label = ", ".join(rec_topics)

            if not chosen_problems:
                st.session_state.messages.append(
                    {"role": "user", "content": f"Recommending problems for tags: {topics_label}."}
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"⚠️ No unsolved problems found for tags: {topics_label}.",
                    }
                )
                del st.session_state["ai_action"]
                st.rerun()
            else:
                problem_data_str = ""
                for idx, p in enumerate(chosen_problems, 1):
                    problem_data_str += f"Problem {idx}: ID={p['contestId']}{p['index']}, Name={p['name']}, Rating={p['rating']}, ContestID={p['contestId']}, Index={p['index']}\n"
                
                prompt = (
                    f"Build exactly 3 custom HTML blocks for these Codeforces problems. Follow Kryphos dark UI guidelines.\n\n"
                    f"{problem_data_str}\n"
                    f"STRICT HTML TEMPLATE REQUIREMENT (Do not wrap in markdown code blocks):\n"
                    f'<div style="background-color: #0f172a; border: 1px solid #1e293b; border-left: 4px solid #00ffc4; border-radius: 8px; padding: 18px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">'
                    f'    <h3 style="color: #00ffc4; margin-top: 0; font-family: sans-serif; font-size: 1.15rem;">🎯 RECOMMENDATION {{NUMBER}}</h3>'
                    f'    <p style="margin: 10px 0;">'
                    f'        <a href="https://codeforces.com/problemset/problem/{{CONTEST_ID}}/{{INDEX}}" target="_blank" style="text-decoration: none; color: #ffffff; font-weight: bold; border: 1px solid #00f2fe; padding: 6px 14px; border-radius: 6px; background-color: #14233c; display: inline-block; font-size: 0.95rem;">'
                    f'            ⭐ {{CONTEST_ID}}{{INDEX}} - {{PROBLEM_NAME}} [Rating: {{RATING}}] ⭐'
                    f'        </a>'
                    f'    </p>'
                    f'    <p style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.5;">'
                    f'        <strong style="color: #00f2fe;">Why it fits:</strong> {{EXPLANATION}}'
                    f'    </p>'
                    f'</div>'
                )
                display_text = f"Recommending problems for tags: {topics_label}."
            
        if prompt:
            with st.spinner("Processing..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.1-flash-lite',
                        contents=prompt,
                        config={"system_instruction": SYSTEM_INSTRUCTION}
                    )
                    response_text = response.text
                except Exception as e:
                    response_text = f"Error: {e}"
                    
            st.session_state.messages.append({"role": "user", "content": display_text})
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            del st.session_state["ai_action"]
            st.rerun()

    if user_msg := st.chat_input("Message your AI coach..."):
        st.session_state.messages.append({"role": "user", "content": user_msg})
        
        context = ""
        if "current_problem" in st.session_state:
            context = f"Active Problem Context:\n{st.session_state['current_problem']}\n\n"
            
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=context + user_msg,
                    config={"system_instruction": SYSTEM_INSTRUCTION}
                )
                response_text = response.text
            except Exception as e:
                response_text = f"Error: {e}"
                
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()