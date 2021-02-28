#!/usr/bin/env python3

"""
docstring is here
"""

import common.framework.application.dbapplication.mysqlapplication as appframe
from common.data.db.LogServer import LogServer
from common.framework.dbsession import local_session
from logic.loglistloader import get_log_list
from typing import List, Any


global LOGGER


class RegistLogServer(appframe.MySQLApplication):

    def __init__(self) -> None:
        super().__init__(__name__, __file__)

    def validate_config(self) -> None:
        super().validate_config()
        str(self.conf.self.loglist.url)
        int(self.conf.self.loglist.timeout)
        int(self.conf.self.ctclient.timeout)

    def setup_resource(self) -> None:
        super().setup_resource()

    def setup_application(self) -> None:
        pass

    def regist_readable_server(self,
                               servers: List[LogServer],
                               timeout: int) -> None:

        with local_session(self.thread_local_session_maker,
                           commit_on_exit=True) as session:

            for server in servers:
                alredy = session.query(LogServer).\
                    filter(LogServer.log_id == server.log_id).\
                    all()
                if not alredy and server.is_readable(timeout):
                    LOGGER.info("new log server found: %s" %
                                (str(server.url)))
                    session.add(server)

    def run_application(self, **args: Any) -> None:

        servers = get_log_list(self.conf.self.loglist.url,
                               self.conf.self.loglist.timeout)

        if servers is not None:
            self.regist_readable_server(
                servers,
                self.conf.self.ctclient.timeout)

    def teardown_application(self) -> None:
        pass

    def teardown_resource(self) -> None:
        pass


if __name__ == "__main__":
    app = RegistLogServer()
    LOGGER = app.create_toplevel_logger()
    app.start()
