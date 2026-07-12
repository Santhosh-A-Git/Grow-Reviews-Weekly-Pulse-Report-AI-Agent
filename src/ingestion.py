import pandas as pd
from datetime import datetime, timedelta, timezone
from google_play_scraper import reviews, Sort
import emoji
from langdetect import detect, DetectorFactory
import langdetect.lang_detect_exception

# Ensure deterministic language detection
DetectorFactory.seed = 0

def load_play_store_reviews(package_name: str, count: int = 8000) -> pd.DataFrame:
    """Fetch recent Google Play reviews."""
    print(f"Fetching Android reviews for {package_name} (Target: {count})...")
    result, _ = reviews(
        package_name,
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=count
    )
    
    if not result:
        return pd.DataFrame()
        
    df = pd.DataFrame(result)
    df = df.rename(columns={
        'at': 'submitted_at',
        'content': 'review_text',
        'score': 'score',
        'userName': 'review_title', # GP doesn't have a specific title field, so mapping user name here
        'reviewId': 'review_id'
    })
    
    df['source'] = 'Play Store'
    df['submitted_at'] = pd.to_datetime(df['submitted_at'], utc=True)
    return df

def is_english(text: str) -> bool:
    """Check if the text is primarily English."""
    try:
        lang = detect(text)
        return lang == 'en'
    except langdetect.lang_detect_exception.LangDetectException:
        # If language can't be detected (e.g. only numbers/symbols), assume not english
        return False

def filter_quality_reviews(df: pd.DataFrame, weeks: int = 12, min_words: int = 8) -> pd.DataFrame:
    """Apply strict quality filters to the reviews DataFrame."""
    # 1. Drop rows with empty review text
    if 'review_text' not in df.columns:
        return df
        
    df = df.dropna(subset=['review_text'])
    df = df[df['review_text'].str.strip() != '']
    
    # 2. Filter by date (last 8-12 weeks)
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(weeks=weeks)
    df = df[df['submitted_at'] >= cutoff_date]
    
    # 3. Filter by word count
    # Split by whitespace to approximate word count
    df = df[df['review_text'].apply(lambda x: len(str(x).split()) >= min_words)]
    
    # 4. Remove reviews containing emojis
    # emoji_count returns the number of emojis in the string
    df = df[df['review_text'].apply(lambda x: emoji.emoji_count(str(x)) == 0)]
    
    # 5. Remove non-English (e.g. Hindi, Hinglish flagged as 'hi' or 'pt' etc)
    df = df[df['review_text'].apply(is_english)]
    
    return df

def ingest_reviews(android_package: str, weeks: int = 12, target_count: int = 8000) -> pd.DataFrame:
    """Main function to fetch and strictly filter reviews."""
    try:
        df = load_play_store_reviews(android_package, count=target_count)
    except Exception as e:
        print(f"Failed to load Play Store reviews: {e}")
        return pd.DataFrame()

    if df.empty:
        return df
        
    print(f"Fetched {len(df)} raw reviews. Applying quality filters (words >= 8, no emojis, en only)...")
    filtered_df = filter_quality_reviews(df, weeks=weeks)
    return filtered_df

if __name__ == "__main__":
    # Target: Groww App
    ANDROID_PACKAGE = "com.nextbillion.groww"
    
    print("Ingesting reviews for Groww (Strict Filtering Mode)...")
    df = ingest_reviews(ANDROID_PACKAGE, weeks=12, target_count=8000)
    
    if df.empty:
        print("No valid reviews found after filtering.")
    else:
        print(f"\nTotal high-quality reviews retained: {len(df)}")
        print("Sample data ready. (Skipping console print to avoid Windows emoji/encoding errors)")
        
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'groww_live_reviews.csv')
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nSaved scraped & filtered reviews to {output_file}")
