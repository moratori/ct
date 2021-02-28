#!/usr/bin/env python3

"""
docstring is here
"""

import common.framework.application.dbapplication.mysqlapplication as appframe
from typing import Any
from common.data.db.LogServer import LogServer
from common.framework.dbsession import local_session


global LOGGER


class MaintainLogServer(appframe.MySQLApplication):

    def __init__(self) -> None:
        super().__init__(__name__, __file__)

    def validate_config(self) -> None:
        super().validate_config()
        int(self.conf.self.ctclient.timeout)
        int(self.conf.self.maintain.failed_threshold)

    def setup_resource(self) -> None:
        super().setup_resource()

    def setup_application(self) -> None:
        pass

    def countup_failed_cnt(self) -> None:

        with local_session(self.thread_local_session_maker,
                           commit_on_exit=True) as session:

            servers = session.query(LogServer).all()

            for server in servers:
                if not server.is_readable(self.conf.self.ctclient.timeout):
                    LOGGER.info("unreadable server found: %s" % (server.url))
                    server.access_failed_cnt += 1

    def deactivate_logserver(self) -> None:

        th = self.conf.self.maintain.failed_threshold

        with local_session(self.thread_local_session_maker,
                           commit_on_exit=True) as session:

            target = session.query(LogServer.log_id).\
                filter(LogServer.access_failed_cnt >= th).\
                all()

            for server in target:
                LOGGER.info("deactivating log server: %s" % server.url)
                server.deactivated = True

    def run_application(self, **args: Any) -> None:
        self.countup_failed_cnt()
        self.deactivate_logserver()

    def teardown_application(self) -> None:
        pass

    def teardown_resource(self) -> None:
        pass


if __name__ == "__main__":
    app = MaintainLogServer()
    LOGGER = app.create_toplevel_logger()
    app.start()
