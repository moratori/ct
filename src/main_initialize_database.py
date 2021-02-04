#!/usr/bin/env python3


import common.framework.application.mysqlapplication as appframe
import common.data.LogServer as LogServer

global LOGGER


class InitializeDatabase(appframe.MySQLApplication):

    def __init__(self):
        super().__init__(__name__, __file__)

    def validate_config(self):
        super().validate_config()

    def setup_resource(self):
        super().setup_resource()

    def setup_application(self):
        pass

    def run_application(self, **args):
        LogServers.Base.metadata.create_all(bind=self.dbengine)

    def teardown_application(self):
        pass

    def teardown_resource(self):
        pass


if __name__ == "__main__":
    dbapp = InitializeDatabase()
    LOGGER = dbapp.create_toplevel_logger()
    dbapp.start()
