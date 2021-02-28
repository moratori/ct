#!/usr/bin/env python3

from sqlalchemy import Column, String, BigInteger, ForeignKey
from common.data.db.base import BaseTable
from common.data.db.LogServer import LogServer


class LogEntry(BaseTable):  # type: ignore

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
