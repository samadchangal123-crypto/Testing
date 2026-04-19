import streamlit as st
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import database as db
from datetime import datetime
import random
import os
import sys

st.set_page_config(
    page_title="MISS ALIYA | INSTAGRAM DM",
    page_icon="📷",
    layout="wide"
)

# ============ PREMIUM CSS ============
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

* {
    font-family: 'Outfit', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #f5f0ff 0%, #e9eaff 40%, #fdf4ff 100%);
}

.main .block-container {
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(12px);
    border-radius: 32px;
    padding: 40px;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
}

.main-header {
    background: linear-gradient(135deg, #fff, #faf5ff);
    border-radius: 28px;
    padding: 30px;
    text-align: center;
}

.main-header h1 {
    background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-size: 3rem;
    font-weight: 900;
}

.center-image-container {
    display: flex;
    justify-content: center;
    margin: -50px auto 20px auto;
}

.center-image {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.stButton>button {
    background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);
    color: white;
    font-weight: 700;
    padding: 12px 28px;
    border-radius: 40px;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(131,58,180,0.3);
}

.console-output {
    background: #0f172a;
    border-radius: 20px;
    padding: 20px;
    max-height: 400px;
    overflow-y: auto;
    color: #00ff88;
    font-family: monospace;
}

.console-line {
    border-left: 3px solid #833ab4;
    padding: 8px 15px;
    margin-bottom: 8px;
    background: #1e293b;
    border-radius: 10px;
    font-family: monospace;
}

.footer {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #833ab4, #fd1d1d);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-weight: 800;
}

.success-box {
    background: linear-gradient(135deg, #10b981, #34d399);
    border-radius: 20px;
    padding: 15px;
    color: white;
    font-weight: 700;
    text-align: center;
}

.error-box {
    background: linear-gradient(135deg, #ef4444, #f87171);
    border-radius: 20px;
    padding: 15px;
    color: white;
    font-weight: 700;
    text-align: center;
}
</style>
"""

center_image_html = """
<div class="center-image-container">
    <img class="center-image" src="https://i.ibb.co/rG4yDJ7D/f5b610892f1e.jpg" alt="MISS ALIYA">
</div>
"""

st.markdown(custom_css + center_image_html, unsafe_allow_html=True)

# ============ SESSION STATE ============
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        st.session_state.logs.append(formatted_msg)
    print(formatted_msg)

def setup_instagram_browser(automation_state=None):
    log_message("Setting up Chrome for Instagram...", automation_state)
    
    chrome_options = Options()
    
    # Important for Render/Cloud
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Try to find chromium binary
    chromium_paths = ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome']
    for path in chromium_paths:
        if os.path.exists(path):
            chrome_options.binary_location = path
            log_message(f"Found browser at: {path}", automation_state)
            break
    
    try:
        from selenium.webdriver.chrome.service import Service
        
        # Try webdriver-manager first
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log_message("Browser ready with webdriver-manager!", automation_state)
            return driver
        except:
            pass
        
        # Fallback to default
        driver = webdriver.Chrome(options=chrome_options)
        log_message("Browser ready with default driver!", automation_state)
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
        
    except Exception as e:
        log_message(f"Browser error: {e}", automation_state)
        raise

def find_instagram_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(5)
    
    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][placeholder*="Message"]',
        'div[aria-label*="Message" i]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="Message"]',
        'div[role="textbox"]'
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    log_message(f'{process_id}: ✅ Found input', automation_state)
                    return element
        except:
            continue
    
    return None

def send_instagram_messages(config, automation_state, user_id, process_id='IG-1'):
    driver = None
    try:
        log_message(f'{process_id}: 🚀 Starting Instagram DM...', automation_state)
        driver = setup_instagram_browser(automation_state)
        
        # Open Instagram
        log_message(f'{process_id}: Opening Instagram...', automation_state)
        driver.get('https://www.instagram.com/')
        time.sleep(5)
        
        # Add cookies
        if config.get('cookies') and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            try:
                cookie_string = config['cookies']
                for cookie_pair in cookie_string.split(';'):
                    if '=' in cookie_pair:
                        name, value = cookie_pair.strip().split('=', 1)
                        try:
                            driver.add_cookie({'name': name, 'value': value, 'domain': '.instagram.com'})
                        except:
                            pass
                driver.refresh()
                time.sleep(5)
            except Exception as e:
                log_message(f'{process_id}: Cookie error: {e}', automation_state)
        
        # Open DM
        chat_target = config.get('chat_id', '').strip()
        if not chat_target:
            log_message(f'{process_id}: ❌ No target!', automation_state)
            automation_state.running = False
            return 0
        
        log_message(f'{process_id}: Opening DM with @{chat_target}...', automation_state)
        driver.get(f'https://www.instagram.com/direct/t/{chat_target}/')
        time.sleep(10)
        
        # Find input
        message_input = find_instagram_message_input(driver, process_id, automation_state)
        
        if not message_input:
            log_message(f'{process_id}: ❌ Input not found!', automation_state)
            automation_state.running = False
            return 0
        
        # Prepare messages
        delay = max(int(config.get('delay', 30)), 30)
        messages_list = [msg.strip() for msg in config.get('messages', 'Hello!').split('\n') if msg.strip()]
        if not messages_list:
            messages_list = ['Hello!']
        
        messages_sent = 0
        
        while automation_state.running:
            base_msg = messages_list[automation_state.message_rotation_index % len(messages_list)]
            automation_state.message_rotation_index += 1
            
            if config.get('name_prefix'):
                msg_to_send = f"{config['name_prefix']} {base_msg}"
            else:
                msg_to_send = base_msg
            
            try:
                # Type message
                driver.execute_script("""
                    arguments[0].click();
                    arguments[0].focus();
                    arguments[0].innerText = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                """, message_input, msg_to_send)
                
                time.sleep(2)
                
                # Send with Enter
                driver.execute_script("""
                    const enter = new KeyboardEvent('keydown', {
                        key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true
                    });
                    arguments[0].dispatchEvent(enter);
                """, message_input)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f'{process_id}: ✅ Sent #{messages_sent}: "{msg_to_send[:40]}..."', automation_state)
                
                # Wait
                actual_delay = random.randint(delay, delay + 15)
                log_message(f'{process_id}: Waiting {actual_delay}s...', automation_state)
                
                # Clear input
                driver.execute_script("arguments[0].innerText = '';", message_input)
                time.sleep(actual_delay)
                
            except Exception as e:
                log_message(f'{process_id}: Error: {str(e)[:100]}', automation_state)
                time.sleep(60)
        
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: Fatal: {str(e)}', automation_state)
        automation_state.running = False
        return 0
    finally:
        if driver:
            driver.quit()

def start_automation(user_config, user_id):
    if st.session_state.automation_state.running:
        return
    
    st.session_state.automation_state.running = True
    st.session_state.automation_state.message_count = 0
    st.session_state.automation_state.logs = []
    st.session_state.automation_state.message_rotation_index = 0
    
    db.set_automation_running(user_id, True)
    
    thread = threading.Thread(target=send_instagram_messages, args=(user_config, st.session_state.automation_state, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)

# ============ LOGIN PAGE ============
def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>📷 MISS ALIYA INSTAGRAM DM</h1>
        <p>INSTAGRAM DM AUTOMATION SYSTEM</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 SIGN-UP"])
    
    with tab1:
        username = st.text_input("USERNAME", key="login_username")
        password = st.text_input("PASSWORD", type="password", key="login_password")
        
        if st.button("🚀 LOGIN", use_container_width=True):
            if username and password:
                user_id = db.verify_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.success(f"✅ WELCOME {username}!")
                    st.rerun()
                else:
                    st.error("❌ INVALID!")
            else:
                st.warning("⚠️ FILL BOTH")
    
    with tab2:
        new_user = st.text_input("USERNAME", key="signup_username")
        new_pass = st.text_input("PASSWORD", type="password", key="signup_password")
        confirm = st.text_input("CONFIRM", type="password", key="confirm")
        
        if st.button("🎉 SIGN UP", use_container_width=True):
            if new_pass == confirm:
                success, msg = db.create_user(new_user, new_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.error("PASSWORDS DON'T MATCH!")

def main_app():
    st.markdown("""
    <div class="main-header">
        <h1>📷 MISS ALIYA INSTAGRAM DM</h1>
        <p>AUTOMATE YOUR INSTAGRAM DIRECT MESSAGES</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"### 👤 {st.session_state.username}")
    if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
        if st.session_state.automation_state.running:
            stop_automation(st.session_state.user_id)
        st.session_state.logged_in = False
        st.rerun()
    
    user_config = db.get_user_config(st.session_state.user_id)
    if not user_config:
        user_config = {'chat_id': '', 'name_prefix': '', 'delay': 35, 'cookies': '', 'messages': 'Hello!\nHow are you?'}
    
    tab1, tab2 = st.tabs(["⚙️ SETTINGS", "🔥 AUTOMATION"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            chat_id = st.text_input("INSTAGRAM USERNAME", value=user_config.get('chat_id', ''), placeholder="john_doe")
            name_prefix = st.text_input("NAME PREFIX", value=user_config.get('name_prefix', ''))
            delay = st.number_input("DELAY (SEC)", min_value=30, max_value=300, value=user_config.get('delay', 35))
        with col2:
            cookies = st.text_area("COOKIES", value=user_config.get('cookies', ''), height=150, placeholder="sessionid=xxx; csrftoken=xxx; ds_user_id=xxx")
            messages = st.text_area("MESSAGES", value=user_config.get('messages', ''), height=200, placeholder="Hello!\nHow are you?")
        
        if st.button("💾 SAVE", use_container_width=True):
            db.update_user_config(st.session_state.user_id, chat_id, name_prefix, delay, cookies, messages)
            st.success("✅ SAVED!")
            st.rerun()
    
    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📨 SENT", st.session_state.automation_state.message_count)
        with col2:
            status = "🟢 RUNNING" if st.session_state.automation_state.running else "🔴 STOPPED"
            st.metric("STATUS", status)
        with col3:
            cfg = db.get_user_config(st.session_state.user_id)
            st.metric("TARGET", cfg.get('chat_id', 'NOT SET')[:15] if cfg else 'NOT SET')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ START", disabled=st.session_state.automation_state.running, use_container_width=True):
                cfg = db.get_user_config(st.session_state.user_id)
                if cfg and cfg.get('chat_id') and cfg.get('cookies'):
                    start_automation(cfg, st.session_state.user_id)
                    st.success("✅ STARTED!")
                    st.rerun()
                else:
                    st.error("❌ SET USERNAME AND COOKIES FIRST!")
        with col2:
            if st.button("⏹️ STOP", disabled=not st.session_state.automation_state.running, use_container_width=True):
                stop_automation(st.session_state.user_id)
                st.warning("⚠️ STOPPED!")
                st.rerun()
        
        if st.session_state.automation_state.logs:
            st.markdown("### 📊 CONSOLE")
            logs_html = '<div class="console-output">'
            for log in st.session_state.automation_state.logs[-40:]:
                logs_html += f'<div class="console-line">{log}</div>'
            logs_html += '</div>'
            st.markdown(logs_html, unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_page()
else:
    main_app()

st.markdown('<div class="footer">⚠️ USE AT OWN RISK · MISS ALIYA</div>', unsafe_allow_html=True)
