
from newspaper import Article

def fetch_article_text(url):
    article = Article(url)
    article.download()
    article.parse()
    
    title = article.title
    author = ', '.join(article.authors)
    pub_date = article.publish_date
    article_text = article.text
    
    return title, author, pub_date, article_text

if __name__ == '__main__':
    url = 'https://www.aha.io/roadmapping/guide/ideation/templates'
    title, author, pub_date, article_text = fetch_article_text(url)
    
    print(f"Title: {title}\n")
    print(f"Author: {author}\n")
    print(f"Published Date: {pub_date}\n")
    print(f"Article Text: {article_text}\n")