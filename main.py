import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import re

# Function to convert relative time (e.g. '22 hrs ago') to actual datetime
def parse_relative_time(time_str):
    # Check for the format like "4 hrs ago", "2 mins ago", etc.
    time_match = re.match(r"(\d+)\s*(hrs?|hours?|mins?|minutes?)\s*ago", time_str.lower())
    
    if time_match:
        quantity = int(time_match.group(1))  # Get the number of hours/minutes
        unit = time_match.group(2).lower()   # Get the unit ('hr' or 'min')
        
        if 'hr' in unit or 'hour' in unit:
            return datetime.now() - timedelta(hours=quantity)
        elif 'min' in unit or 'minute' in unit:
            return datetime.now() - timedelta(minutes=quantity)
    return datetime.now()  # Default to current time if not matched


# Define a function to scrape the news
def scrape_bbc_news():
    url = "https://www.bbc.com/news"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all articles (may need to adjust selectors based on the site structure)
    articles = soup.find_all('div', class_='sc-b8778340-0 kFuHJG')

    # Lists to store article data
    titles, dates, summaries, categories = [], [], [], []

    for article in articles:
        # Extract title
        title = article.find('div', class_='sc-8ea7699c-1 hxRodh').text if article.find('div', class_='sc-8ea7699c-1 hxRodh') else None
        titles.append(title)


       # Extract publication date (relative time, e.g., "22 hrs ago")
        date_tag = article.find('span', {'data-testid': 'card-metadata-lastupdated'})
        date = parse_relative_time(date_tag.text.strip()) if date_tag else datetime.now()
        dates.append(date)

        # Extract summary
        summary = article.find('p').text if article.find('p') else "No summary available"
        summaries.append(summary)

        # Extract category (if available)
        category = article.find('span', class_='sc-6fba5bd4-2 bHkTZK').text if article.find('span', class_='sc-6fba5bd4-2 bHkTZK') else "General"
        categories.append(category)

    # Create a DataFrame
    news_df = pd.DataFrame({
        'Title': titles,
        'Publication Date': dates,
        'Summary': summaries,
        'Category': categories
    })

    return news_df

# Streamlit app
st.title("Latest News Dashboard")
st.sidebar.title("Filters")

# Scrape news data
news_df = scrape_bbc_news()

# Set a default date range to display all news initially
default_start_date = datetime(2000, 1, 1).date()  # Arbitrary far past date
default_end_date = datetime.now().date()          # Current date

# Sidebar filters
start_date, end_date = st.sidebar.date_input("Select Date Range", [default_start_date, default_end_date])

category_filter = st.sidebar.multiselect("Select Category", news_df['Category'].unique())

if start_date and end_date:
    # Ensure 'Publication Date' is in datetime format
    news_df['Publication Date'] = pd.to_datetime(news_df['Publication Date'])
    news_df = news_df[(news_df['Publication Date'].dt.date >= start_date) & (news_df['Publication Date'].dt.date <= end_date)]

if category_filter:
    news_df = news_df[news_df['Category'].isin(category_filter)]

# Display news articles
for idx, row in news_df.iterrows():
    st.subheader(row['Title'])
    st.write(f"**Published on:** {row['Publication Date'].strftime('%Y-%m-%d')}")
    st.write(f"**Category:** {row['Category']}")
    st.write(row['Summary'])
    st.write("---")

