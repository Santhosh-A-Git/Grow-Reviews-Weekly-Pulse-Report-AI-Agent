import re
import pandas as pd

def strip_pii(text: str) -> str:
    """
    Strips Personally Identifiable Information (PII) from the given text.
    Handles:
    - Standard Email addresses
    - Obfuscated Email addresses (e.g., name at domain dot com)
    - Phone numbers (basic international & domestic formats)
    - UUIDs/Device IDs
    """
    if not isinstance(text, str):
        return ""

    # 1. Strip Email Addresses
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text = re.sub(email_regex, '[EMAIL_REDACTED]', text)
    
    # 2. Strip Obfuscated Emails (e.g., john at gmail dot com)
    obfuscated_email_regex = r'[a-zA-Z0-9_.+-]+\s+(?:at|@)\s+[a-zA-Z0-9-]+\s+(?:dot|\.)\s+[a-zA-Z]{2,}'
    text = re.sub(obfuscated_email_regex, '[EMAIL_REDACTED]', text, flags=re.IGNORECASE)

    # 3. Strip UUIDs / Device IDs (Must happen BEFORE phone numbers to prevent partial matches)
    uuid_regex = r'\b[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}\b'
    text = re.sub(uuid_regex, '[ID_REDACTED]', text)

    # 4. Strip Phone Numbers
    phone_regex = r'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'
    # A broader phone regex to catch standard numeric sequences typical in reviews:
    broad_phone_regex = r'\+?\b(?:\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    text = re.sub(broad_phone_regex, '[PHONE_REDACTED]', text)
    
    # 5. Strip custom User IDs often found in format: user_12345, id: 9876
    user_id_regex = r'(?i)\b(?:user|id|device)[\s_-]*[:#]?[\s]*(?!REDACTED)[a-zA-Z0-9]{5,}\b'
    text = re.sub(user_id_regex, '[USER_ID_REDACTED]', text)

    return text.strip()

def filter_spam(df: pd.DataFrame, min_length: int = 4) -> pd.DataFrame:
    """
    Filters out spam or empty reviews to improve signal-to-noise ratio.
    Removes:
    - Reviews shorter than min_length characters
    - Reviews consisting entirely of redacted PII
    """
    if df.empty or 'review_text' not in df.columns:
        return df
        
    # Apply PII stripping to the entire column
    df['clean_text'] = df['review_text'].apply(strip_pii)
    
    # Remove rows where the clean text is too short (e.g. "ok", "hi")
    df = df[df['clean_text'].str.len() >= min_length]
    
    # Remove rows that are just redaction tags
    # E.g., if a user just posted "[EMAIL_REDACTED]" it's useless now.
    useless_patterns = ['[EMAIL_REDACTED]', '[PHONE_REDACTED]', '[ID_REDACTED]', '[USER_ID_REDACTED]']
    
    def is_useless(text):
        for pattern in useless_patterns:
            text = text.replace(pattern, '').strip()
        return len(text) < min_length

    df = df[~df['clean_text'].apply(is_useless)]
    
    return df

if __name__ == "__main__":
    import os
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    input_file = os.path.join(data_dir, 'groww_live_reviews.csv')
    output_file = os.path.join(data_dir, 'groww_live_reviews_clean.csv')
    
    if os.path.exists(input_file):
        print(f"Loading raw dataset from {input_file}...")
        df = pd.read_csv(input_file)
        
        print("Applying PII stripping and secondary spam filtering...")
        clean_df = filter_spam(df, min_length=4)
        
        clean_df.to_csv(output_file, index=False, encoding='utf-8')
        json_output = output_file.replace('.csv', '.json')
        clean_df.to_json(json_output, orient='records', indent=2, date_format='iso')
        
        print(f"Sanitization complete! Kept {len(clean_df)} reviews.")
        print(f"Saved cleaned dataset to {output_file} and {json_output}")
    else:
        print(f"Error: {input_file} not found. Please run ingestion.py first.")
