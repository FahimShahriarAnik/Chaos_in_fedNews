import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_json("2_months_data/filtered_posts.jsonl", lines=True)

# Convert timestamp to datetime
df["date"] = pd.to_datetime(df["created_utc"], unit="s")

# Daily post volume
daily_posts = df.set_index("date").resample("D").size()
daily_posts.plot(title="Daily Posts (Jan-Feb 2025)")
plt.xlabel("Date")
plt.ylabel("Posts")
plt.axvline(pd.Timestamp("2025-01-20"), color="red", linestyle="--", label="Event")
plt.show()

# Top 10 active users
top_users = df["author"].value_counts().head(10)
print("Top 10 Active Users:\n", top_users)

# Engagement metrics (pre/post event)
event_date = pd.Timestamp("2025-01-20")
df["period"] = df["date"].apply(lambda x: "Before" if x < event_date else "After")

engagement = df.groupby("period").agg(
    avg_comments=("num_comments", "mean"),
    avg_score=("score", "mean")
)
print("\nEngagement Trends:\n", engagement)