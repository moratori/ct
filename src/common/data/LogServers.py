#!/usr/bin/env python

from logging import getLogger
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

LOGGER = getLogger(__name__)
Base = declarative_base()


class LogServer(Base):

    __tablename__ = "log_server"

    log_id = Column("log_id",
                    String(128),
                    nullable=False,
                    primary_key=True)

    operator = Column("operator_name",
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
