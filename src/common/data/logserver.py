#!/usr/bin/env python

from logging import getLogger
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import Boolean
from sqlalchemy import BigInteger
from sqlalchemy.ext.declarative import declarative_base

LOGGER = getLogger(__name__)
Base = declarative_base()


class LogServer(Base):  # type: ignore

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

    added_at = Column("added_at",
                      DateTime(),
                      nullable=False)

    url = Column("url",
                 String(1024),
                 nullable=False)

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
