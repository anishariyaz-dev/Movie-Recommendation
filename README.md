# Movie-Recommendation  Flixora // The Perfect Movie Vibe Picker
Flixora is a professional, single-page web application engineered to help users discover cinematic experiences tailored to their exact mood or current "vibe."

Powered by a lightweight Flask backend and an immersive, glassmorphic Tailwind CSS user interface, the application integrates dynamically with The Movie Database (TMDB) API to deliver real-time data seamlessly.

KEY FEATURES
Cinematic Entrance: Features a custom CSS keyframe blur-to-focus splash screen animation that establishes a premium application tone from the start.

Intelligent Vibe Search: Utilizes an asynchronous, real-time input mechanism that renders live autocomplete suggestions instantly from TMDB’s catalog as the user types.

Persisted Watchlist: Implements a smooth, side-drawer interface backed by browser localStorage, allowing users to save movies without needing a database or account registration.

Responsive Glassmorphism: Built entirely with highly responsive utility classes, featuring custom micro-interactions and dark, frosted-glass visual cards optimized for both mobile and desktop screens.

TECHNICAL ARCHITECTURE
Backend Framework: Leverages Python and Flask to handle route orchestration and internal API wrappers cleanly.

Connection Optimization: Utilizes persistent HTTP connection pooling via requests.Session to significantly minimize network latency during high-frequency searching.

Client-Side Caching: Uses high-performance Vanilla JavaScript (ES6) backed by a native memory Map cache to eliminate redundant API requests for already-loaded titles.

Smart Recommendation Engine: Extracts the original language profile of a selected movie, blends official TMDB recommendations with trending global discovery data from that same language, filters duplicates, and returns twenty highly relevant results.

SETUP AND INSTALLATION
Clone the Repository: Run git clone https://github.com/anishariyaz-dev/Movie-Recommendation/tree/main in your terminal and navigate into the project root directory.

Initialize Environment: Create a clean Python virtual environment by executing python -m venv venv and activate it using the appropriate script for your operating system.

Install Dependencies: Install the required core packages by executing the command pip install flask requests python-dotenv (or via a requirements.txt file).

Configure Authentication: Obtain a free API key from themoviedb.org, create a text file named .env in the root folder, and add the line: TMDB_API_KEY=your_actual_api_key.

Launch the Application: Boot the local development server by executing python app.py in your console, then navigate to http://127.0.0.1:5000/ in your web browser.

LICENSE
Distributed under the permissive MIT License. The software remains entirely open for further open-source modifications, personal portfolios, and localized development expansions.