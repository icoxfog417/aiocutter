from aiocutter.scrap import Scrap
from urllib.parse import urlparse


class BBCTopNews(Scrap):
    Relations = []

    def __init__(self, title, desc):
        super().__init__()
        self.title = title
        self.desc = desc

    @classmethod
    def get_iterator(cls, url, html):
        top = html.find(id="top-story")
        second = html.find(id="second-story")
        third = html.find(id="third-story")

        return [top, second, third]

    @classmethod
    def get_relations(cls):
        # override in sub class.
        return cls.Relations

    @classmethod
    def add_relation(cls, scrap_class):
        cls.Relations.append(scrap_class)

    @classmethod
    def clear_relations(cls):
        cls.Relations.clear()

    @classmethod
    def create(cls, url, html):
        title = cls._get_element_text(html.h2.a)
        desc = cls._get_element_text(html.p)

        news = BBCTopNews(title, desc)
        return news

    def to_line(self):
        return "\t".join([self.title, self.desc])

    def __str__(self):
        return self.to_line()


class BBCNews(Scrap):

    def __init__(self, news_id, title, introduction, paragraphs):
        super().__init__()
        self.news_id = news_id
        self.title = title
        self.introduction = introduction
        self.paragraphs = paragraphs

    @classmethod
    def get_url(cls, url, html):
        link = html.h2.a["href"]
        abs_url = cls._make_abs_url(url, link)
        return abs_url

    @classmethod
    def create(cls, url, html):
        parsed = urlparse(url)
        pathes = parsed.path.split("/")
        path_params = pathes[len(pathes) - 1].split("-")

        news_id = path_params[len(path_params) - 1]
        title = html.select(".story-header")[0].string
        introduction = cls._get_element_text(html.select(".introduction")[0])
        paragraphs = list(map(lambda p: p.string, html.select(".cross-head")))

        news = BBCNews(news_id, title, introduction, paragraphs)
        return news

    def to_line(self):
        return "\t".join([self.news_id, self.title, self.introduction, ",".join(self.paragraphs)])

    def __str__(self):
        return self.to_line()
