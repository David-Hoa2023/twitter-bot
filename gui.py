import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from quantpy_feed.twitter_feed_bot import TwitterBot
from quantpy_feed.call_openai import generate_response
from langchain.schema import HumanMessage

# Initialize TwitterBot and Scheduler
twitter_bot = TwitterBot()
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

def generate_tweet_with_topic(topic, title):
    # Use the generate_response function from call_openai.py for consistent prompt and process
    long_response, short_response = generate_response(twitter_bot.llm, topic, title)
    return long_response

def generate_tweet_from_text(text):
    prompt = f"""
hãy dùng phong cách dev, informal, dùng cho mạng xã hội để viết lại và mở rộng bài bên dưới bằng cách thêm các anecdotes và ví dụ minh họa. hãy tiết chế hài nhảm, fluff, KHÔNG DÙNG EMOJI. output in English
* Use simple language: Write plainly with short sentences.
* Avoid AI-giveaway phrases: Don't use clichés like 'dive into,' 'unleash your potential,' etc.
* Be direct and concise: Get to the point; remove unnecessary words.
* Maintain a natural tone: Write as you normally speak; it's okay to start sentences with 'and' or 'but.'
* Avoid marketing language: Don't use hype or promotional words.
* Keep it real: Be honest; don't force friendliness.
* Simplify grammar: Don't stress about perfect grammar; it's fine not to capitalize 'i' if that's your style.
* Stay away from fluff: Avoid unnecessary adjectives and adverbs.
* Focus on clarity: Make your message easy to understand.

Bài gốc:
{text}
"""
    # Use HumanMessage for chat models
    response = twitter_bot.llm([HumanMessage(content=prompt)])
    return response.content

def post_tweet(tweet_text):
    # Post the tweet using TwitterBot's API
    class DummyTweet:
        def to_text(self):
            return tweet_text
    twitter_bot.post_tweet(DummyTweet())

def schedule_tweet(tweet_text, run_datetime):
    scheduler.add_job(post_tweet, 'date', run_date=run_datetime, args=[tweet_text])

def on_generate():
    option = option_var.get()
    if option == 1:
        topic = topic_entry.get()
        title = title_entry.get()
        if not topic or not title:
            messagebox.showerror("Input Error", "Please enter both topic and title.")
            return
        tweet = generate_tweet_with_topic(topic, title)
    else:
        text = text_entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Input Error", "Please enter the text.")
            return
        tweet = generate_tweet_from_text(text)
    tweet_display.delete("1.0", tk.END)
    tweet_display.insert(tk.END, tweet)

def on_schedule():
    tweet = tweet_display.get("1.0", tk.END).strip()
    if not tweet:
        messagebox.showerror("No Tweet", "Please generate a tweet first.")
        return
    date_str = date_entry.get()
    time_str = time_entry.get()
    try:
        run_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        messagebox.showerror("Date/Time Error", "Please enter date and time in the correct format.")
        return
    schedule_tweet(tweet, run_datetime)
    messagebox.showinfo("Scheduled", f"Tweet scheduled for {run_datetime}")

def on_option_change():
    if option_var.get() == 1:
        topic_entry.config(state='normal')
        title_entry.config(state='normal')
        text_entry.config(state='disabled')
    else:
        topic_entry.config(state='disabled')
        title_entry.config(state='disabled')
        text_entry.config(state='normal')

root = tk.Tk()
root.title("QuantPy Twitter Bot GUI")

option_var = tk.IntVar(value=1)

# Option selection
option_frame = ttk.LabelFrame(root, text="Tweet Generation Options")
option_frame.pack(fill='x', padx=10, pady=5)

tk.Radiobutton(option_frame, text="Generate with topic and title", variable=option_var, value=1, command=on_option_change).pack(anchor='w')
tk.Radiobutton(option_frame, text="Generate from provided text", variable=option_var, value=2, command=on_option_change).pack(anchor='w')

# Topic and title
topic_label = ttk.Label(option_frame, text="Topic:")
topic_label.pack(anchor='w')
topic_entry = ttk.Entry(option_frame, width=40)
topic_entry.pack(anchor='w', padx=20)

title_label = ttk.Label(option_frame, text="Title:")
title_label.pack(anchor='w')
title_entry = ttk.Entry(option_frame, width=40)
title_entry.pack(anchor='w', padx=20)

# Text input
text_label = ttk.Label(option_frame, text="Text:")
text_label.pack(anchor='w')
text_entry = tk.Text(option_frame, height=4, width=40, state='disabled')
text_entry.pack(anchor='w', padx=20)

# Generate button
generate_btn = ttk.Button(root, text="Generate Tweet", command=on_generate)
generate_btn.pack(pady=5)

# Tweet display
tweet_display = tk.Text(root, height=6, width=60)
tweet_display.pack(padx=10, pady=5)

# Schedule controls
schedule_frame = ttk.LabelFrame(root, text="Schedule Tweet Publishing")
schedule_frame.pack(fill='x', padx=10, pady=5)

date_label = ttk.Label(schedule_frame, text="Date (YYYY-MM-DD):")
date_label.pack(anchor='w')
date_entry = ttk.Entry(schedule_frame, width=20)
date_entry.pack(anchor='w', padx=20)

time_label = ttk.Label(schedule_frame, text="Time (HH:MM, 24h):")
time_label.pack(anchor='w')
time_entry = ttk.Entry(schedule_frame, width=20)
time_entry.pack(anchor='w', padx=20)

schedule_btn = ttk.Button(schedule_frame, text="Schedule Tweet", command=on_schedule)
schedule_btn.pack(pady=5)

on_option_change()
root.mainloop() 