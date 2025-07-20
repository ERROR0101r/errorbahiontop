import instaloader
import os
from datetime import datetime
from textwrap import fill

# Developer Credit
DEVELOPER = "@ERROR0101r"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    print("=" * 60)
    print(f"{'INSTAGRAM PROFILE ANALYZER':^60}")
    print(f"{'Developed by ' + DEVELOPER:^60}")
    print("=" * 60)
    print()

def get_profile(username):
    try:
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)
        return profile
    except Exception as e:
        print(f"🚨 Error: {str(e)}")
        return None

def save_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"\n📁 Data saved to '{filename}'")

def analyze_engagement(profile):
    if profile.mediacount == 0:
        return 0
    avg_likes = sum(post.likes for post in profile.get_posts()) / profile.mediacount
    engagement_rate = (avg_likes / profile.followers) * 100
    return round(engagement_rate, 2)

def display_profile(profile):
    clear_screen()
    display_header()
    
    print(f"👤 USERNAME: {profile.username}")
    print(f"📛 FULL NAME: {profile.full_name}")
    print(f"📌 BIO:\n{fill(profile.biography, width=60)}")
    print(f"🔗 EXTERNAL URL: {profile.external_url if profile.external_url else 'None'}")
    print(f"👥 FOLLOWERS: {profile.followers:,}")
    print(f"👤 FOLLOWING: {profile.followees:,}")
    print(f"📸 POSTS: {profile.mediacount:,}")
    print(f"🔒 PRIVATE: {'Yes' if profile.is_private else 'No'}")
    print(f"✅ VERIFIED: {'Yes' if profile.is_verified else 'No'}")
    print(f"📊 ENGAGEMENT RATE: {analyze_engagement(profile)}%")
    print("=" * 60)
    print()

def display_posts(profile, limit=3):
    print(f"📝 RECENT POSTS (Last {limit}):")
    print("=" * 60)
    
    for i, post in enumerate(profile.get_posts(), 1):
        if i > limit:
            break
        
        print(f"\n🆔 POST #{i}")
        print(f"📅 DATE: {post.date_local}")
        print(f"❤️ LIKES: {post.likes:,}")
        print(f"💬 COMMENTS: {post.comments:,}")
        print(f"👀 VIEWS: {post.video_view_count if post.is_video else 'N/A'}")
        
        # Caption Analysis
        print("\n📜 CAPTION:")
        print(fill(post.caption if post.caption else "No caption", width=60))
        
        # Hashtags & Mentions
        if post.caption:
            hashtags = [word for word in post.caption.split() if word.startswith('#')]
            mentions = [word for word in post.caption.split() if word.startswith('@')]
            
            if hashtags:
                print("\n🔖 HASHTAGS: " + ", ".join(hashtags))
            if mentions:
                print("\n👥 MENTIONS: " + ", ".join(mentions))
        
        # Top Comments
        print("\n🏆 TOP COMMENTS:")
        comments = list(post.get_comments())
        if comments:
            top_comments = sorted(comments, key=lambda c: c.likes_count, reverse=True)[:3]
            for j, comment in enumerate(top_comments, 1):
                print(f"{j}. 👤 {comment.owner.username}: {fill(comment.text, width=50)}")
                print(f"   ❤️ {comment.likes_count} likes")
        else:
            print("No comments yet.")
        
        print("-" * 60)
    
    print("=" * 60)
    print()

def display_followers_following(profile, limit=5):
    print("👥 FOLLOWERS & FOLLOWING ANALYSIS")
    print("=" * 60)
    
    try:
        # Followers
        followers = list(profile.get_followers())
        print(f"\n🫂 TOTAL FOLLOWERS: {len(followers):,}")
        print("🔍 SAMPLE FOLLOWERS:")
        for i, follower in enumerate(followers[:limit], 1):
            print(f"{i}. {follower.username} ({follower.full_name})")
        
        # Following
        following = list(profile.get_followees())
        print(f"\n👤 TOTAL FOLLOWING: {len(following):,}")
        print("🔍 SAMPLE FOLLOWING:")
        for i, followee in enumerate(following[:limit], 1):
            print(f"{i}. {followee.username} ({followee.full_name})")
    
    except Exception as e:
        print(f"⚠️ Could not fetch followers/following: {str(e)}")
    
    print("=" * 60)
    print()

def display_stories_highlights(profile):
    print("📽️ STORIES & HIGHLIGHTS")
    print("=" * 60)
    
    L = instaloader.Instaloader()
    try:
        # Check active stories
        stories = L.get_stories([profile.userid])
        if stories:
            print("\n📱 ACTIVE STORIES:")
            for story in stories:
                print(f"- {story.media_count} story items")
        else:
            print("\nNo active stories.")
        
        # Check highlights
        highlights = list(profile.get_highlights())
        if highlights:
            print("\n🌟 HIGHLIGHTS:")
            for highlight in highlights:
                print(f"- {highlight.title} ({highlight.media_count} posts)")
        else:
            print("\nNo highlights available.")
    
    except Exception as e:
        print(f"⚠️ Could not fetch stories/highlights: {str(e)}")
    
    print("=" * 60)
    print()

def main():
    clear_screen()
    display_header()
    
    while True:
        username = input("Enter Instagram username (or 'quit' to exit): ").strip()
        
        if username.lower() == 'quit':
            print("\nThanks for using Instagram Profile Analyzer! 🚀")
            break
        
        profile = get_profile(username)
        if not profile:
            print("❌ Profile not found or private.")
            continue
        
        display_profile(profile)
        display_posts(profile)
        display_followers_following(profile)
        display_stories_highlights(profile)
        
        # Save data to file
        save_option = input("Save data to a file? (y/n): ").lower()
        if save_option == 'y':
            filename = f"instagram_{username}_report.txt"
            report = f"Instagram Profile Report for @{username}\nGenerated on {datetime.now()}\n\n"
            report += f"Followers: {profile.followers}\nFollowing: {profile.followees}\nPosts: {profile.mediacount}\n"
            report += f"Engagement Rate: {analyze_engagement(profile)}%\n"
            save_to_file(report, filename)
        
        input("\nPress Enter to analyze another profile...")
        clear_screen()
        display_header()

if __name__ == "__main__":
    main()
