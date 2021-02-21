#!/usr/bin/env python3

"""
docstring is here
"""

import common.framework.application.mysqlapplication as appframe
from common.db.table import LogServer
from logic.loglist import LogList
from typing import List


global LOGGER


class RegistLogServer(appframe.MySQLApplication):

    def __init__(self):
        super().__init__(__name__, __file__)

    def validate_config(self):
        super().validate_config()
        str(self.conf.self.loglist.url)
        int(self.conf.self.loglist.timeout)
        int(self.conf.self.ctclient.timeout)

    def setup_resource(self):
        super().setup_resource()

    def setup_application(self):
        pass

    def regist_readable_server(self, servers: List[LogServer]):

        for server in servers:
            alredy = self.session.query(LogServer).\
                filter(LogServer.log_id == server.log_id).\
                all()
            if not alredy:
                LOGGER.info("new log server found: %s" %
                            (str(server.url)))
                self.session.add(server)

        self.session.commit()

    def run_application(self):
        loglist = LogList()
        loglist.get_list(
            self.conf.self.loglist.url,
            self.conf.self.loglist.timeout)

        readable = loglist.find_readable_server(
            self.conf.self.ctclient.timeout)

        self.regist_readable_server(readable)

    def teardown_application(self):
        pass

    def teardown_resource(self):
        pass


if __name__ == "__main__":
    app = RegistLogServer()
    LOGGER = app.create_toplevel_logger()
    app.start()
