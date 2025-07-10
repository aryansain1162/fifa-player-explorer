import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import time

# Page Config
st.set_page_config(page_title="FIFA Player Explorer", page_icon="⚽", layout="wide")

# Custom CSS for style and smooth effects
st.markdown("""
    <style>
        .main { animation: fadeIn ease 1s; animation-fill-mode: forwards; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .block-container { padding-top: 1rem; }
        .stRadio > div { flex-direction: row; justify-content: center; }
        .stRadio label {
            background-color: #111;
            color: white;
            padding: 8px 20px;
            margin: 5px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
        }
        .stRadio input { display: none; }
        .stRadio label:hover {
            background-color: #333;
            transform: scale(1.02);
            box-shadow: 0 0 10px #00ffe1;
            transition: 0.3s ease;
        }
    </style>
""", unsafe_allow_html=True)

# Cache Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("male_players_legacy.csv")
    df['growth'] = df['potential'] - df['overall']
    return df

df = load_data()

# Navigation Bar
page = st.radio(
    "Navigation",
    ["🏠 Home", "🔎 Explore Player", "⚔️ Compare Players", "🏆 Leaderboard", "🏟️ Explore by Club", "🤖 AI Recommends"],
    horizontal=True,
    label_visibility="collapsed"
)

# Banner Image
img = Image.open("ronaldo_vs_messi.jpg")
resized_img = img.resize((1600, 350))
st.image(resized_img)

# Title & Welcome
st.title("👋 Welcome to FIFA Player Explorer")
st.markdown("Explore FIFA 23 male player data with smart suggestions, player insights and more.")

# Home Page
if page == "🏠 Home":
    st.markdown("## 🌟 Trending Picks")
    top_trending = df[df['overall'] > 88].sample(3)
    for _, row in top_trending.iterrows():
        st.markdown(f"**{row['short_name']}** | {row['club_name']} | 🌟 {row['overall']}")

    st.markdown("---")
    st.markdown("## 📅 Recent Players")
    st.dataframe(df[['short_name', 'club_name', 'overall', 'age']].head(10))

# Explore Player
elif page == "🔎 Explore Player":
    search_query = st.text_input("Search Player")
    filtered_players = df[df['short_name'].str.contains(search_query, case=False, na=False)]
    if not filtered_players.empty:
        player_selected = st.selectbox("Select a Player", filtered_players['short_name'].unique())
        player_data = df[df['short_name'] == player_selected].iloc[0]

        st.image(player_data['player_face_url'], width=200)

        overall = player_data['overall']
        badge = "🏆 Elite" if overall >= 88 else "⚡ Pro" if overall >= 80 else "🎯 Rookie"
        badge_color = "#FFD700" if overall >= 88 else "#1E90FF" if overall >= 80 else "#7CFC00"

        st.markdown(f"""
            <h2 style='color:white'>{player_data['short_name']}</h2>
            <h3 style='color:{badge_color}'>{badge}</h3>
            <p style='color:white'>Overall: {overall}</p>
            <p style='color:white'>Age: {player_data['age']} | Nationality: {player_data['nationality_name']}</p>
            <p style='color:white'>Club: {player_data['club_name']}</p>
        """, unsafe_allow_html=True)

        st.subheader("📊 Skill Overview")
        radar_cols = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
        stats = player_data[radar_cols].values
        angles = np.linspace(0, 2 * np.pi, len(radar_cols), endpoint=False).tolist()
        stats = np.concatenate((stats, [stats[0]]))
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
        ax.plot(angles, stats, color='cyan', linewidth=2)
        ax.fill(angles, stats, color='cyan', alpha=0.4)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(radar_cols)
        ax.set_yticklabels([])
        st.pyplot(fig)
    else:
        st.warning("No players found. Try a different name.")

# Compare Players
elif page == "⚔️ Compare Players":
    st.subheader("⚔️ Compare Two FIFA Players")
    player1 = st.selectbox("Select First Player", df['short_name'].dropna().unique(), key="p1")
    player2 = st.selectbox("Select Second Player", df['short_name'].dropna().unique(), key="p2")

    if player1 != player2:
        p1 = df[df['short_name'] == player1].iloc[0]
        p2 = df[df['short_name'] == player2].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.image(p1['player_face_url'], width=150)
            st.markdown(f"### {p1['short_name']}")
            st.write(f"Overall: {p1['overall']}, Age: {p1['age']}, Club: {p1['club_name']}")
        with col2:
            st.image(p2['player_face_url'], width=150)
            st.markdown(f"### {p2['short_name']}")
            st.write(f"Overall: {p2['overall']}, Age: {p2['age']}, Club: {p2['club_name']}")
    else:
        st.warning("Choose two different players.")

# Leaderboard
elif page == "🏆 Leaderboard":
    st.subheader("🏆 Top 10 Players")
    top_players = df.sort_values(by='overall', ascending=False).head(10)
    for _, row in top_players.iterrows():
        st.markdown(f"""
            <div style='background-color:#222; padding:10px; border-radius:10px;'>
                <img src="{row['player_face_url']}" width=50>
                <b style='color:white'>{row['short_name']}</b> - {row['club_name']} | Overall: {row['overall']}
            </div>
        """, unsafe_allow_html=True)

# Club-wise View
elif page == "🏟️ Explore by Club":
    st.subheader("🏟️ Explore by Club")
    clubs = sorted(df['club_name'].dropna().unique())
    selected_club = st.selectbox("Select Club", clubs)
    club_df = df[df['club_name'] == selected_club]

    for _, row in club_df.iterrows():
        st.markdown(f"""
            <div style='background-color:#333; padding:10px; border-radius:10px;'>
                <img src="{row['player_face_url']}" width=40>
                <b style='color:white'>{row['short_name']}</b> | Overall: {row['overall']} | Age: {row['age']}
            </div>
        """, unsafe_allow_html=True)

# AI Recommends
elif page == "🤖 AI Recommends":
    st.subheader("🤖 AI Recommends: Smart Player Picks")
    choice = st.selectbox("Choose Suggestion Type", [
        "Hidden Gems (Low Overall, High Potential)",
        "Top Young Players (≤ 21)",
        "Best Attackers",
        "Best Midfielders",
        "Best Defenders"
    ])

    if choice == "Hidden Gems (Low Overall, High Potential)":
        result = df[df['overall'] < 75].sort_values(by='growth', ascending=False).head(10)
    elif choice == "Top Young Players (≤ 21)":
        result = df[df['age'] <= 21].sort_values(by='potential', ascending=False).head(10)
    elif choice == "Best Attackers":
        result = df.sort_values(by=['shooting', 'pace'], ascending=False).head(10)
    elif choice == "Best Midfielders":
        result = df.sort_values(by=['passing', 'vision'], ascending=False).head(10)
    elif choice == "Best Defenders":
        result = df.sort_values(by=['defending', 'physic'], ascending=False).head(10)

    for _, row in result.iterrows():
        st.markdown(f"""
            <div style='background-color:#222; padding:10px; border-radius:10px;'>
                <img src="{row['player_face_url']}" width=50>
                <b style='color:white'>{row['short_name']}</b> - {row['club_name']} | Overall: {row['overall']}, Age: {row['age']}
            </div>
        """, unsafe_allow_html=True)
