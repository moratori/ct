#!/usr/bin/env python3

from sqlalchemy import Column, String, BigInteger, Boolean, ForeignKey, Text
from common.data.db.base import BaseTable
from common.data.db.LogServer import LogServer


class RetryTarget(BaseTable):  # type: ignore

    log_id = Column("log_id",
                    String(128),
                    ForeignKey(LogServer.log_id),
                    nullable=False,
                    primary_key=True)

    entry_num = Column("entry_num",
                       BigInteger,
                       nullable=False,
                       primary_key=True)

    data = Column("data",
                  Text,
                  nullable=False)

    is_retried = Column("is_retried",
                        Boolean,
                        nullable=False,
                        default=False)

    version = Column(BigInteger,
                     nullable=False)

    __tablename__ = "retry_target"
    __mapper_args__ = {'version_id_col': version}
