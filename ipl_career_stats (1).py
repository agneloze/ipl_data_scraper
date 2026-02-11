"""
IPL Player Stats Scraper - Career Stats Only
Gets only career totals (not year-by-year breakdown)
"""

import json
import re
import pandas as pd
import requests
import time

# ===================== CONFIGURATION =====================
# Add all player URLs here - any order is fine!

PLAYER_URLS = [
    "https://www.iplt20.com/players/ms-dhoni/1",
    "https://www.iplt20.com/players/dewald-brevis/20593",
    "https://www.iplt20.com/players/devon-conway/20572",
    "https://www.iplt20.com/players/rahul-tripathi/3838",
    # Add more player URLs below - just paste them, no need to organize by team
    
]

# =========================================================


def extract_player_id_from_url(url):
    """Extract player slug and ID from URL"""
    # Remove https:// if present
    url = url.replace('https://', '').replace('http://', '').replace('www.', '')
    match = re.search(r'players/([^/]+)/(\d+)', url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def fetch_player_stats(player_slug, player_id):
    """Fetch player stats from the API"""
    # The actual data is on AWS S3, not on iplt20.com!
    api_url = f"https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/player/{player_id}-playerstats.js"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.iplt20.com/',
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Remove the JavaScript wrapper
            json_str = response.text.strip()
            json_str = re.sub(r'^onPlayerStats\((.*)\);?$', r'\1', json_str, flags=re.DOTALL)
            data = json.loads(json_str)
            return data
        else:
            print(f"   ✗ HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None


def get_career_stats(url):
    """Get only career stats for a player"""
    player_slug, player_id = extract_player_id_from_url(url)
    
    if not player_slug or not player_id:
        print(f"   ⚠️ Invalid URL: {url}")
        return None
    
    print(f"   Fetching {player_slug}...")
    stats = fetch_player_stats(player_slug, player_id)
    
    if not stats:
        return None
    
    # Initialize row with basic info
    row = {
        'First_Name': '',
        'Last_Name': '',
        'Full_Name': '',
    }
    
    # Get batting career stats (Year = "AllTime")
    if 'Batting' in stats and stats['Batting']:
        career_bat = next((b for b in stats['Batting'] if b.get('Year') == 'AllTime'), None)
        if career_bat:
            full_name = career_bat.get('PlayerName', '')
            name_parts = full_name.split()
            row['First_Name'] = name_parts[0] if name_parts else ''
            row['Last_Name'] = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            row['Full_Name'] = full_name
            
            # Batting stats
            row['Matches'] = career_bat.get('Matches', '')
            row['Innings'] = career_bat.get('Innings', '')
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
    """Main function"""
    print("🏏 IPL Career Stats Scraper")
    print("=" * 50)
    print(f"\n📝 Processing {len(PLAYER_URLS)} players...\n")
    
    all_data = []
    
    for url in PLAYER_URLS:
        player_data = get_career_stats(url)
        if player_data:
            all_data.append(player_data)
        time.sleep(0.3)  # Small delay between requests
    
    # Create Excel file
    if all_data:
        df = pd.DataFrame(all_data)
        
        output_file = 'IPL_Career_Stats.xlsx'
        df.to_excel(output_file, index=False, sheet_name='Career Stats')
        
        print(f"\n✅ Success! Data saved to {output_file}")
        print(f"📊 Total players: {len(df)}")
    else:
        print("\n❌ No data collected!")


if __name__ == "__main__":
    main()
