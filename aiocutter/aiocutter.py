import os
import sys
import asyncio
import logging
import aiohttp
import bs4
from .logger import create_logger


class AioCutter():

    def __init__(self,
                 name=__name__,
                 parallel=5,
                 proxy=None,
                 proxy_auth=None,
                 is_write_file=True,
                 data_folder="",
                 dump_size=100,
                 log_level=logging.WARNING,
                 handler=logging.StreamHandler(sys.stderr)):

        self.name = name
        self._semaphore = asyncio.Semaphore(parallel)
        self._connector = None
        self._logger = create_logger(self.name, log_level, handler)
        self.is_write_file = is_write_file
        self.data_folder = data_folder
        if self.is_write_file and not self.data_folder:
            self.data_folder = os.path.join(os.path.dirname(sys.argv[0]), "./data")
        
        self.dump_size = dump_size

        if proxy:
            self._connector = aiohttp.ProxyConnector(proxy=proxy, proxy_auth=proxy_auth)
        else:
            if "HTTP_PROXY" in os.environ:
                env_proxy = os.environ["HTTP_PROXY"]
                self._connector = aiohttp.ProxyConnector(proxy=env_proxy)

    def run(self, url, scrap_class):
        if self.is_write_file and not os.path.exists(self.data_folder):
            raise Exception("Data folder {0} is not exist.".format(self.data_folder))

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self._scrape(url, scrap_class))
        return result

    @asyncio.coroutine
    def _scrape(self, url, scrap_class, root_chain=True):
        next_url = url
        result = []

        def fetch_relations(u, c, h):
            r_url = c.get_url(u, h)
            relation_ins = yield from self._scrape(r_url, c, root_chain=False)
            return c.__name__, relation_ins

        with (yield from self._semaphore):
            counter = 0
            while next_url:
                self._logger.debug("{0}[{1}]: {2}".format(scrap_class.__name__, counter, next_url))

                try:
                    html = yield from self.fetch(next_url)
                except Exception as ex:
                    self._logger.exception("Exception has occurred when fetching the url.")
                    next_url = ""  # exit loop
                    continue

                instances = []

                for el in scrap_class.get_iterator(next_url, html):
                    ins = scrap_class.create(next_url, el)

                    if len(scrap_class.get_relations()) > 0:
                        relations = asyncio.wait([fetch_relations(next_url, c, el) for c in scrap_class.get_relations()])
                        done, pending = yield from relations
                        for t in done:
                            try:
                                rel = t.result()
                                ins.relates[rel[0]] = rel[1]
                            except Exception as ex:
                                self._logger.exception("Exception has occurred when extracting relation.")

                    instances.append(ins)

                result += instances
                next_url = scrap_class.get_next_url(next_url, html)

                if root_chain and (len(result) % self.dump_size == 0 and len(result) // self.dump_size > 0):
                    index = (len(result) // self.dump_size - 1) * self.dump_size
                    self._write_file(result, index)

                counter += 1

        if root_chain and len(result) % self.dump_size > 0:
            index = 0 if len(result) < self.dump_size else (len(result) // self.dump_size - 1) * self.dump_size
            self._write_file(result, index)

        return result

    def _write_file(self, result, from_index=0):
        if not self.is_write_file:
            return False

        if len(result) == 0:
            return False

        # write spot and reviews to file
        name = result[len(result) - 1].__class__.__name__
        f_result = os.path.join(self.data_folder, "{0}.txt".format(name))
        lines = 0
        relations = {}

        write_type = "wb"
        if from_index > 0:
            write_type = "ab"

        if os.path.isfile(f_result):
            with open(f_result) as targetfile:
                lines = sum(1 for line in targetfile)

        with open(f_result, write_type) as outfile:
            self._logger.debug("Write {0} from {1} to {2}.".format(name, lines, len(result[from_index:]) - 1))
            for s in result[from_index:]:
                outfile.write((s.to_line() + "\r\n").encode("utf-8"))

                if s.relates and len(s.relates.keys()) > 0:
                    for k in [k for k in s.relates.keys() if len(s.relates[k]) > 0]:
                        if k not in relations:
                            relations[k] = []
                        relations[k] += s.relates[k]

        for k in relations:
            if from_index == 0:
                self._write_file(relations[k], 0)
            else:
                self._write_file(["DUMMY"] + relations[k], 1)

    @asyncio.coroutine
    def fetch(self, url):
        try:
            response = yield from self.__get(url)
            body = yield from response.read()
            soup = bs4.BeautifulSoup(body)
            return soup
        except Exception as e:
            self._logger.exception("Error has occurred when access to {0}.".format(url))
            raise e

    def __get(self, url):
        return aiohttp.request("GET", url, connector=self._connector)
