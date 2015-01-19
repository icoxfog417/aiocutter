import urllib.parse as up
import bs4


class Scrap():

    def __init__(self):
        self.relates = {}

    def to_line(self):
        # override in sub class.
        values = []
        for k in self.__dict__.keys():
            values.append(self.__dict__[k])

        return "\t".join(values)

    @classmethod
    def get_relations(cls):
        # override in sub class.
        return []

    @classmethod
    def get_url(cls, url, html):
        # override in sub class.
        return ""

    @classmethod
    def get_iterator(cls, url, html):
        # override in sub class.
        return [html]

    @classmethod
    def create(cls, url, html):
        raise Exception("read_page method have to be overridedden in sub class of Scrap.")

    @classmethod
    def get_next_url(cls, url, html):
        # override in sub class.
        return ""

    @classmethod
    def _make_abs_url(cls, base_url, relative_url):
        return up.urljoin(base_url, relative_url)

    @classmethod
    def _trim(cls, text):
        if text:
            # \r\n is used to split line in data file. All cr in data is \n.
            return text.strip().replace("\r\n", "\n")
        else:
            return ""

    @classmethod
    def _get_query_parameter(cls, url, parameter_name):
        qs = up.urlparse(url).query
        qp = up.parse_qs(qs)

        if parameter_name in qp:
            return qp[parameter_name]
        else:
            return [""]

    @classmethod
    def _get_element_text(cls, html):
        texts = list(filter(lambda e: isinstance(e, bs4.NavigableString), html.contents))
        if len(texts) > 0:
            return cls._trim(texts[0])
        else:
            return ""
