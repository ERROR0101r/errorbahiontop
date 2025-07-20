#!/usr/bin/env python3
# OSINT TOOL WITH 40+ SITES - By @ERROR0101r

import os
import requests
from termcolor import colored
import pyfiglet
from datetime import datetime

# ===== 40+ POPULAR SITES =====
SITES = [
    {"name": "GitHub", "url": "https://github.com/{}", "info": "Code repositories"},
    {"name": "Twitter", "url": "https://twitter.com/{}", "info": "Social media profile"},
    {"name": "Instagram", "url": "https://instagram.com/{}", "info": "Photos and profile"},
    {"name": "Facebook", "url": "https://facebook.com/{}", "info": "Social profile"},
    {"name": "YouTube", "url": "https://youtube.com/{}", "info": "Video channel"},
    {"name": "Reddit", "url": "https://reddit.com/user/{}", "info": "Forum activity"},
    {"name": "Pinterest", "url": "https://pinterest.com/{}", "info": "Image collections"},
    {"name": "TikTok", "url": "https://tiktok.com/@{}", "info": "Short videos"},
    {"name": "Telegram", "url": "https://t.me/{}", "info": "Messenger profile"},
    {"name": "LinkedIn", "url": "https://linkedin.com/in/{}", "info": "Professional profile"},
    {"name": "Twitch", "url": "https://twitch.tv/{}", "info": "Live streams"},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}", "info": "Music profile"},
    {"name": "Discord", "url": "https://discord.com/users/{}", "info": "Gaming profile"},
    {"name": "Medium", "url": "https://medium.com/@{}", "info": "Blog articles"},
    {"name": "Quora", "url": "https://quora.com/profile/{}", "info": "Q&A profile"},
    {"name": "Vimeo", "url": "https://vimeo.com/{}", "info": "Video uploads"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}", "info": "Audio uploads"},
    {"name": "DeviantArt", "url": "https://{}.deviantart.com", "info": "Art portfolio"},
    {"name": "Flickr", "url": "https://flickr.com/people/{}", "info": "Photo sharing"},
    {"name": "Dribbble", "url": "https://dribbble.com/{}", "info": "Design portfolio"},
    {"name": "Behance", "url": "https://behance.net/{}", "info": "Creative work"},
    {"name": "VK", "url": "https://vk.com/{}", "info": "Russian social network"},
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}", "info": "Gaming profile"},
    {"name": "Xbox", "url": "https://xboxgamertag.com/search/{}", "info": "Gamer profile"},
    {"name": "PlayStation", "url": "https://psnprofiles.com/{}", "info": "PSN profile"},
    {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/User:{}", "info": "Wiki edits"},
    {"name": "Tumblr", "url": "https://{}.tumblr.com", "info": "Microblogging"},
    {"name": "Blogger", "url": "https://{}.blogspot.com", "info": "Blog platform"},
    {"name": "WordPress", "url": "https://{}.wordpress.com", "info": "Blog site"},
    {"name": "Ebay", "url": "https://www.ebay.com/usr/{}", "info": "Seller profile"},
    {"name": "Etsy", "url": "https://www.etsy.com/shop/{}", "info": "Crafts shop"},
    {"name": "Fiverr", "url": "https://www.fiverr.com/{}", "info": "Freelance profile"},
    {"name": "Upwork", "url": "https://www.upwork.com/freelancers/{}", "info": "Freelancer"},
    {"name": "CodePen", "url": "https://codepen.io/{}", "info": "Code snippets"},
    {"name": "GitLab", "url": "https://gitlab.com/{}", "info": "Code repositories"},
    {"name": "Bitbucket", "url": "https://bitbucket.org/{}", "info": "Code hosting"},
    {"name": "Keybase", "url": "https://keybase.io/{}", "info": "Encrypted identity"},
    {"name": "HackerNews", "url": "https://news.ycombinator.com/user?id={}", "info": "Tech forum"},
    {"name": "Slack", "url": "https://{}.slack.com", "info": "Workspace profile"},
    {"name": "StackOverflow", "url": "https://stackoverflow.com/users/{}", "info": "Q&A profile"},
    {"name": "Pastebin", "url": "https://pastebin.com/u/{}", "info": "Code pastes"},
    {"name": "Kickstarter", "url": "https://kickstarter.com/profile/{}", "info": "Project creator"},
    {"name": "Patreon", "url": "https://patreon.com/{}", "info": "Creator profile"},
    {"name": "Duolingo", "url": "https://duolingo.com/profile/{}", "info": "Language learning"}
]

def check_username(username):
    print(colored(f"\n🔍 Searching 40+ platforms for: @{username}", 'yellow'))
    results = []
    
    for site in SITES:
        try:
            url = site['url'].format(username)
            response = requests.get(
                url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10,
                allow_redirects=False
            )
            
            # Different checks for different sites
            if response.status_code == 200:
                print(colored(f"[✓] FOUND: {site['name']}", 'green'))
                print(colored(f"   🔗 Profile: {url}", 'cyan'))
                print(colored(f"   📝 Info: {site['info']}\n", 'yellow'))
                results.append(site)
            else:
                print(colored(f"[×] Not on {site['name']}", 'red'))
        except:
            print(colored(f"[!] Error checking {site['name']}", 'yellow'))
    
    print(colored(f"\n✅ Found on {len(results)} platforms", 'green'))
    return results

def main():
    print(colored(pyfiglet.figlet_format("OSINT TOOL"), 'red'))
    print(colored("v10.3 - 40+ Sites Search\n", 'yellow'))
    
    username = input(colored("[?] Enter username: ", 'green'))
    check_username(username)

if __name__ == "__main__":
    main()
