# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: remote.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'remote.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import types_pb2 as types__pb2
from .gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cremote.proto\x12\nprometheus\x1a\x0btypes.proto\x1a\x14gogoproto/gogo.proto\"z\n\x0cWriteRequest\x12\x30\n\ntimeseries\x18\x01 \x03(\x0b\x32\x16.prometheus.TimeSeriesB\x04\xc8\xde\x1f\x00\x12\x32\n\x08metadata\x18\x03 \x03(\x0b\x32\x1a.prometheus.MetricMetadataB\x04\xc8\xde\x1f\x00J\x04\x08\x02\x10\x03\"\xae\x01\n\x0bReadRequest\x12\"\n\x07queries\x18\x01 \x03(\x0b\x32\x11.prometheus.Query\x12\x45\n\x17\x61\x63\x63\x65pted_response_types\x18\x02 \x03(\x0e\x32$.prometheus.ReadRequest.ResponseType\"4\n\x0cResponseType\x12\x0b\n\x07SAMPLES\x10\x00\x12\x17\n\x13STREAMED_XOR_CHUNKS\x10\x01\"8\n\x0cReadResponse\x12(\n\x07results\x18\x01 \x03(\x0b\x32\x17.prometheus.QueryResult\"\x8f\x01\n\x05Query\x12\x1a\n\x12start_timestamp_ms\x18\x01 \x01(\x03\x12\x18\n\x10\x65nd_timestamp_ms\x18\x02 \x01(\x03\x12*\n\x08matchers\x18\x03 \x03(\x0b\x32\x18.prometheus.LabelMatcher\x12$\n\x05hints\x18\x04 \x01(\x0b\x32\x15.prometheus.ReadHints\"9\n\x0bQueryResult\x12*\n\ntimeseries\x18\x01 \x03(\x0b\x32\x16.prometheus.TimeSeries\"]\n\x13\x43hunkedReadResponse\x12\x31\n\x0e\x63hunked_series\x18\x01 \x03(\x0b\x32\x19.prometheus.ChunkedSeries\x12\x13\n\x0bquery_index\x18\x02 \x01(\x03\x42\x08Z\x06prompbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'remote_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\006prompb'
  _globals['_WRITEREQUEST'].fields_by_name['timeseries']._loaded_options = None
  _globals['_WRITEREQUEST'].fields_by_name['timeseries']._serialized_options = b'\310\336\037\000'
  _globals['_WRITEREQUEST'].fields_by_name['metadata']._loaded_options = None
  _globals['_WRITEREQUEST'].fields_by_name['metadata']._serialized_options = b'\310\336\037\000'
  _globals['_WRITEREQUEST']._serialized_start=63
  _globals['_WRITEREQUEST']._serialized_end=185
  _globals['_READREQUEST']._serialized_start=188
  _globals['_READREQUEST']._serialized_end=362
  _globals['_READREQUEST_RESPONSETYPE']._serialized_start=310
  _globals['_READREQUEST_RESPONSETYPE']._serialized_end=362
  _globals['_READRESPONSE']._serialized_start=364
  _globals['_READRESPONSE']._serialized_end=420
  _globals['_QUERY']._serialized_start=423
  _globals['_QUERY']._serialized_end=566
  _globals['_QUERYRESULT']._serialized_start=568
  _globals['_QUERYRESULT']._serialized_end=625
  _globals['_CHUNKEDREADRESPONSE']._serialized_start=627
  _globals['_CHUNKEDREADRESPONSE']._serialized_end=720
# @@protoc_insertion_point(module_scope)
