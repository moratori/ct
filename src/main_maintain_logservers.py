#!/usr/bin/env python3

"""
docstring is here
"""

import common.framework.application.mysqlapplication as appframe
from common.db.table import LogServer
from logic.ctclient import CTclient
from typing import List


global LOGGER


class MaintainLogServer(appframe.MySQLApplication):

    def __init__(self):
        super().__init__(__name__, __file__)

    def validate_config(self):
        super().validate_config()
        int(self.conf.self.ctclient.timeout)
        int(self.conf.self.maintain.failed_threshold)

    def setup_resource(self):
        super().setup_resource()

    def setup_application(self):
        pass

    def countup_failed_cnt(self):

        servers: List[LogServer] = \
            self.session.query(LogServer).all()

        for server in servers:
            url = server.url
            client = CTclient(url, self.conf.self.ctclient.timeout)
            if client.is_unreadable_server():
                LOGGER.info("unreadable server found: %s" % (url))
                server.access_failed_cnt += 1

        self.session.commit()

    def deactivate_logserver(self):

        th = self.conf.self.maintain.failed_threshold

        target: List[LogServer] = \
            self.session.query(LogServer.log_id).\
            filter(LogServer.access_failed_cnt >= th).\
            all()

        for server in target:
            LOGGER.info("deactivating log server: %s" % server.url)
            server.deactivated = True

        self.session.commit()

    def run_application(self):
        self.countup_failed_cnt()
        self.deactivate_logserver()

    def teardown_application(self):
        pass

    def teardown_resource(self):
        pass


if __name__ == "__main__":
    app = MaintainLogServer()
    LOGGER = app.create_toplevel_logger()
    app.start()
