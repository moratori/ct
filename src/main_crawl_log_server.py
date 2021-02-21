#!/usr/bin/env python3

"""
docstring is here
"""

import common.framework.application.mysqlapplication as appframe
import datetime
import binascii
from cryptography.hazmat.primitives import hashes
from typing import List
from sqlalchemy.sql.expression import false
from common.db.table import LogServer
from logic.ctclient import CTclient


global LOGGER


class CrawlLogServer(appframe.MySQLApplication):

    def __init__(self):
        super().__init__(__name__, __file__)

    def validate_config(self):
        super().validate_config()
        int(self.conf.self.crawler.entry_fetch_step)
        int(self.conf.self.ctclient.timeout)

    def setup_resource(self):
        super().setup_resource()

    def setup_application(self):
        pass

    def calculate_fp_sha256(self, cert):

        return binascii.b2a_hex(
            cert.fingerprint(hashes.SHA256())).decode("utf8").upper()

    def calculate_fp_sha1(self, cert):

        return binascii.b2a_hex(
            cert.fingerprint(hashes.SHA1())).decode("utf8").upper()

    def get_sans_id(self, cert):
        pass

    def regist_certificates(self, log_id, cert_info):

        (precert_flag, pem, cert, entry_num) = cert_info


    def crawl_log_server(self) -> List[LogServer]:

        target = self.session.query(LogServer).\
            filter(LogServer.deactivated == false()).\
            all()

        for server in target:
            start_size = server.last_fetched_entry + 1
            end_size = self.conf.self.crawler.entry_fetch_step

            ctclient = CTclient(server.url,
                                self.conf.self.ctclient.timeout)
            tree_size = ctclient.get_tree_size()            

            if tree_size is not None and end_size > tree_size:
                LOGGER.info("tree_size(%s) is smaller than endsize(%s)" %
                            (tree_size, end_size))
                continue

            ret = ctclient.get_certificates(start_size, end_size)
            last_entry = None

            for cert_info in ret:
                try:
                    self.regist_certificates(server.log_id, cert_info)
                    entry_num = cert_info[-1]
                    if last_entry is None or entry_num > last_entry:
                        last_entry = entry_num
                except Exception as ex:
                    LOGGER.warning("unable to regist certificate")
                    LOGGER.info("%s" % (str(ex)))
                    LOGGER.info("cert info: %s" % str(ret))
                    continue

            if last_entry is not None:
                current_time = datetime.datetime.utcnow()
                server.last_fetched_at = current_time
                server.last_entry = last_entry
                self.session.commit()
            else:
                self.session.rollback()

    def run_application(self):
        pass

    def teardown_application(self):
        pass

    def teardown_resource(self):
        pass


if __name__ == "__main__":
    app = CrawlLogServer()
    LOGGER = app.create_toplevel_logger()
    app.start()
