from urllib.parse import urlparse
import re
from rake_nltk import Rake
import nltk
from nltk.corpus import stopwords
import wikipedia

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

def extract_url_tags(url: str) -> list:
    """Extract meaningful tags from URL path segments"""
    parsed = urlparse(url)
    path = re.sub(r'\d+', '', parsed.path)  # Remove numbers
    segments = re.findall(r'[\w-]+', path)
    
    custom_blacklist = {'watch', 'video', 'product', 'article', 'tag', 'page'}
    tags = []
    
    for segment in segments:
        # Split camelCase and hyphenated words
        words = re.sub(r'([a-z])([A-Z])', r'\1 \2', segment).split('-')
        for word in words:
            word_clean = re.sub(r'[^a-zA-Z]', '', word).lower()
            if (word_clean 
                and len(word_clean) > 2 
                and word_clean not in custom_blacklist
            ):
                tags.append(word_clean)
    
    return tags

def extract_priority_terms(text: str) -> list:
    patterns = [
        r'\b[A-Z]{2,}\b',  # Acronyms like AI
        r'\b\d+[kmg]?b\b',  # Tech terms like 4K
        r'\b[a-z]+-[a-z]+\b',  # Hyphenated terms
    ]
    return list(set(
        term.lower()
        for pattern in patterns
        for term in re.findall(pattern, text)
    ))

def extract_keywords(text: str) -> list:
    priority_terms = extract_priority_terms(text)
    
    r = Rake(
        min_length=2,
        max_length=3,
        include_repeated_phrases=False
    )
    r.extract_keywords_from_text(text)
    phrases = r.get_ranked_phrases()[:7] 

    valid_phrases = []
    for phrase in phrases:
        if any(c.isupper() for c in phrase):  
            valid_phrases.append(phrase)
        elif len(phrase.split()) > 1:
            valid_phrases.append(phrase.replace(' ', '-'))

    return priority_terms + valid_phrases[:5]

def get_wikipedia_tags(title: str, description: str) -> list:
    wikipedia.set_lang('en')
    try:
        search_results = wikipedia.search(title)[:3]  # Top 3 results
        context_words = set(
            re.findall(r'\w+', f"{title.lower()} {description.lower()}")
        )
        tags = []
        
        for result in search_results:
            if '(disambiguation)' in result:
                continue
                
            # Check title overlap with Wikipedia result
            result_words = set(re.findall(r'\w+', result.lower()))
            if any(word in context_words for word in result_words):
                tags.extend([
                    word for word in result_words 
                    if word not in stopwords.words('english')
                ])
        
        return list(set(tags))
    except:
        return []

def clean_tags(tags: list) -> list:
    # Filter criteria
    bad_patterns = {
        'test', 'report', 'hidden', 'secret', 'howto', 
        'page', 'based', 'new', 'use', 'basic'
    }
    
    return [
        tag.lower() for tag in tags
        if (tag not in bad_patterns and
            not tag.isnumeric() and
            3 < len(tag) < 25 and
            not re.search(r'^https?://', tag))
    ]

def auto_tag_bookmark(url: str, title: str, description: str) -> list:
    url_tags = extract_url_tags(url)
    text = f"{title} {description}"
    tfidf_tags = extract_keywords(text)
    wiki_tags = get_wikipedia_tags(title, description)
    
    all_tags = url_tags + tfidf_tags + wiki_tags
    unique_tags = list(set(all_tags))
    
    return clean_tags(unique_tags)[:10]

# # Test functions
# def test_article_berlin():
#     url = "https://travelblog.com/The-excursion-in-Berlin"
#     title = "Exploring Berlin's Hidden Gems"
#     description = "A comprehensive guide to the best walking tours and historical excursions in Germany's capital city Berlin"
#     tags = auto_tag_bookmark(url, title, description)
#     print(f"\nTest 1 - Berlin Article:\nURL: {url}\nTags: {tags}")

# def test_youtube_baking():
#     url = "https://youtube.com/watch?v=XYZ_Chocolate-Cake-Tutorial"
#     title = "Professional Chocolate Cake Recipe"
#     description = "Learn how to make moist chocolate cake with ganache frosting - baking techniques from master pastry chefs"
#     tags = auto_tag_bookmark(url, title, description)
#     print(f"\nTest 2 - Baking Video:\nURL: {url}\nTags: {tags}")

# def test_amazon_product():
#     url = "https://amazon.com/Sony-Alpha-Mirrorless-Digital-Camera"
#     title = "Sony α7 IV Full-Frame Mirrorless Camera"
#     description = "Professional 33MP digital camera with 4K video, advanced autofocus, and 15-stop dynamic range"
#     tags = auto_tag_bookmark(url, title, description)
#     print(f"\nTest 3 - Camera Product:\nURL: {url}\nTags: {tags}")

# def test_tech_article():
#     url = "https://techcrunch.com/AI-Healthcare-Revolution-2024"
#     title = "AI Transforming Medical Diagnostics"
#     description = "How machine learning algorithms are revolutionizing early cancer detection and patient care"
#     tags = auto_tag_bookmark(url, title, description)
#     print(f"\nTest 4 - Tech Article:\nURL: {url}\nTags: {tags}")

# def test_news_climate():
#     url = "https://bbc.com/Renewable-Energy-Breakthrough-Report"
#     title = "Solar Panel Efficiency Reaches New Record"
#     description = "Scientists develop perovskite solar cells achieving 33.7% energy conversion efficiency in laboratory tests"
#     tags = auto_tag_bookmark(url, title, description)
#     print(f"\nTest 5 - Climate News:\nURL: {url}\nTags: {tags}")

# if __name__ == "__main__":
#     test_article_berlin()
#     test_youtube_baking()
#     test_amazon_product()
#     test_tech_article()
#     test_news_climate()