#!/usr/bin/env python3

import enum
from sqlalchemy import Column, String, BigInteger, Integer, Enum, Index
from common.data.db.base import BaseTable


class IdentifierType(enum.Enum):
    ipaddress = 0
    dnsname = 1


class SubjectAltName(BaseTable):  # type: ignore

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
