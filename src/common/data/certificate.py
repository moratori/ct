#!/usr/bin/env python

from logging import getLogger
from sqlalchemy import Column, String, DateTime
from sqlalchemy import Boolean
from sqlalchemy import BigInteger
from sqlalchemy import Index
from sqlalchemy.ext.declarative import declarative_base

LOGGER = getLogger(__name__)
Base = declarative_base()


class Certificate(Base):  # type: ignore

    fp_sha256 = Column("fp_sha256",
                       String(64),
                       nullable=False,
                       primary_key=True)

    fp_sha1 = Column("fp_sha1",
                     String(40),
                     nullable=False)

    is_precert = Column("is_precert",
                        Boolean,
                        nullable=False)

    is_root = Column("is_root",
                     Boolean,
                     nullable=False)

    serial_number = Column("serial_number",
                           String(256),
                           nullable=False)

    issuer = Column("issuer",
                    String(512),
                    nullable=False)

    subject = Column("subject",
                     String(512),
                     nullable=False)

    not_before = Column("not_before",
                        DateTime,
                        nullable=False)

    not_after = Column("not_after",
                       DateTime,
                       nullable=False)

    cert_data = Column("cert_data",
                       String(8192),
                       nullable=False)

    # パーテンションにする為には、primaryにする必要がある
    sans_id = Column("sans_id",
                     BigInteger,
                     primary_key=True,
                     nullable=False)

    version = Column(BigInteger,
                     nullable=False)

    __tablename__ = "certificate"
    __mapper_args__ = {"version_id_col": version}
    __table_args__ = (Index("ix_sans_id", "sans_id"),
                      Index("ix_issuer", "issuer"),
                      {"mysql_partition_by": "HASH( sans_id )",
                       "mysql_partitions": "100"})
