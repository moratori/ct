#!/usr/bin/env python

from logging import getLogger
from sqlalchemy import Column, String
from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from common.data.logserver import LogServer

LOGGER = getLogger(__name__)
Base = declarative_base()


class LogEntry(Base):  # type: ignore

    log_id = Column("log_id",
                    String(128),
                    ForeignKey(LogServer.log_id),
                    nullable=False,
                    primary_key=True)

    entry_num = Column("entry_num",
                       BigInteger,
                       nullable=False,
                       primary_key=True)

    # Certificateテーブルにforeignkeyをはる事はできない
    # Certificateテーブルのfp_sha256だけではprimary-keyにならない為
    fp_sha256 = Column("fp_sha256",
                       String(64),
                       nullable=False)

    version = Column(BigInteger,
                     nullable=False)

    __tablename__ = "log_entry"
    __mapper_args__ = {'version_id_col': version}
