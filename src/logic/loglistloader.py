#!/usr/bin/env python3

import requests
from common.data.db.LogServer import LogServer
from logging import getLogger
from typing import List, Optional

LOGGER = getLogger(__name__)


def get_log_list(url: str,
                 timeout: int) -> Optional[List[LogServer]]:

    LOGGER.info("retrieving log list: %s" % url)

    ret = requests.get(url, timeout=timeout)

    if ret.status_code != requests.codes.ok or \
            not ret.headers["content-type"].startswith("application/json"):
        return None

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
                access_failed_cnt=0))

    return result
