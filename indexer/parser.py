from bs4 import BeautifulSoup

class Parser:

    def __init__(self, use_lxml: bool = True):
        self.use_lxml = use_lxml

    def _make_soup(self, html: str):
        parser_name = "lxml" if self.use_lxml else "html.parser"
        try:
            return BeautifulSoup(html or "", parser_name)
        except Exception:
            return BeautifulSoup(html or "", "html.parser")

    def extract_text(self, html: str):
        """
        Returns:
            normal_text (str)
            important_text (str)
        """
        if not html:
            return "", ""

        soup = self._make_soup(html)

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.extract()

        # Important text: title, h1/h2/h3, bold/strong
        important_fragments = []

        # <title>
        if soup.title and soup.title.string:
            important_fragments.append(soup.title.string)

        # Headings
        for tag_name in ("h1", "h2", "h3"):
            for h in soup.find_all(tag_name):
                text = h.get_text(separator=" ", strip=True)
                if text:
                    important_fragments.append(text)

        # Bold / strong text
        for b in soup.find_all(["b", "strong"]):
            text = b.get_text(separator=" ", strip=True)
            if text:
                important_fragments.append(text)

        important_text = " ".join(important_fragments)

        normal_text = soup.get_text(separator=" ", strip=True)

        return normal_text, important_text
