#!/usr/bin/env python3
"""
Cyber Bonsai - Terminal ASCII bonsai that grows or withers based on GitHub activity
"""

import os
import sys
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

# ASCII art states of the bonsai
BONSAI_STATES = {
    'dead': """
        |~|  
        | |  
      _/   \_
     /  ___  \
    |  /   \  |
    | |     | |
    | |     | |
    |_|_____|_|
    DEAD
    """,
    'withered': """
        |~|
        | |
       /   \
      /  ~  \
     /       \
    |    ~    |
    |    |    |
    |____|____|
    WITHERED
    """,
    'struggling': """
        |~|
        | |
       /| |\
      / | | \
     /  | |  \
    |   | |   |
    |  /   \  |
    |_|_____|_|
    STRUGGLING
    """,
    'healthy': """
         |~|
        /| |\
       / | | \
      /  | |  \
     |  /   \  |
     | /     \ |
     |/       \|
    |___________|
    HEALTHY
    """,
    'thriving': """
        __|~|__
       /  | |  \
      /   | |   \
     /    | |    \
    |    /   \    |
    |   /     \   |
    |  /       \  |
    |_____________|
    THRIVING!
    """,
    'legendary': """
      ___|~|___
     /   | |   \
    /    | |    \
   /     | |     \
  |     /   \     |
  |    /     \    |
  |   /       \   |
  |  /         \  |
  |_______________|
  LEGENDARY!!
    """
}


def get_github_contributions(username: str, token: str = None) -> int:
    """
    Fetch GitHub contribution count for the last 30 days
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    # Get events for the user (public events)
    url = f"https://api.github.com/users/{username}/events"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        events = response.json()
        
        # Count events from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_events = [
            e for e in events 
            if datetime.fromisoformat(e['created_at'].replace('Z', '+00:00')) > thirty_days_ago
        ]
        
        # Weight different event types
        score = 0
        for event in recent_events:
            event_type = event.get('type', '')
            if event_type == 'PushEvent':
                score += 2
            elif event_type in ['CreateEvent', 'PullRequestEvent']:
                score += 3
            elif event_type == 'IssuesEvent':
                score += 1
            else:
                score += 0.5
        
        return int(score)
    
    except Exception as e:
        print(f"Error fetching GitHub data: {e}", file=sys.stderr)
        return 0


def get_bonsai_state(contribution_score: int) -> str:
    """
    Determine bonsai state based on contribution score
    """
    if contribution_score < 5:
        return 'dead'
    elif contribution_score < 15:
        return 'withered'
    elif contribution_score < 30:
        return 'struggling'
    elif contribution_score < 50:
        return 'healthy'
    elif contribution_score < 80:
        return 'thriving'
    else:
        return 'legendary'


def display_bonsai(username: str, score: int, state: str):
    """
    Display the bonsai with stats
    """
    art = BONSAI_STATES.get(state, BONSAI_STATES['healthy'])
    
    # Clear screen (optional, for animation)
    # os.system('clear' if os.name == 'posix' else 'cls')
    
    print("\n" + "="*50)
    print(f"  🌳 CYBER BONSAI - @{username}")
    print("="*50)
    print(art)
    print(f"\n  Activity Score (30 days): {score}")
    print(f"  State: {state.upper()}")
    print("="*50)
    print("\n  Tip: Push code to make your bonsai grow!")
    print("="*50 + "\n")


def main():
    # Get GitHub username from env or args
    username = os.environ.get('GITHUB_USERNAME')
    token = os.environ.get('GITHUB_TOKEN')
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
    
    if not username:
        print("Usage: cyber-bonsai <github_username>")
        print("Or set GITHUB_USERNAME environment variable")
        sys.exit(1)
    
    # Fetch contributions
    score = get_github_contributions(username, token)
    
    # Determine state
    state = get_bonsai_state(score)
    
    # Display
    display_bonsai(username, score, state)


if __name__ == '__main__':
    main()
