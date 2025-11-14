from bs4 import BeautifulSoup

class HTMLParser:
    def __init__(self):
        pass

    def extract_text(self, html):
        if html is None:
            return "", ""

        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception:
            return "", ""

        # Remove unwanted tags
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.extract()
            
        important_fragments = []

        # Title
        if soup.title and soup.title.string:
            important_fragments.append(soup.title.string)

        # Headings
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                important_fragments.append(h.get_text(separator=" ", strip=True))

        # Bold and strong
        for b in soup.find_all(["b", "strong"]):
            important_fragments.append(b.get_text(separator=" ", strip=True))

        important_text = " ".join(important_fragments)

        normal_text = soup.get_text(separator=" ", strip=True)

        return normal_text, important_text
