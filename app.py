import streamlit as st
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS UX
# ==========================================
st.set_page_config(page_title="Lumière | Curated Cinema", layout="wide", initial_sidebar_state="expanded")

# Inject Custom Pastel Minimalist CSS styling
st.markdown("""
    <style>
        /* Base Backgrounds & Typography */
        .stApp { background-color: #F7F9F6; }
        .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp span, .stApp label, .stApp div {
            color: #4A554A !important;
            font-family: 'Helvetica Neue', sans-serif;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] { background-color: #E2ECE9 !important; border-right: 1px solid rgba(0,0,0,0.05); }
        
        /* Elegant Buttons */
        div.stButton > button {
            background-color: #F7F9F6 !important;
            border: 1.5px solid #C2828E !important;
            color: #C2828E !important;
            border-radius: 16px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: #C2828E !important;
            color: #F7F9F6 !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0,0,0,0.05) !important;
        }

        /* Movie Image Cards */
        [data-testid="stImage"] img {
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: transform 0.3s;
        }
        [data-testid="stImage"] img:hover { transform: scale(1.02); }

        /* Metric Badge override */
        [data-testid="stMetricValue"] { color: #C2828E !important; font-size: 1.2rem !important; }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. DATA LOADING & ML PIPELINE
# ==========================================
@st.cache_resource
def load_and_prepare_data():
    """Loads CSV, cleans headers, and prepares Content-Based TF-IDF matrix."""
    df = pd.read_csv('movies.csv')
    
    # Strictly strip whitespace as requested
    df.columns = df.columns.str.strip()
    
    # Safely target only the text features for NA string replacement
    # (Fixes pandas TypeError on float/integer columns)
    text_features = ['genres', 'overview', 'mood', 'cast']
    df[text_features] = df[text_features].fillna('')
    
    # Create unified metadata string for mathematical weighting
    df['combined_features'] = (df['genres'] + " " + df['overview'] + " " + df['mood'] + " " + df['cast']).str.lower()
    
    # Initialize TF-IDF Vectorizer
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined_features'])
    
    # Compute Cosine Similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    return df, cosine_sim

df, cosine_sim = load_and_prepare_data()


# ==========================================
# 3. CORE LOGIC & STATE MANAGEMENT
# ==========================================
# Initialize Session States
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
    
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = df['title'].iloc[0]

if 'mood_filter' not in st.session_state:
    st.session_state.mood_filter = "Any"

def add_to_watchlist(movie_title):
    """Adds a given movie to the user's local session watchlist."""
    if movie_title not in st.session_state.watchlist:
        st.session_state.watchlist.append(movie_title)
        st.toast(f"Added {movie_title} to your watchlist! 🍿")

def handle_surprise_me():
    """Selects a random movie, optionally factoring in the active mood filter."""
    if st.session_state.mood_filter == "Any":
        pool = df['title'].tolist()
    else:
        pool = df[df['mood'] == st.session_state.mood_filter]['title'].tolist()
        
    if pool:
        st.session_state.selected_movie = random.choice(pool)
    else:
        st.toast("No movies match this mood for a surprise!")

def get_recommendations(title, mood_filter="Any", num_recs=6):
    """Calculates and retrieves top recommendations based on similarity and mood."""
    if title not in df['title'].values:
        return pd.DataFrame()
    
    idx = df[df['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    movie_indices = [i[0] for i in sim_scores if i[0] != idx]
    recs_df = df.iloc[movie_indices]
    
    if mood_filter != "Any":
        recs_df = recs_df[recs_df['mood'] == mood_filter]
        
    return recs_df.head(num_recs)


# ==========================================
# 4. UI CONSTRUCTION
# ==========================================

# --- SIDEBAR: Watchlist & Export ---
with st.sidebar:
    st.markdown("## 🎞️ Your Watchlist")
    st.markdown("Curate your favorite finds.")
    
    if st.session_state.watchlist:
        for idx, item in enumerate(st.session_state.watchlist):
            st.markdown(f"- **{item}**")
            
        # Export Functional Tool
        export_text = "\n".join(st.session_state.watchlist)
        st.download_button(
            label="Download Watchlist 📥",
            data=export_text,
            file_name="my_lumiere_watchlist.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Your watchlist is currently empty.")

# --- MAIN APP ---
st.markdown("<h1 style='text-align: center; color: #4A554A;'>Lumière</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1rem;'>A curated, content-filtering recommendation engine.</p>", unsafe_allow_html=True)
st.write("---")

# Controls Layout (Autocomplete Search, Mood Filter, Surprise Button)
col_search, col_mood, col_surprise = st.columns([2, 1, 1])

movie_list = df['title'].tolist()
mood_list = ["Any", "happy", "sad", "love", "vibe", "friends together"]

with col_search:
    selected_movie = st.selectbox(
        "Search Base Movie:", 
        options=movie_list, 
        index=movie_list.index(st.session_state.selected_movie) if st.session_state.selected_movie in movie_list else 0,
        key="search_dropdown"
    )
    # Sync state manually without relying on rerun loops if altered from UI
    if selected_movie != st.session_state.selected_movie:
        st.session_state.selected_movie = selected_movie

with col_mood:
    st.selectbox(
        "Filter by Mood:", 
        options=mood_list,
        key="mood_filter"
    )

with col_surprise:
    st.markdown("<br>", unsafe_allow_html=True) # padding alignment
    st.button("Surprise Me ✨", on_click=handle_surprise_me, use_container_width=True)

# Generate Recommendations
st.markdown("### Hand-picked for you")
recs = get_recommendations(st.session_state.selected_movie, st.session_state.mood_filter)

# Dynamic Result Grid (Render in Multi-Column Rows)
if recs.empty:
    st.markdown(
        f"""
        <div style="background-color: #E2ECE9; padding: 20px; border-radius: 12px; text-align: center;">
            <p style="margin: 0; color: #4A554A;">We couldn't find a perfect match for the mood <b>'{st.session_state.mood_filter}'</b> based on this movie. Try expanding your search or altering the vibe!</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
else:
    # Build dynamic rows of 3 columns each
    cols_per_row = 3
    for i in range(0, len(recs), cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j, col in enumerate(row_cols):
            if i + j < len(recs):
                row_data = recs.iloc[i + j]
                with col:
                    # Poster Image
                    st.image(row_data['poster_url'], use_container_width=True)
                    
                    # Title & Star Rating
                    st.markdown(f"#### {row_data['title']}")
                    
                    # Pill/Badge CSS simulation for genres & mood
                    genre_tags = "".join([f"<span style='background-color:#C2828E; color:#F7F9F6; padding:4px 8px; border-radius:12px; font-size:0.75rem; margin-right:4px;'>{g.strip()}</span>" for g in row_data['genres'].split(',')])
                    st.markdown(genre_tags, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Metadata
                    st.caption(f"**Cast:** {row_data['cast']}")
                    st.caption(f"⭐ **{row_data['vote_average']} / 10**")
                    
                    # Action Button
                    st.button("Save to Watchlist", key=f"save_{row_data['id']}", on_click=add_to_watchlist, args=(row_data['title'],), use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)