import unittest
import logging
from aiocutter import aiocutter
from aiocutter.test.news import BBCTopNews, BBCNews
from aiocutter.test.github_issue import GithubIssue


class TestAioCutter(unittest.TestCase):

    def test_set_proxy(self):
        # usual proxy
        proxy = "http://proxy:8080"
        cutter = aiocutter.AioCutter(proxy=proxy)
        self.assertEqual(cutter._connector._proxy, proxy)

        # with auth
        for p in ["http://user:p@ssword@proxy:8080", "http://user:p%40ssword@proxy:8080"]:
            cutter = aiocutter.AioCutter(proxy=p)
            self.assertEqual(cutter._connector._proxy, proxy)
            self.assertEqual(cutter._connector._proxy_auth.login, "user")
            self.assertEqual(cutter._connector._proxy_auth.password, "p@ssword")

    def test_single_scrap(self):
        url = "http://www.bbc.com/news/science_and_environment/"
        cutter = aiocutter.AioCutter(data_folder="./data")
        BBCTopNews.Relations.clear()
        result = cutter.run(url, BBCTopNews)

        for r in result:
            self.assertTrue(r.title)
            self.assertTrue(r.desc)
            print(r)

        self.assertEqual(len(result), 3)

    def test_relation(self):

        url = "http://www.bbc.com/news/science_and_environment/"
        cutter = aiocutter.AioCutter(data_folder="./data")
        BBCTopNews.add_relation(BBCNews)
        result = cutter.run(url, BBCTopNews)

        for r in result:
            self.assertTrue(BBCNews.__name__ in r.relates)
            for n in r.relates[BBCNews.__name__]:
                print(n)

    def test_paging(self):

        url = "https://github.com/python/pythondotorg/issues"
        cutter = aiocutter.AioCutter(data_folder="./data", log_level=logging.DEBUG)
        result = cutter.run(url, GithubIssue)

        for r in result[:10]:
            print(r)

        self.assertTrue(len(result) > 0)
