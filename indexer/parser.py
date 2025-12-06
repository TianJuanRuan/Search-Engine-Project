from bs4 import BeautifulSoup
from urllib.parse import urljoin

class Parser:

    def __init__(self, use_lxml: bool = True):
        self.use_lxml = use_lxml

    def _make_soup(self, html: str):
        parser_name = "lxml" if self.use_lxml else "html.parser"
        try:
            return BeautifulSoup(html or "", parser_name)
        except Exception:
            return BeautifulSoup(html or "", "html.parser")

    def parse(self, html: str, base_url: str):
        if not html:
            return "", [], set()

        soup = self._make_soup(html)

        important_words = set()

        if soup.title and soup.title.string:
            important_words.update(soup.title.get_text(separator=" ", strip=True).lower().split())

        for tag in soup.find_all(["h1", "h2", "h3"]):
            important_words.update(tag.get_text(separator=" ", strip=True).lower().split())

        for tag in soup.find_all(["b", "strong"]):
            important_words.update(tag.get_text(separator=" ", strip=True).lower().split())

        out_links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            anchor_text = a_tag.get_text(separator=" ", strip=True)
            try:
                absolute_url = urljoin(base_url, href).split("#")[0]
                out_links.append((absolute_url, anchor_text))
            except:
                continue

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.extract()

        text = soup.get_text(separator=" ", strip=True)

        return text, out_links, important_words
