import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import os

# 1. Page Config
st.set_page_config(page_title="FIFA Player Explorer", page_icon="⚽", layout="wide")

# 2. Custom CSS for Smooth Animations
st.markdown("""
    <style>
    .main {
        animation: fadeInAnimation ease 1s;
        animation-iteration-count: 1;
        animation-fill-mode: forwards;
    }

    @keyframes fadeInAnimation {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# 3. Load Data with Spinner (Optimized version)
with st.spinner('Loading FIFA player data... ⚡'):
    time.sleep(2)

    # Drop heavy/unneeded columns
    cols_to_exclude = ['player_url', 'real_face', 'body_type', 'team_jersey_number']
    df_full = pd.read_csv('male_players (legacy).csv', low_memory=True, usecols=lambda col: col not in cols_to_exclude)

    # Sample for performance
    df = df_full.sample(n=1000, random_state=42)


# 4. Title
st.title("⚽ FIFA Player Explorer")

# 5. Navigation Tabs
page = st.sidebar.selectbox("Navigate", ["🏠 Home", "🔎 Explore Player", "🏆 Leaderboard", "🏟️ Explore by Club"])

# 6. Home Page
if page == "🏠 Home":
    st.image("https://cdn.wallpapersafari.com/71/93/zTgNtx.jpg", use_column_width=True)
    st.markdown("## Welcome to FIFA Explorer App ⚡\nExplore Players, Clubs and More!")

# 7. Player Explorer Page
elif page == "🔎 Explore Player":
    search_query = st.sidebar.text_input("Search Player", key="search_box")
    filtered_players = df[df['short_name'].str.contains(search_query, case=False, na=False)]
    player_selected = st.sidebar.selectbox("Select a Player", filtered_players['short_name'].unique(), key='player_select')

    player_data = df[df['short_name'] == player_selected].iloc[0]

    # Player Image
    img_url = player_data['player_face_url']
    st.image(img_url, width=200)

    # Badge
    overall = player_data['overall']
    if overall >= 88:
        badge = "🏆 Elite"
        badge_color = "#FFD700"
    elif overall >= 80:
        badge = "⚡ Pro"
        badge_color = "#1E90FF"
    else:
        badge = "🎯 Rookie"
        badge_color = "#7CFC00"

    st.markdown(f"""
        <h2 style="color:white; text-shadow: 1px 1px 2px black;">{player_data['short_name']}</h2>
        <h3 style="color:{badge_color}; text-shadow: 1px 1px 2px black;">{badge}</h3>
        <p style="color:white; text-shadow: 1px 1px 2px black;">Overall: {overall}</p>
        <p style="color:white; text-shadow: 1px 1px 2px black;">Age: {player_data['age']} | Nationality: {player_data['nationality_name']}</p>
        <p style="color:white; text-shadow: 1px 1px 2px black;">Club: {player_data['club_name']}</p>
    """, unsafe_allow_html=True)

    # Radar Chart
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

# 8. Leaderboard Page
elif page == "🏆 Leaderboard":
    st.subheader("🏆 Top 10 Players by Overall Rating")

    top_players = df.sort_values(by='overall', ascending=False).head(10)

    for index, row in top_players.iterrows():
        st.markdown(f"""
            <div style="background-color:#222222; padding:10px; border-radius:10px; margin-bottom:10px;">
                <img src="{row['player_face_url']}" style="width:50px; height:auto; vertical-align:middle; margin-right:10px;">
                <b style="color:white;">{row['short_name']} ({row['overall']})</b> - {row['club_name']}
            </div>
        """, unsafe_allow_html=True)

# 9. Club Wise Players Page
elif page == "🏟️ Explore by Club":
    st.subheader("🏟️ Explore Players by Club")

    clubs = df['club_name'].dropna().unique()
    club_selected = st.selectbox("Select Club", sorted(clubs))

    club_players = df[df['club_name'] == club_selected]

    st.write(f"### {club_selected} Players ({len(club_players)})")

    for idx, row in club_players.iterrows():
        st.markdown(f"""
            <div style="background-color:#333333; padding:10px; border-radius:10px; margin-bottom:8px;">
                <img src="{row['player_face_url']}" style="width:40px; height:auto; vertical-align:middle; margin-right:8px;">
                <b style="color:white;">{row['short_name']}</b> | Overall: {row['overall']} | Age: {row['age']}
            </div>
        """, unsafe_allow_html=True)


