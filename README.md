=================
aiocutter
=================

aiocutter is scraping tool for [asyncio](https://docs.python.org/3/library/asyncio.html).


## Usage

```
from aiocutter import aiocutter

url = "https://github.com/python/pythondotorg/issues"
cutter = aiocutter.AioCutter()
result = cutter.run(url, GithubIssue)
```

write scraping rule in the class which inherits `Scrap`.

```
from aiocutter.scrap import Scrap


class GithubIssue(Scrap):

    def __init__(self, title):
        super().__init__()
        self.title = title

    @classmethod
    def get_iterator(cls, url, html):
        issues = html.find_all("a", class_="issue-title-link")
        return issues

    @classmethod
    def get_next_url(cls, url, html):
        next_url = ""
        current = html.select("em.current")[0]
        next_link = current.find_next_siblings("a")
        if len(next_link) > 0 and next_link[0].string and next_link[0].string.isdigit():
            next_url = cls._make_abs_url(url, next_link[0]["href"])

        return next_url

    @classmethod
    def create(cls, url, html):
        title = cls._get_element_text(html)
        news = GithubIssue(title)
        return news

    def to_line(self):
        return "\t".join([self.title])

    def __str__(self):
        return self.to_line()

```

## Install

```
pip install aiocutter
```
