import praw
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import cohere

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

reddit = praw.Reddit(
    client_id="rlgrpr8TzVLk6vyuD7Rw", 
    client_secret="SkUexiSzADrXXDCRD0c-maf0hywOQ",
    user_agent="script:GenAIInternAssignment:v1.0 (by u/Emergency-Fail4885)"
)


def get_user_data(username, max_items=20):
    redditor = reddit.redditor(username)
    data = {"username": username, "posts": [], "comments": []}

    try:
        for submission in redditor.submissions.new(limit=max_items):
            data["posts"].append({
                "title": submission.title,
                "body": submission.selftext,
                "subreddit": str(submission.subreddit),
                "created": datetime.utcfromtimestamp(
                    submission.created_utc).isoformat(),
                "url": submission.url,
                "score": submission.score
            })
        print(f"✅ Found {len(data['posts'])} posts for {username}")
    except Exception as e:
        print(f"⚠️ Could not fetch posts for {username}: {e}")

    try:
        for comment in redditor.comments.new(limit=max_items):
            data["comments"].append({
                "body": comment.body,
                "subreddit": str(comment.subreddit),
                "created": datetime.utcfromtimestamp(
                    comment.created_utc).isoformat(),
                "link": f"https://www.reddit.com{comment.permalink}",
                "score": comment.score
            })
        print(f"✅ Found {len(data['comments'])} comments for {username}")
    except Exception as e:
        print(f"⚠️ Could not fetch comments for {username}: {e}")

    os.makedirs("data", exist_ok=True)
    filepath = f"data/{username}_data.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Reddit data saved to: {filepath}")

    return data


def generate_persona(data):
    prompt = f"""
You are an AI language model that creates personality
profiles from Reddit activity.

Using the following posts and comments, write a persona that includes:
- Tone and writing style
- Interests and hobbies
- Beliefs and opinions
- Favorite subreddits
- Patterns in communication

Use quotes and specify whether they came from a post or comment.

Reddit data:
{json.dumps(data, indent=2)}
    """

    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        max_tokens=1000,
        temperature=0.7
    )

    return response.generations[0].text.strip()


def save_persona(username, persona_text):
    os.makedirs("outputs", exist_ok=True)
    filepath = f"outputs/{username}_persona.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(persona_text)
    print(f"✅ Persona saved to: {filepath}")


if __name__ == "__main__":
    username = "Hungry-Move-6603"
    print(f"🚀 Fetching data for u/{username}")
    reddit_data = get_user_data(username)
    persona_text = generate_persona(reddit_data)
    save_persona(username, persona_text)
