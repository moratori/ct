#!/usr/bin/env python3

from sqlalchemy import Column, String, BigInteger, DateTime, Boolean, Integer
from common.data.db.base import BaseTable
from logic.ctclient import CTclient


class LogServer(BaseTable):  # type: ignore

    log_id = Column("log_id",
                    String(128),
                    nullable=False,
                    primary_key=True)

    operator = Column("operator",
                      String(256),
                      nullable=False)

    description = Column("description",
                         String(512),
                         nullable=False)

    url = Column("url",
                 String(1024),
                 nullable=False)

    last_fetched_entry = Column("last_fetched_entry",
                                BigInteger,
                                nullable=False,
                                default=-1)

    last_fetched_at = Column("last_fetched_at",
                             DateTime(),
                             nullable=True)

    access_failed_cnt = Column("access_failed_cnt",
                               Integer,
                               nullable=False,
                               default=0)

    deactivated = Column("deactivated",
                         Boolean,
                         nullable=False,
                         default=False)

    version = Column(BigInteger,
                     nullable=False)

    __tablename__ = "log_server"
    __mapper_args__ = {'version_id_col': version}

    def is_readable(self, timeout: int) -> bool:
        client = CTclient(self.url, timeout)
        return client.is_readable_server()
