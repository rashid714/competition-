import streamlit as st
import datetime
import os
from pathlib import Path
import logging
from agent import FoodRescueAgent
from utils.visualization import (
    create_metrics_dashboard,
    create_weight_distribution_chart,
    create_donation_timeline,
    create_impact_card
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="FoodRescue — Community Food Rescue",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark-only theme: load the dark CSS for a consistent, professional look
base = os.path.dirname(__file__)
theme_file = "dark_style.css"
css_path = os.path.join(base, "static", theme_file)
try:
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning(f"Theme file {theme_file} not found. Using default styles.")

# Ensure the app knows we're using the dark theme
st.session_state['theme'] = 'Dark'

# Initialize agent
@st.cache_resource
def get_agent():
    """Get cached agent instance"""
    return FoodRescueAgent()

agent = get_agent()

# Config (Gemini) from agent memory
config = agent.memory.config

# Session state initialization
if 'current_session' not in st.session_state:
    st.session_state.current_session = f"daily_{datetime.date.today().strftime('%Y%m%d')}"

# Header
st.markdown("""
<div class="app-header">
    <h1 class="app-title">FoodRescue — Community Food Rescue</h1>
    <p class="app-subtitle">Track surplus food, measure community impact, and coordinate safe pickups</p>
</div>
""", unsafe_allow_html=True)

# System status check
st.sidebar.markdown("## 🔍 System Status")

# AI / Gemini settings
st.sidebar.markdown("## 🤖 AI Settings")
use_gemini = st.sidebar.checkbox("Enable Gemini AI (use for impact reports & suggestions)", value=config.gemini_ready)
st.session_state['use_gemini'] = use_gemini

if use_gemini and not config.gemini_ready:
    st.sidebar.warning("Gemini requested but not configured correctly. Use the diagnostic below.")

if st.sidebar.button("Test Gemini Connection"):
    # Attempt a lightweight test call and report success/failure, do not expose key
    if not config.gemini_key:
        st.sidebar.error("No GEMINI_API_KEY found. Add it to .env or environment and restart.")
    else:
        with st.sidebar.spinner("Testing Gemini..."):
            try:
                # Make a very small test generation to validate connectivity/permissions
                if not config.model:
                    st.sidebar.info("Initializing Gemini model instance...")
                    config._setup_gemini()

                test_prompt = "Ping"
                resp = config.model.generate_content(test_prompt)
                text = getattr(resp, 'text', None) or getattr(resp, 'result', None)
                if text:
                    st.sidebar.success("Gemini test succeeded — model responded.")
                else:
                    st.sidebar.error("Gemini responded but returned empty text. Check key/permissions.")
            except Exception as e:
                st.sidebar.error(f"Gemini test failed: {str(e)}")

# AI Assistant (sidebar chat)
with st.sidebar.expander("🤖 AI Assistant", expanded=False):
    if 'assistant_history' not in st.session_state:
        st.session_state['assistant_history'] = []

    # Ensure assistant input exists and handle a one-time clear flag
    if 'assistant_input' not in st.session_state:
        st.session_state['assistant_input'] = ''
    # If a previous action requested clearing the input, perform it before widgets are instantiated
    if st.session_state.get('assistant_clear'):
        st.session_state['assistant_input'] = ''
        st.session_state['assistant_clear'] = False

    # Quick templates
    templates = {
        "Summarize today's donations": "Summarize today's donations into a 1-2 sentence impact statement.",
        "Write friendly social post": "Write a short friendly social media post announcing today's rescued food and thanks to donors.",
        "Explain pickup steps": "Provide concise pickup instructions for volunteers collecting donations.",
        "Suggest volunteers/tasks": "Suggest volunteer roles and quick tasks for organizing donations this afternoon."
    }
    template_choice = st.selectbox("Templates", ["(choose a template)"] + list(templates.keys()))
    if st.button("Apply template", key='apply_template') and template_choice and template_choice != "(choose a template)":
        st.session_state['assistant_input'] = templates[template_choice]

    # Display conversation history
    for msg in st.session_state['assistant_history']:
        role = msg.get('role', 'assistant')
        content = msg.get('content', '')
        if role == 'user':
            st.markdown(f"<div style='padding:6px;border-radius:8px;background:#eef2ff;margin-bottom:6px;'><strong>You:</strong> {content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding:6px;border-radius:8px;background:#f3f4f6;margin-bottom:6px;'><strong>Assistant:</strong> {content}</div>", unsafe_allow_html=True)

    # Input box
    user_query = st.text_area("Ask the assistant", key='assistant_input', height=80)
    if st.button("Send", key='assistant_send'):
        query = (st.session_state.get('assistant_input') or '').strip()
        if not query:
            st.warning("Please type a question before sending.")
        else:
            # Append user message
            st.session_state['assistant_history'].append({'role': 'user', 'content': query})

            # Determine response strategy
            if st.session_state.get('demo_mode'):
                resp_text = "Demo mode active — AI is disabled. Try toggling demo mode off to use Gemini."
            elif not st.session_state.get('use_gemini'):
                resp_text = "Gemini is disabled in AI Settings. Enable it to get assistant responses."
            else:
                # Try to initialize model and generate a response
                try:
                    ok = config.ensure_model()
                    if not ok:
                        resp_text = f"Could not initialize Gemini: {config.last_error or 'unknown error'}"
                    else:
                        prompt = f"You are a helpful assistant for the Google Food Rescue app. Answer concisely and help the user with donation tracking, summaries, and guidance.\nUser: {query}\nAssistant:"
                        resp = config.model.generate_content(prompt)
                        text = getattr(resp, 'text', None) or getattr(resp, 'result', None)
                        resp_text = text.strip() if text else "Gemini returned an empty response."
                except Exception as e:
                    resp_text = f"Assistant error: {str(e)}"

            # Append assistant response and request clearing the input on next run
            st.session_state['assistant_history'].append({'role': 'assistant', 'content': resp_text})
            # Do not assign to `assistant_input` after the widget is created; set a clear flag
            st.session_state['assistant_clear'] = True

    # Transcript download
    if st.session_state.get('assistant_history'):
        transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state['assistant_history']])
        st.download_button("Download Transcript", transcript, file_name=f"assistant_transcript_{datetime.date.today().isoformat()}.txt")

# Demo mode toggle
st.sidebar.markdown("## 🧪 Demo & Safety")
demo_mode = st.sidebar.checkbox("Enable demo/sample data mode (no writes to disk)", value=False)
st.session_state['demo_mode'] = demo_mode

# Onboarding banner (show once, compatible with older Streamlit)
if 'seen_onboarding' not in st.session_state:
    st.session_state['seen_onboarding'] = False

if not st.session_state['seen_onboarding']:
    with st.container():
        st.markdown("""
        ## Welcome 👋
        This app helps track surplus food donations, measure impact, and generate friendly impact reports.

        - Use **Log New Surplus** to record donations.
        - Use the **AI Settings** to enable Gemini — set your `GEMINI_API_KEY` in a local `.env` file.
        - Enable **Demo Mode** to try the app without writing data.

        Click **Got it** to continue.
        """)
        if st.button("Got it", key='onboarding_got_it'):
            st.session_state['seen_onboarding'] = True
        st.markdown("---")

# Gemini key guidance (do not paste secrets in the UI/chat)
if not config.gemini_ready:
    # Provide clearer diagnostics: whether the key exists and any initialization error
    key_present = bool(config.gemini_key)
    if not key_present:
        st.sidebar.markdown(
            '''
Gemini not configured. To enable AI features, set `GEMINI_API_KEY` in your environment or in a `.env` file next to the project.

Example (macOS / zsh):
```bash
export GEMINI_API_KEY=your_api_key_here
```
After setting the key, restart the Streamlit server.
'''
        )
    else:
        # Key appears present but initialization failed — show guidance and safe diagnostics
        st.sidebar.markdown(f"**Gemini key present but initialization failed.**")
        if getattr(config, 'last_error', None):
            st.sidebar.markdown(f"- Error: {config.last_error}")
        st.sidebar.markdown("- Check network access, key validity, and that the key has proper IAM/permissions.\n- Restart the app after fixing the key.")

# Check Gemini status
gemini_status = "✅ Ready" if config.gemini_ready else "❌ Not Configured"
gemini_class = "status-green" if config.gemini_ready else "status-red"

st.sidebar.markdown(f"""
<div class="status-badge {gemini_class}">
    Gemini API: {gemini_status}
</div>
""", unsafe_allow_html=True)

# Check data directory status
data_dir_status = "✅ Ready" if os.path.exists("session_data") and os.access("session_data", os.W_OK) else "❌ Not Accessible"
data_dir_class = "status-green" if os.path.exists("session_data") and os.access("session_data", os.W_OK) else "status-red"

st.sidebar.markdown(f"""
<div class="status-badge {data_dir_class}">
    Data Storage: {data_dir_status}
</div>
""", unsafe_allow_html=True)

# Session selection with validation
st.sidebar.markdown("## 📅 Session Management")
session_input = st.sidebar.text_input(
    "Session ID",
    value=st.session_state.current_session,
    help="Format: daily_YYYYMMDD"
)

# Validate session format
if session_input and session_input != st.session_state.current_session:
    if session_input.startswith('daily_') and len(session_input) >= 13:
        st.session_state.current_session = session_input
        logger.info(f"Session changed to: {session_input}")
    else:
        st.sidebar.warning("⚠️ Invalid session format. Use: daily_YYYYMMDD")

# Get dashboard data
dashboard = agent.get_dashboard(st.session_state.current_session)

# Main content
st.markdown(f'<div class="session-badge">🎯 Dashboard - {st.session_state.current_session}</div>', unsafe_allow_html=True)

# Two-column layout
col1, col2 = st.columns([2, 3])

with col1:
    st.markdown("### 📝 Log New Surplus")
    
    with st.form("donation_form"):
        store = st.text_input("🏪 Store Name*", placeholder="e.g., FreshMart Downtown")
        item = st.text_input("🥬 Food Item*", placeholder="e.g., Organic Carrots")
        weight = st.number_input("⚖️ Weight (lbs)*", min_value=0.1, value=50.0, step=1.0)
        location = st.text_input("📍 Location*", placeholder="e.g., San Francisco")
        
        submitted = st.form_submit_button("✅ Log Surplus", type="primary")
    
    if submitted:
        if not all([store.strip(), item.strip(), location.strip()]):
            st.error("❌ Please fill all required fields marked with *")
        elif weight <= 0:
            st.error("❌ Weight must be greater than zero")
        else:
            with st.spinner("🧠 Processing with Google AI..."):
                result = agent.log_donation(
                    store.strip(),
                    item.strip(),
                    weight,
                    location.strip(),
                    st.session_state.current_session
                )
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                st.balloons()
                
                # Update dashboard after successful log
                dashboard = agent.get_dashboard(st.session_state.current_session)
                
                # Show impact report
                st.markdown("### 🌍 Community Impact")
                create_impact_card(result['report'])
            else:
                st.error(f"❌ {result['message']}")

with col2:
    # Impact report
    if dashboard.get('donations'):
        st.markdown("### 🌍 Today's Impact")
        # Show latest or regenerated report
        current_report = st.session_state.get('regenerated_report') or dashboard.get('report')
        create_impact_card(current_report)

        if st.button("Regenerate Impact Report"):
            try:
                new_report = agent.memory.generate_impact_report(st.session_state.current_session)
                st.session_state['regenerated_report'] = new_report
                st.success("Impact report regenerated.")
                create_impact_card(new_report)
            except Exception as e:
                st.error(f"Failed to regenerate report: {str(e)}")
    
    # Metrics dashboard
    st.markdown("### 📊 Key Metrics")
    create_metrics_dashboard(dashboard['metrics'])
    
    # Charts
    st.markdown("### 📈 Weight Distribution")
    create_weight_distribution_chart(dashboard['metrics'])
    
    st.markdown("### ⏰ Donation Timeline")
    create_donation_timeline(dashboard.get('donations', []))

# Recent donations section
if dashboard.get('donations'):
    st.markdown("### 📋 Recent Donations")
    
    # Sort donations by timestamp (newest first)
    sorted_donations = sorted(
        dashboard['donations'],
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    for donation in sorted_donations[:10]:  # Show last 10 donations
        time_str = donation['timestamp'].split('T')[1][:5] if 'T' in donation.get('timestamp', '') else '00:00'
        st.markdown(f"""
        <div class="donation-card">
            <strong>{time_str}</strong> - <strong>{donation.get('store', 'Unknown Store')}</strong><br>
            {donation.get('item', 'Unknown Item')} ({donation.get('weight', 0):.1f} lbs)<br>
            <small>📍 {donation.get('location', 'Unknown Location')}</small>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("📭 No donations logged yet for this session. Start by logging your first surplus!")

# Footer
st.markdown("""
<div class="footer">
    <p>🍎 FoodRescue — Community Food Rescue • Kaggle Capstone 2025</p>
    <p>Optional Gemini AI • Reproducible & auditable • Community-focused</p>
    <p style="font-size: 0.85em; margin-top: 8px; color: #666;">
        System Status: All components operational • Last updated: {time}
    </p>
</div>
""".format(time=datetime.datetime.now().strftime('%H:%M:%S')), unsafe_allow_html=True)
