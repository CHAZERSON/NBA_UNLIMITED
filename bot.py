import requests
import os

# Securely grab the Bot ID from the GitHub Vault
BOT_ID = os.environ.get("GROUPME_BOT_ID")

def get_scores():
    url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        response = requests.get(url).json()
        events = response.get('events', [])
        
        if not events:
            return "No NBA games scheduled today.", False
            
        score_lines = []
        game_is_live = False
        
        for event in events:
            status_type = event['status']['type']['state'].lower()
            status_detail = event['status']['type']['detail']
            
            # Check if game is live
            if status_type in ['in', 'live'] or "quarter" in status_detail.lower() or "half" in status_detail.lower():
                game_is_live = True
            
            home = event['competitions'][0]['competitors'][0]
            away = event['competitions'][0]['competitors'][1]
            
            h_name = home['team']['abbreviation']
            h_score = home.get('score', '0')
            a_name = away['team']['abbreviation']
            a_score = away.get('score', '0')
            
            if status_type == 'pre':
                score_lines.append(f"{a_name} @ {h_name} ({status_detail})")
            else:
                score_lines.append(f"{a_name} {a_score} - {h_score} {h_name} ({status_detail})")
        
        return "\n".join(score_lines), game_is_live
    except Exception:
        return "Error fetching scores.", False

def send_to_groupme(text):
    if not BOT_ID:
        print("Error: No Bot ID found in Secrets.")
        return
    requests.post("https://api.groupme.com/v3/bots/post", json={"bot_id": BOT_ID, "text": text})

# Run the checks
message, is_live = get_scores()

# Send the appropriate message
if is_live:
    send_to_groupme(message)
