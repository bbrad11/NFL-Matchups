import streamlit as st

# Page config
st.set_page_config(
    page_title="Sports Matchup Analyzer",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM STYLES ----------
st.markdown("""
<style>
/* Hide Streamlit's default sidebar nav */
section[data-testid="stSidebarNav"] { display: none; }

/* Adjust spacing */
[data-testid="stSidebar"] { padding-top: 2rem !important; }

/* ---------- GLOBAL STYLES ---------- */
.stApp {
    background-color: #F8FAFC;
    color: #111827;
}

.main h1 {
    font-size: 4rem !important;
    font-weight: 900 !important;
    text-align: center;
    background: linear-gradient(90deg, #1E3A8A 0%, #C9082A 50%, #FDB927 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #475569;
    font-size: 1.5rem;
    margin-bottom: 3rem;
}

/* ---------- CARD STYLES ---------- */
.sport-card {
    background: white;
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease;
    cursor: pointer;
    border: 2px solid #E5E7EB;
}

.sport-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.15);
    border-color: #2563EB;
}

.sport-icon {
    font-size: 5rem;
    text-align: center;
    margin-bottom: 1rem;
}

.sport-title {
    font-size: 2rem;
    font-weight: 800;
    text-align: center;
    color: #111827;
    margin-bottom: 1rem;
}

.sport-description {
    color: #4B5563;
    text-align: center;
    font-size: 1.1rem;
}

.feature-list {
    margin-top: 1.5rem;
    padding-left: 0;
    list-style: none;
}

.feature-item {
    padding: 0.5rem 0;
    color: #1F2937;
    font-size: 1.05rem;
}

.feature-item:before {
    content: "✓ ";
    color: #10B981;
    font-weight: bold;
    margin-right: 0.5rem;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background-color: #0F172A; /* Dark navy */
    color: white;
}

section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] p {
    color: white !important;
}

/* Sidebar selectbox styling */
div[data-baseweb="select"] > div {
    background-color: #1E293B !important;
    border-radius: 10px;
    border: 1px solid #334155 !important;
    color: white !important;
}

div[data-baseweb="select"] svg {
    color: white !important;
}

/* Sidebar header gradient */
.sidebar-header {
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #1E3A8A, #C9082A, #FDB927);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}

/* Sidebar footer */
.sidebar-footer {
    text-align: center;
    color: #9CA3AF;
    font-size: 0.8rem;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.markdown("<div class='sidebar-header'>🏆 Sports Analyzer</div>", unsafe_allow_html=True)

sport = st.sidebar.selectbox(
    "Select Sport",
    ["Home", "🏈 NFL", "🏀 NBA"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# ---------- PAGE ROUTER ----------
if sport == "Home":
    st.markdown("<h1>🏆 Sports Matchup Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Data-driven insights for smarter lineup decisions</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # NFL Card
        st.markdown("""
        <div class="sport-card">
            <div class="sport-icon">🏈</div>
            <div class="sport-title">NFL Matchup Analyzer</div>
            <div class="sport-description">
                Find the best NFL matchups and identify defensive weaknesses.
            </div>
            <ul class="feature-list">
                <li class="feature-item">Defense positional weaknesses</li>
                <li class="feature-item">Week-by-week matchup analysis</li>
                <li class="feature-item">Player consistency ratings</li>
                <li class="feature-item">NextGen Stats integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # NBA Card
        st.markdown("""
        <div class="sport-card">
            <div class="sport-icon">🏀</div>
            <div class="sport-title">NBA Matchup Analyzer</div>
            <div class="sport-description">
                Analyze NBA matchups and find scoring opportunities.
            </div>
            <ul class="feature-list">
                <li class="feature-item">Team defensive rankings</li>
                <li class="feature-item">Tonight's game analysis</li>
                <li class="feature-item">Player performance trends</li>
                <li class="feature-item">Pace and efficiency stats</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h2>🚀 Getting Started</h2>
        <p style='font-size: 1.2rem; color: #4B5563;'>
            Select a sport from the dropdown above to begin your analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

elif sport == "🏈 NFL":
    st.switch_page("pages/1_🏈_NFL.py")

elif sport == "🏀 NBA":
    st.switch_page("pages/2_🏀_NBA.py")

# ---------- FOOTER ----------
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class='sidebar-footer'>
    📊 Data updated daily<br>
    Built with Streamlit
</div>
""", unsafe_allow_html=True)
