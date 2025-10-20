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

/* ---------- GLOBAL / PAGE ---------- */
.stApp {
    background-color: #F8FAFC; /* light page background */
    color: #0F172A; /* default readable text color */
}

/* Block container (main content) */
.block-container {
    padding-top: 1.5rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    background-color: transparent;
}

/* Force readable colors in any markdown / text containers */
div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] span,
div[data-testid="stMarkdownContainer"] li {
    color: #0F172A !important;
}

/* Title gradient */
.main h1 {
    font-size: 3.75rem !important;
    font-weight: 900 !important;
    text-align: center;
    background: linear-gradient(90deg, #1E3A8A 0%, #C9082A 50%, #FDB927 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #475569;
    font-size: 1.25rem;
    margin-bottom: 2.5rem;
}

/* ---------- CARD STYLES (force dark text inside) ---------- */
.sport-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 25px rgba(2,6,23,0.06);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border 0.25s ease;
    cursor: pointer;
    border: 2px solid #E6E9EE;
    /* ensure children don't inherit weird colors */
    color: #0F172A !important;
}

/* make sure all elements inside the card are readable */
.sport-card * {
    color: #0F172A !important;
}

/* hover effect */
.sport-card:hover {
    transform: translateY(-8px) scale(1.01);
    box-shadow: 0 22px 46px rgba(2,6,23,0.14);
    border-color: #2563EB;
}

/* Icon/title/desc */
.sport-icon {
    font-size: 4.75rem;
    text-align: center;
    margin-bottom: 0.5rem;
}

.sport-title {
    font-size: 1.9rem;
    font-weight: 800;
    text-align: center;
    color: #0F172A !important;
    margin-bottom: 0.6rem;
}

.sport-description {
    color: #475569 !important;
    text-align: center;
    font-size: 1.02rem;
}

/* feature list */
.feature-list {
    margin-top: 1.25rem;
    padding-left: 0;
    list-style: none;
}

.feature-item {
    padding: 0.45rem 0;
    color: #0F172A !important;
    font-size: 1.02rem;
}

.feature-item:before {
    content: "✓ ";
    color: #10B981;
    font-weight: 700;
    margin-right: 0.5rem;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background-color: #0B1220; /* dark navy */
    color: white;
    padding-top: 1.25rem;
}

/* Force readable sidebar text */
section[data-testid="stSidebar"] * {
    color: #E6EEF8 !important;
}

/* Sidebar selectbox styling (visible dropdown) */
div[data-baseweb="select"] > div {
    background-color: #0F172A !important;
    border-radius: 10px;
    border: 1px solid #273246 !important;
    color: #E6EEF8 !important;
}

/* ensure the select text & arrow are visible */
div[data-baseweb="select"] svg, div[data-baseweb="select"] span {
    color: #E6EEF8 !important;
}

/* Sidebar header gradient */
.sidebar-header {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #1E3A8A, #C9082A, #FDB927);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.6rem;
}

/* sidebar footer */
.sidebar-footer {
    text-align: center;
    color: #9CA3AF;
    font-size: 0.85rem;
    margin-top: 2.25rem;
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

# ---------- PAGE CONTENT ----------
if sport == "Home":
    st.markdown("<h1>🏆 Sports Matchup Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Data-driven insights for smarter lineup decisions</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # NFL Card
        st.markdown("""
        <div class="sport-card" role="button" tabindex="0">
            <div class="sport-icon">🏈</div>
            <div class="sport-title">NFL Matchup Analyzer</div>
