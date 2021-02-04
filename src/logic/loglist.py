#!/usr/bin/env python3

import requests
import datetime
from common.data.logserver import LogServer
from logic.ctclient import CTclient
from logging import getLogger
from typing import List

LOGGER = getLogger(__name__)


class LogList:

    def __init__(self, loglist=[]):
        self.loglist: List[LogServer] = loglist

    def get_list(self, url, timeout):

        LOGGER.info("retrieving log list: %s" % url)

        ret = requests.get(url, timeout=timeout)

        if ret.status_code != requests.codes.ok or \
                not ret.headers["content-type"].startswith("application/json"):
            return

        current_time = datetime.datetime.utcnow()
        result = []

        for each in ret.json()["operators"]:
            operator = each["name"]
            logs = each["logs"]

            for log in logs:
                result.append(LogServer(
                    log_id=log["log_id"],
                    operator=operator,
                    description=log["description"],
                    url=log["url"],
                    added_at=current_time,
                    access_failed_cnt=0))

        self.loglist = result

    def __find_server(self, test, timeout) -> List[LogServer]:
        result = []
        for server in self.loglist:
            client = CTclient(server.url, timeout)
            if test(client.get_certificates(0, 0)):
                result.append(server)
        return result

    def find_readable_server(self, timeout) -> List[LogServer]:
        return self.__find_server(lambda x: len(x) > 0,
                                  timeout)

    def find_unreadable_server(self, timeout) -> List[LogServer]:
        return self.__find_server(lambda x: len(x) <= 0,
                                  timeout)
