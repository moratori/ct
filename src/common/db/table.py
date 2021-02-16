#!/usr/bin/env python

import enum

from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy import Column, String, DateTime  # type: ignore
from sqlalchemy import Boolean, BigInteger, Index
from sqlalchemy import ForeignKey, Integer, Enum

Base = declarative_base()


class IdentifierType(enum.Enum):
    ipaddress = 0
    dnsname = 1


class SubjectAltName(Base):  # type: ignore

    """
    SANsを持つ証明書を管理する為のテーブル
    """

    sans_id = Column("sans_id",
                     BigInteger,
                     nullable=False,
                     primary_key=True)

    identifier_ordering = Column("identifier_ordering",
                                 Integer,
                                 nullable=False,
                                 primary_key=True)

    identifier_type = Column("identifier_type",
                             Enum(IdentifierType),
                             nullable=False)

    identifier = Column("identifier",
                        String(256),
                        nullable=False)

    identifier_tld = Column("identifier_tld",
                            String(64),
                            nullable=True)

    identifier_sld = Column("identifier_sld",
                            String(64),
                            nullable=True)

    version = Column(BigInteger,
                     nullable=False)

    __tablename__ = "subject_alt_name"
    __mapper_args__ = {"version_id_col": version}
    __table_args__ = (Index("ix_identifier_tld", "identifier_tld"),
                      Index("ix_identifier_sld", "identifier_sld"))


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
