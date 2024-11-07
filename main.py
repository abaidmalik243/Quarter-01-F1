import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from datetime import datetime

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


        # Extract publication date (if available)
        date_tag = article.find('time')
        date = date_tag['datetime'] if date_tag else datetime.now().isoformat()
        dates.append(date)

        # Extract summary
        summary = article.find('p').text if article.find('p') else "No summary available"
        summaries.append(summary)

        # Extract category (if available)
        category = article.find('a', class_='gs-c-section-link').text if article.find('a', class_='gs-c-section-link') else "General"
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

# Convert date to datetime format for filtering
news_df['Publication Date'] = pd.to_datetime(news_df['Publication Date'])

# Sidebar filters
date_filter = st.sidebar.date_input("Select Date", [])
category_filter = st.sidebar.multiselect("Select Category", news_df['Category'].unique())

# Apply filters
if date_filter:
    news_df = news_df[news_df['Publication Date'].dt.date == date_filter]

if category_filter:
    news_df = news_df[news_df['Category'].isin(category_filter)]

# Display news articles
for idx, row in news_df.iterrows():
    st.subheader(row['Title'])
    st.write(f"**Published on:** {row['Publication Date'].strftime('%Y-%m-%d')}")
    st.write(f"**Category:** {row['Category']}")
    st.write(row['Summary'])
    st.write("---")

