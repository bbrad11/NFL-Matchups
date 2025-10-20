import streamlit as st
from datetime import datetime

# -------------- Page config --------------
st.set_page_config(
    page_title="Sports Matchup Analyzer",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------- Styles (light + pop) --------------
st.markdown("""
<style>
/* Hide Streamlit's default sidebar nav */
section[data-testid="stSidebarNav"] { display: none; }

/* Sidebar spacing */
[data-testid="stSidebar"] { padding-top: 2rem !important; }

/* App background & readable text */
.stApp { background-color: #F8FAFC; color: #0F172A; }

/* Ensure block container padding */
.block-container { padding-top: 1.5rem; padding-left: 2.5rem; padding-right: 2.5rem; }

/* Title gradient */
.main h1 {
    font-size: 3.75rem !important;
    font-weight: 900 !important;
    text-align: center;
    background: linear-gradient(90deg, #1E3A8A 0%, #C9082A 50%, #FDB927 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}

/* Subtitle */
.subtitle { text-align: center; color: #475569; font-size: 1.25rem; margin-bottom: 2.5rem; }

/* Card */
.sport-card {
    background: #ffffff; border-radius: 18px; padding: 2rem;
    box-shadow: 0 10px 25px rgba(2,6,23,0.06);
    transition: transform 0.25s, box-shadow 0.25s, border 0.25s; cursor: pointer;
    border: 2px solid #E6E9EE; color: #0F172A !important;
}
.sport-card * { color: #0F172A !important; }
.sport-card:hover { transform: translateY(-8px) scale(1.01); box-shadow: 0 22px 46px rgba(2,6,23,0.14); border-color: #2563EB; }

.sport-icon { font-size: 4.75rem; text-align: center; margin-bottom: 0.5rem; }
.sport-title { font-size: 1.9rem; font-weight: 800; text-align: center; margin-bottom: 0.6rem; color: #0F172A; }
.sport-description { color: #475569; text-align: center; font-size: 1.02rem; }

.feature-list { margin-top: 1.25rem; padding-left: 0; list-style: none; }
.feature-item { padding: 0.45rem 0; color: #0F172A; font-size: 1.02rem; }
.feature-item:before { content: "✓ "; color: #10B981; font-weight: 700; margin-right: 0.5rem; }

/* Sidebar style */
section[data-testid="stSidebar"] { background-color: #0B1220; color: white; padding-top: 1.25rem; }
section[data-testid="stSidebar"] * { color: #E6EEF8 !important; }
div[data-baseweb="select"] > div { background-color: #0F172A !important; border-radius: 10px; border: 1px solid #273246 !important; color: #E6EEF8 !important; }
div[data-baseweb="select"] svg, div[data-baseweb="select"] span { color: #E6EEF8 !important; }

/* Sidebar header & footer */
.sidebar-header { text-align:center; font-size:1.5rem; font-weight:700; background: linear-gradient(90deg, #1E3A8A, #C9082A, #FDB927); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }
.sidebar-footer { text-align:center; color:#9CA3AF; font-size:0.85rem; margin-top:2.25rem; }
</style>
""", unsafe_allow_html=True)

# -------------- Sidebar (single nav) --------------
st.sidebar.markdown("<div class='sidebar-header'>🏆 Sports Analyzer</div>", unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Select Sport",
    ["Home", "NFL Data (Inline)", "Open NFL Page (pages/1_🏈_NFL.py)"],
    index=0,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class='sidebar-footer'>
    📊 Data updated daily<br>
    Built with Streamlit
</div>
""", unsafe_allow_html=True)


# ----------------- Helper: try import nflreadpy -----------------
def try_import_nflreadpy():
    try:
        import nflreadpy as nfl
        return nfl
    except Exception as e:
        return None


# ----------------- HOME PAGE -----------------
if page == "Home":
    st.markdown("<h1>🏆 Sports Matchup Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Data-driven insights for smarter lineup decisions</p>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown("""
        <div class="sport-card" role="button" tabindex="0">
            <div class="sport-icon">🏈</div>
            <div class="sport-title">NFL Matchup Analyzer</div>
            <div class="sport-description">Find the best NFL matchups and identify defensive weaknesses.</div>
            <ul class="feature-list">
                <li class="feature-item">Defense positional weaknesses</li>
                <li class="feature-item">Week-by-week matchup analysis</li>
                <li class="feature-item">Player consistency ratings</li>
                <li class="feature-item">NextGen Stats integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="sport-card" role="button" tabindex="0">
            <div class="sport-icon">🏀</div>
            <div class="sport-title">NBA Matchup Analyzer</div>
            <div class="sport-description">Analyze NBA matchups and find scoring opportunities.</div>
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
    <div style='text-align:center;padding:1.5rem;'>
        <h2>🚀 Getting Started</h2>
        <p style='font-size:1.05rem;color:#475569;'>Pick "NFL Data (Inline)" to load live nflverse data (requires nflreadpy). Or click "Open NFL Page" if you prefer the dedicated page file under /pages.</p>
    </div>
    """, unsafe_allow_html=True)


# ----------------- INLINE NFL DATA PAGE -----------------
elif page == "NFL Data (Inline)":
    st.markdown("<h1>🏈 NFL Data Explorer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Load play-by-play, team, and player data (uses nflreadpy)</p>", unsafe_allow_html=True)

    nfl = try_import_nflreadpy()
    if nfl is None:
        st.error("nflreadpy is not installed. Install it with `pip install nflreadpy` and restart the app.")
    else:
        # basic config controls
        col1, col2, col3 = st.columns(3)
        with col1:
            current_year = nfl.get_current_season() if hasattr(nfl, "get_current_season") else datetime.now().year
            season = st.number_input("Season", min_value=1990, max_value=datetime.now().year, value=current_year, step=1)
        with col2:
            week_default = nfl.get_current_week() if hasattr(nfl, "get_current_week") else 1
            week = st.number_input("Week (1-22)", min_value=1, max_value=22, value=week_default, step=1)
        with col3:
            sample_rows = st.number_input("Preview rows", min_value=5, max_value=200, value=20, step=5)

        st.markdown("### Load Play-by-Play (may take longer)")
        if st.button("Load play-by-play"):
            with st.spinner("Downloading play-by-play..."):
                try:
                    pbp = nfl.load_pbp(seasons=season)
                    st.success(f"Loaded play-by-play for {season} (rows: {len(pbp)})")
                    st.dataframe(pbp.head(sample_rows).to_pandas() if hasattr(pbp, "to_pandas") else pbp.head(sample_rows))
                except Exception as e:
                    st.error(f"Error loading play-by-play: {e}")

        st.markdown("### Team stats")
        if st.button("Load team stats"):
            with st.spinner("Downloading team stats..."):
                try:
                    teams = nfl.load_team_stats(seasons=season)
                    st.success(f"Loaded team stats for {season} (rows: {len(teams)})")
                    st.dataframe(teams.head(sample_rows).to_pandas() if hasattr(teams, "to_pandas") else teams.head(sample_rows))
                except Exception as e:
                    st.error(f"Error loading team stats: {e}")

        st.markdown("### Player stats")
        if st.button("Load player stats"):
            with st.spinner("Downloading player stats..."):
                try:
                    players = nfl.load_player_stats(seasons=season)
                    st.success(f"Loaded player stats for {season} (rows: {len(players)})")
                    st.dataframe(players.head(sample_rows).to_pandas() if hasattr(players, "to_pandas") else players.head(sample_rows))
                except Exception as e:
                    st.error(f"Error loading player stats: {e}")

        st.markdown("### Utilities")
        cols = st.columns(3)
        if cols[0].button("Clear nflreadpy cache"):
            try:
                if hasattr(nfl, "clear_cache"):
                    nfl.clear_cache()
                    st.success("nflreadpy cache cleared.")
                else:
                    st.info("clear_cache not available in this version.")
            except Exception as e:
                st.error(f"Error clearing cache: {e}")

        if cols[1].button("Show available loaders"):
            items = [x for x in dir(nfl) if callable(getattr(nfl, x)) and x.startswith("load_")]
            st.write(items)

        if cols[2].button("Show config"):
            try:
                from nflreadpy.config import get_config
                st.json(get_config().__dict__)
            except Exception:
                st.info("No programmatic get_config available or config object hidden in this version.")


# ----------------- Open page in /pages (if you prefer) -----------------
elif page == "Open NFL Page (pages/1_🏈_NFL.py)":
    # attempt to switch_page to the pages folder entry (Streamlit >=1.15 supports st.switch_page)
    try:
        st.info("Opening the NFL page (pages/1_🏈_NFL.py). If that fails, make sure the pages file exists.")
        st.experimental_set_query_params(page="1_🏈_NFL")  # minor hint for navigation
        st.write("If your Streamlit version supports it, use the UI sidebar to navigate to the NFL page in the Pages section.")
    except Exception:
        st.warning("Could not programmatically open the pages/ file. Please use Streamlit's Pages menu (sidebar) or navigate manually.")

