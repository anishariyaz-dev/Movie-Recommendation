import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 1. DATA HANDLING & MOCK DATASET
# ==========================================
@st.cache_data
def load_data():
    """
    Generates a high-quality sample dataset of 20 famous movies.
    This ensures the app runs out-of-the-box without needing external CSV files.
    """
    data = {
        'movie_id': list(range(1, 21)),
        'title': [
            'Inception', 'Interstellar', 'The Dark Knight', 'The Avengers', 'Titanic',
            'Avatar', 'The Matrix', 'Iron Man', 'The Notebook', 'Gladiator',
            'The Prestige', 'Shutter Island', 'Avengers: Endgame', 'Spider-Man: No Way Home', 'Romeo + Juliet',
            'Gravity', 'The Martian', 'Batman Begins', 'A Walk to Remember', 'Mad Max: Fury Road'
        ],
        'genres': [
            'Action Sci-Fi Thriller', 'Adventure Drama Sci-Fi', 'Action Crime Drama', 'Action Adventure Sci-Fi', 'Drama Romance',
            'Action Adventure Fantasy Sci-Fi', 'Action Sci-Fi', 'Action Sci-Fi Adventure', 'Drama Romance', 'Action Drama Adventure',
            'Drama Mystery Sci-Fi', 'Drama Thriller Mystery', 'Action Adventure Sci-Fi', 'Action Adventure Sci-Fi', 'Drama Romance',
            'Sci-Fi Thriller Drama', 'Adventure Sci-Fi Drama', 'Action Crime Drama', 'Drama Romance', 'Action Adventure Sci-Fi'
        ],
        'keywords': [
            'dream mind-bending subconscious', 'space time-travel wormhole', 'batman joker superhero', 'marvel superhero avengers', 'shipwreck love tragedy',
            'alien pandora 3d', 'virtual-reality hacker simulation', 'marvel superhero inventor', 'love memory alzheimers', 'love memory alzheimers',
            'magic illusion rivalry', 'asylum mind-bending twist', 'marvel superhero time-travel', 'marvel superhero multiverse', 'shakespeare love tragedy',
            'space survival orbit', 'mars survival astronaut', 'batman origin superhero', 'love tragedy high-school', 'desert post-apocalyptic survival'
        ],
        'overview': [
            'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
            'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
            'Earth\'s mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from enslaving humanity.',
            'A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.',
            'A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.',
            'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
            'After being held captive in an Afghan cave, billionaire engineer Tony Stark creates a unique weaponized suit of armor to fight evil.',
            'A poor yet passionate young man falls in love with a rich young woman, giving her a sense of freedom, but they are soon separated because of their social differences.',
            'A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.',
            'After a tragic accident, two stage magicians engage in a battle to create the ultimate illusion while sacrificing everything they have to outwit each other.',
            'In 1954, a U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane.',
            'After the devastating events of Infinity War, the Avengers assemble once more in order to reverse Thanos\' actions and restore balance to the universe.',
            'With Spider-Man\'s identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear.',
            'Shakespeare\'s famous play is updated to the hip modern suburb of Verona still retaining its original dialogue.',
            'Two astronauts work together to survive after an accident leaves them stranded in space.',
            'An astronaut becomes stranded on Mars after his team assume him dead, and must rely on his ingenuity to find a way to signal to Earth that he is alive.',
            'After training with his mentor, Batman begins his fight to free crime-ridden Gotham City from corruption.',
            'The story of two North Carolina teens, Landon Carter and Jamie Sullivan, who are thrown together after Landon gets into trouble and is made to do community service.',
            'In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.'
        ]
    }
    return pd.DataFrame(data)

# ==========================================
# 2. METHODOLOGY & ML LOGIC
# ==========================================
@st.cache_resource
def prepare_model(df):
    """
    Prepares the Content-Based Filtering model.
    Combines features, vectorizes text, and computes the cosine similarity matrix.
    """
    # Combine 'genres', 'keywords', and 'overview' into a single 'tags' column
    df['tags'] = df['genres'] + " " + df['keywords'] + " " + df['overview']
    
    # Initialize CountVectorizer to convert text to vectors, removing English stop words
    cv = CountVectorizer(max_features=5000, stop_words='english')
    
    # Fit and transform the 'tags' column into a numerical matrix
    vectors = cv.fit_transform(df['tags']).toarray()
    
    # Compute the Cosine Similarity matrix
    similarity_matrix = cosine_similarity(vectors)
    
    return similarity_matrix

def recommend(movie_title, df, similarity_matrix):
    """
    Finds the index of the input movie, fetches similarity scores, and returns top 5 matches.
    """
    # ---> THIS IS THE INDEXING LOGIC <---
    # Find the index of the selected movie in the dataframe
    movie_index = df[df['title'] == movie_title].index[0]
    
    # Fetch similarity scores for this specific movie index
    distances = similarity_matrix[movie_index]
    
    # Sort the movies based on similarity scores in descending order (excluding itself)
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    # Retrieve the actual movie data for the top 5 recommendations using their indexes
    recommended_movies = [df.iloc[i[0]] for i in movies_list]
    
    return recommended_movies

# ==========================================
# 3. USER INTERFACE (STREAMLIT)
# ==========================================
def main():
    # Set page configuration for a clean, modern layout
    st.set_page_config(page_title="FlickFinder", page_icon="🍿", layout="wide")
    
    # Load data and prepare model
    df = load_data()
    similarity_matrix = prepare_model(df)
    
    # Header Section
    st.title("🍿 FlickFinder: AI Movie Recommendations")
    st.markdown("Discover your next favorite film! Select a movie you love, and our Content-Based AI will recommend 5 similar movies based on genres, keywords, and plot overviews.")
    st.divider()
    
    # Input Section
    st.subheader("What should we base our recommendations on?")
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown:",
        df['title'].values
    )
    
    # Action Button
    if st.button("Get Recommendations", type="primary"):
        
        # 1. Display Anchor Movie Details
        anchor_movie = df[df['title'] == selected_movie].iloc[0]
        
        st.success("Recommendations generated successfully!")
        st.markdown("### 🎬 You Selected:")
        st.markdown(f"**{anchor_movie['title']}**")
        st.caption(f"**Genres:** {anchor_movie['genres']}")
        st.write(f"> *{anchor_movie['overview']}*")
        
        st.divider()
        
        # 2. Display Top 5 Recommendations in a Horizontal Layout
        st.markdown("### 🔥 Top 5 Recommended Movies:")
        
        recommendations = recommend(selected_movie, df, similarity_matrix)
        
        # Create 5 columns for the clean card layout
        cols = st.columns(5)
        
        for col, movie in zip(cols, recommendations):
            with col:
                # Extract the main genre (first word of the genres string)
                main_genre = movie['genres'].split()[0] if pd.notna(movie['genres']) else "Unknown"
                
                # Render the "Card" using HTML/CSS inside Streamlit
                st.markdown(f"""
                <div style="background-color: #1E1E1E; padding: 15px; border-radius: 10px; height: 120px; border: 1px solid #333;">
                    <h5 style="margin-bottom: 5px; color: white;">{movie['title']}</h5>
                    <span style="background-color: #FF4B4B; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">
                        {main_genre}
                    </span>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()