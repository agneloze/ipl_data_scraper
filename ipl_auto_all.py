import json
import re
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import sqlite3

# ===================== CONFIGURATION =====================

TEAMS = [
    'chennai-super-kings',
    'mumbai-indians',
    'royal-challengers-bengaluru',
    'kolkata-knight-riders',
    'delhi-capitals',
    'punjab-kings',
    'rajasthan-royals',
    'sunrisers-hyderabad',
    'lucknow-super-giants',
    'gujarat-titans',
]


# =========================================================


def get_team_player_ids(team_slug):
    """Extract all player IDs from a team's squad page"""
    url = f"https://www.iplt20.com/teams/{team_slug}"

    print(f"\n📋 Fetching {team_slug}...")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"   ✗ Failed to fetch team page")
            return []

        # Parse HTML to find player links
        soup = BeautifulSoup(response.text, 'html.parser')

        player_ids = []
        # Find all links that match /players/*/NUMBER pattern
        for link in soup.find_all('a', href=True):
            href = link['href']
            match = re.search(r'/players/[^/]+/(\d+)', href)
            if match:
                player_id = match.group(1)
                player_ids.append(player_id)

        # Remove duplicates
        player_ids = list(set(player_ids))
        print(f"   ✓ Found {len(player_ids)} players")

        return player_ids

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return []


def fetch_player_stats(player_id):
    """Fetch player stats from S3"""
    api_url = f"https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/player/{player_id}-playerstats.js"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.iplt20.com/',
        }

        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            json_str = response.text.strip()
            json_str = re.sub(r'^onPlayerStats\((.*)\);?$', r'\1', json_str, flags=re.DOTALL)
            data = json.loads(json_str)
            return data
        else:
            return None

    except:
        return None


def get_career_stats(player_id):
    """Get only career stats for a player"""
    stats = fetch_player_stats(player_id)

    if not stats:
        return None

    row = {
        'Player_ID': player_id,
        'First_Name': '',
        'Last_Name': '',
        'Full_Name': '',
    }

    # Get batting career stats
    if 'Batting' in stats and stats['Batting']:
        career_bat = next((b for b in stats['Batting'] if b.get('Year') == 'AllTime'), None)
        if career_bat:
            full_name = career_bat.get('PlayerName', '')
            name_parts = full_name.split()
            row['First_Name'] = name_parts[0] if name_parts else ''
            row['Last_Name'] = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            row['Full_Name'] = full_name

            row['Matches'] = (career_bat.get('Matches', ''))
            row['Innings'] = (career_bat.get('Innings', ''))
            row['Runs'] = career_bat.get('Runs', '')
            row['Balls_Faced'] = career_bat.get('Balls', '')
            row['Highest_Score'] = career_bat.get('HighestScore', '')
            row['Batting_Average'] = career_bat.get('BattingAvg', '')
            row['Strike_Rate'] = career_bat.get('StrikeRate', '')
            row['Fifties'] = career_bat.get('Fifties', '')
            row['Hundreds'] = career_bat.get('Hundreds', '')
            row['Fours'] = career_bat.get('Fours', '')
            row['Sixes'] = career_bat.get('Sixes', '')
            row['Not_Outs'] = career_bat.get('NotOuts', '')
            row['Catches'] = career_bat.get('Catches', '')
            row['Stumpings'] = career_bat.get('Stumpings', '')


    # Get bowling career stats
    if 'Bowling' in stats and stats['Bowling']:
        career_bowl = next((b for b in stats['Bowling'] if b.get('Year') == 'AllTime'), None)
        if career_bowl:
            row['Overs'] = career_bowl.get('Overs', '')
            row['Runs_Conceded'] = career_bowl.get('Runs', '')
            row['Wickets'] = career_bowl.get('Wickets', '')
            row['Bowling_Average'] = career_bowl.get('Average', '')
            row['Economy'] = career_bowl.get('Econ', '')
            row['Bowling_Strike_Rate'] = career_bowl.get('StrikeRate', '')
            row['Best_Bowling'] = career_bowl.get('BBM', '')
            row['4_Wickets'] = career_bowl.get('FourWkts', '')
            row['5_Wickets'] = career_bowl.get('FiveWkts', '')

    return row


def main():
    """Main function - fully automated!"""
    print("🏏 IPL Career Stats Scraper - FULLY AUTOMATED")
    print("=" * 50)
    print("\n🤖 This will automatically fetch ALL players from ALL teams!")
    print("⏱️  This might take a few minutes...\n")

    all_player_ids = []

    # Step 1: Get all player IDs from all teams
    for team in TEAMS:
        player_ids = get_team_player_ids(team)
        all_player_ids.extend(player_ids)
        time.sleep(1)  # Be nice to the server

    # Remove duplicates (players who played for multiple teams)
    all_player_ids = list(set(all_player_ids))

    print(f"\n📊 Total unique players found: {len(all_player_ids)}")
    print(f"\n⬇️  Downloading stats for all players...\n")

    # Step 2: Get stats for each player
    all_data = []
    for i, player_id in enumerate(all_player_ids, 1):
        if i % 10 == 0:  # Progress update every 10 players
            print(f"   Progress: {i}/{len(all_player_ids)} players...")

        player_data = get_career_stats(player_id)
        if player_data:
            all_data.append(player_data)
        time.sleep(0.1)

    # Step 3: Save to Excel
    if all_data:
        df = pd.DataFrame(all_data)

        output_file = 'IPL_All_Players_Stats'
        conn = sqlite3.connect(f'{output_file}.db')
        df.to_sql(name='employees', con=conn, if_exists='replace', index=False)
        df.to_csv(f'{output_file}.csv')
        df.to_excel(f'{output_file}.xlsx', index=False, sheet_name='Career Stats')

        print(f"\n✅ SUCCESS! Data saved to {output_file}")
        print(f"📊 Total players with data: {len(df)}")
        print(f"🏏 You now have stats for {df['Full_Name'].nunique()} IPL players!")
    else:
        print("\n❌ No data collected!")


if __name__ == "__main__":
    main()
