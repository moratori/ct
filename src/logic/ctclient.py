#!/usr/bin/env python3

import base64
import io
import re
import json as jsn
import urllib.parse
import requests
import cryptography.x509 as crypto
from typing import Optional, Any, List, Tuple, Dict
from logging import getLogger
from cryptography import x509
from cryptography.hazmat.backends import default_backend

LOGGER = getLogger(__name__)


def get_json_from_url(url: str,
                      timeout: int,
                      params: Dict = dict()) -> Optional[Any]:
    try:
        res = requests.get(url, params=params, timeout=timeout)
        content_type = res.headers["content-type"]
        if (res.status_code != 200 or
                (not content_type.startswith("application/json") and
                 not content_type.startswith("text/plain"))):
            LOGGER.error(
                "status code: %s, content type: %s" %
                (str(res.status_code), str(content_type)))
            return None
        return res.json()
    except Exception as ex:
        LOGGER.warning("unable to get json data from %s" % url)
        LOGGER.info("exception occurred: %s" % str(ex))
        return None


def post_json_to_url(url: str,
                     timeout: int,
                     data: str = "") -> Optional[Any]:
    try:
        res = requests.post(url, data=data, timeout=timeout,
                            headers={'content-type': 'application/json'})
        content_type = res.headers["content-type"]
        if (res.status_code != 200 or
                (not content_type.startswith("application/json") and
                 not content_type.startswith("text/plain"))):
            LOGGER.error(
                "status code: %s, content type: %s" %
                (str(res.status_code), str(content_type)))
            return None
        return res.json()
    except Exception as ex:
        LOGGER.warning("unable to get json data from %s" % url)
        LOGGER.info("exception occurred: %s" % str(ex))
        return None


def get_cert_object_from_der(der: bytes) -> crypto.Certificate:
    try:
        cert = x509.load_der_x509_certificate(der, default_backend())
    except Exception as ex:
        LOGGER.debug("unable to parse data using cryptography: %r" % der)
        raise ex
    return cert


class CTclient:

    GET_STH = "ct/v1/get-sth"
    GET_ROOTS = "ct/v1/get-roots"
    GET_ENTRIES = "ct/v1/get-entries"
    ADD_CHAIN = "ct/v1/add-chain"

    def __init__(self, logserver: str, timeout: int) -> None:
        self.logserver = logserver.rstrip("/") + "/"
        self.timeout = timeout

    def _construct_chain_json(self, chainfile: str) -> Optional[str]:
        preamble = "-----BEGIN CERTIFICATE-----"
        postamble = "-----END CERTIFICATE-----"
        pattern = \
            "[\r\n]*%s[\r\n]+[a-zA-Z0-9+/=\r\n ]+[\r\n]+%s[\r\n]*" % (
                preamble,
                postamble)
        try:
            chain_json = []
            with open(chainfile, "r", encoding="ascii") as handle:
                chain = re.findall(pattern, handle.read())
                for pem in chain:
                    chain_json.append(pem.strip().
                                      replace(preamble, "").
                                      replace(postamble, ""))

            return jsn.dumps(dict(chain=chain_json))
        except Exception as ex:
            LOGGER.warning("error occurred while constructing chain: %s" %
                           str(ex))
            return None

    def add_chain(self, chainfile: str) -> Optional[Any]:
        chain_json = self._construct_chain_json(chainfile)
        if chain_json is not None:
            url = urllib.parse.urljoin(self.logserver,
                                       CTclient.ADD_CHAIN)
            ret = post_json_to_url(url, self.timeout, data=chain_json)
            return ret
        return None

    def get_sth(self) -> Optional[Any]:
        url = urllib.parse.urljoin(self.logserver,
                                   CTclient.GET_STH)
        ret = get_json_from_url(url, self.timeout)

        return ret

    def get_tree_size(self) -> Optional[int]:
        ret = self.get_sth()
        if ret is not None:
            try:
                return int(ret["tree_size"])
            except KeyError:
                LOGGER.warning("unable to get tree_size: %s" %
                               str(ret))
        return None

    def get_roots(self) -> List[crypto.Certificate]:
        url = urllib.parse.urljoin(self.logserver,
                                   CTclient.GET_ROOTS)
        ret = get_json_from_url(url, self.timeout)
        result: List[crypto.Certificate] = []
        if ret is None or "certificates" not in ret:
            LOGGER.warning("unable to get root certificates: %s" %
                           (str(ret)))
            return result
        else:
            for root in ret["certificates"]:
                try:
                    cert = get_cert_object_from_der(base64.b64decode(root))
                    result.append(cert)
                except Exception as ex:
                    LOGGER.warning("unable to parse root certificate")
                    LOGGER.info("exception occurred : %s" % str(ex))
                    continue
            return result

    def is_readable_server(self) -> bool:
        succ, failed = self.get_certificates(0, 0)
        return len(succ) + len(failed) > 0

    def is_unreadable_server(self) -> bool:
        succ, failed = self.get_certificates(0, 0)
        return len(succ) + len(failed) <= 0

    def get_certificates(self,
                         startsize: int,
                         endsize: int) -> \
            Tuple[List[Tuple[bool, str, crypto.Certificate, int]],
                  List[Tuple[int, str]]]:

        if startsize > endsize:
            LOGGER.error("startsize must be less than endsize")
            return [], []

        url = urllib.parse.urljoin(self.logserver,
                                   CTclient.GET_ENTRIES)
        params = dict(start=startsize, end=endsize)
        ret = get_json_from_url(url, self.timeout, params=params)

        result: List[Tuple[bool, str, Any, int]] = []
        retry_target: List[Tuple[int, str]] = []

        if ret is not None and ("entries" in ret):
            entries = ret["entries"]
            if entries is None:
                LOGGER.error("maybe range %s~%s is too big" %
                             (startsize, endsize))
                return [], []
            expected_size = (endsize - startsize + 1)
            if len(entries) != expected_size:
                LOGGER.error("num of entries does not match request size")
                LOGGER.info("req : actual = %d : %d" % (expected_size,
                                                        len(entries)))
                return [], []
            for num, entry in enumerate(entries):
                entry_num = num + startsize
                precert_flag, pem, cert = \
                    self.parse_entry_to_certificate(entry)
                if not (precert_flag is None or pem is None or cert is None):
                    result.append((precert_flag, pem, cert, entry_num))
                else:
                    retry_target.append((entry_num, entry))
        else:
            LOGGER.warning("unable to get entries in properly")
            LOGGER.info("return data from log server: %s" % str(ret))
        return result, retry_target

    def _parse_first_found_cert_in_tls_encoded_data(
            self,
            bytes_data: bytes) -> Tuple[bytes, crypto.Certificate]:
        CERT_LENGTH_SIZE = 3
        DER_SEQUENCE_TAG = 48

        while True:
            size = int.from_bytes(bytes_data[0:CERT_LENGTH_SIZE],
                                  "big")
            bytes_data = bytes_data[CERT_LENGTH_SIZE:CERT_LENGTH_SIZE+size]
            if bytes_data[0] == DER_SEQUENCE_TAG:
                data = bytes_data
                break

        cert = get_cert_object_from_der(data)

        return data, cert

    def parse_entry_to_certificate(
            self,
            entry: Dict) -> Tuple[Optional[bool],
                                  Optional[str],
                                  Optional[crypto.Certificate]]:
        X509_ENTRY = 0
        PRECERT_ENTRY = 1

        precert_flag = pem = cert = None

        try:

            leaf_input = base64.b64decode(entry["leaf_input"])
            extra_data = base64.b64decode(entry["extra_data"])

            with io.BytesIO(leaf_input) as handle:
                int.from_bytes(handle.read(1), "big")  # version
                int.from_bytes(handle.read(1), "big")  # mercle_leaf_type
                int.from_bytes(handle.read(8), "big")  # timestamp
                log_entry_type = int.from_bytes(handle.read(2), "big")
                rest_of_data = handle.read()

                if log_entry_type == PRECERT_ENTRY:
                    precert_flag = True
                    target_data = extra_data
                elif log_entry_type == X509_ENTRY:
                    precert_flag = False
                    target_data = rest_of_data
                else:
                    precert_flag = False
                    target_data = b''
                    LOGGER.warning("unknown log_entry_type: %s" %
                                   str(log_entry_type))

                rawdata, cert = \
                    self._parse_first_found_cert_in_tls_encoded_data(
                        target_data)

                pem = base64.b64encode(rawdata).decode("ascii")

        except Exception as ex:
            LOGGER.warning("except occurred while parsing cert: %s" % str(ex))
            LOGGER.info("unable to get certificate from entry")
            LOGGER.info("%s" % str(entry))

        return precert_flag, pem, cert
