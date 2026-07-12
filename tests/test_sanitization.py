import unittest
import pandas as pd
from src.sanitization import strip_pii, filter_spam

class TestSanitization(unittest.TestCase):

    def test_strip_standard_email(self):
        text = "Please fix my account at test@example.com!"
        result = strip_pii(text)
        self.assertEqual(result, "Please fix my account at [EMAIL_REDACTED]!")

    def test_strip_obfuscated_email(self):
        text = "Contact me at john at gmail dot com for details."
        result = strip_pii(text)
        self.assertEqual(result, "Contact me at [EMAIL_REDACTED] for details.")

    def test_strip_phone_number(self):
        text = "Call me back at 123-456-7890."
        result = strip_pii(text)
        self.assertEqual(result, "Call me back at [PHONE_REDACTED].")

        text2 = "International: +1 (800) 555-1234 is broken."
        result2 = strip_pii(text2)
        self.assertEqual(result2, "International: [PHONE_REDACTED] is broken.")

    def test_strip_uuid(self):
        text = "My device id is 123e4567-e89b-12d3-a456-426614174000."
        result = strip_pii(text)
        self.assertEqual(result, "My device id is [ID_REDACTED].")
        
    def test_strip_custom_user_id(self):
        text = "Fix this! My ID is user_12345."
        result = strip_pii(text)
        self.assertEqual(result, "Fix this! My ID is [USER_ID_REDACTED].")

    def test_filter_spam_length(self):
        data = {
            'review_text': [
                "This app is amazing and very useful.",
                "ok",
                "yes",
                "a",
                "The payments are failing constantly."
            ]
        }
        df = pd.DataFrame(data)
        filtered_df = filter_spam(df, min_length=4)
        self.assertEqual(len(filtered_df), 2)
        self.assertTrue("This app is amazing and very useful." in filtered_df['clean_text'].values)

    def test_filter_spam_useless_redactions(self):
        data = {
            'review_text': [
                "My email is test@gmail.com", 
                "Just an email: test@gmail.com",
                "Real review with email test@gmail.com, please fix the bug!"
            ]
        }
        df = pd.DataFrame(data)
        # "My email is " (12 chars) -> kept
        # "Just an email: " (15 chars) -> kept
        # Let's test a purely redacted string
        data_pure = {
            'review_text': ["test@gmail.com", "123-456-7890"]
        }
        df_pure = pd.DataFrame(data_pure)
        filtered_pure = filter_spam(df_pure)
        self.assertEqual(len(filtered_pure), 0)

if __name__ == '__main__':
    unittest.main()
