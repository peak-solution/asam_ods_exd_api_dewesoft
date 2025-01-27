# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import ods_external_data_pb2 as ods__external__data__pb2

GRPC_GENERATED_VERSION = '1.66.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in ods_external_data_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ExternalDataReaderStub(object):
    """
    EXD-API RPC service definition
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Open = channel.unary_unary(
                '/ods.external_data.ExternalDataReader/Open',
                request_serializer=ods__external__data__pb2.Identifier.SerializeToString,
                response_deserializer=ods__external__data__pb2.Handle.FromString,
                _registered_method=True)
        self.GetStructure = channel.unary_unary(
                '/ods.external_data.ExternalDataReader/GetStructure',
                request_serializer=ods__external__data__pb2.StructureRequest.SerializeToString,
                response_deserializer=ods__external__data__pb2.StructureResult.FromString,
                _registered_method=True)
        self.GetValues = channel.unary_unary(
                '/ods.external_data.ExternalDataReader/GetValues',
                request_serializer=ods__external__data__pb2.ValuesRequest.SerializeToString,
                response_deserializer=ods__external__data__pb2.ValuesResult.FromString,
                _registered_method=True)
        self.GetValuesEx = channel.unary_unary(
                '/ods.external_data.ExternalDataReader/GetValuesEx',
                request_serializer=ods__external__data__pb2.ValuesExRequest.SerializeToString,
                response_deserializer=ods__external__data__pb2.ValuesExResult.FromString,
                _registered_method=True)
        self.Close = channel.unary_unary(
                '/ods.external_data.ExternalDataReader/Close',
                request_serializer=ods__external__data__pb2.Handle.SerializeToString,
                response_deserializer=ods__external__data__pb2.Empty.FromString,
                _registered_method=True)


class ExternalDataReaderServicer(object):
    """
    EXD-API RPC service definition
    """

    def Open(self, request, context):
        """
        'OpenExternalData' opens the external data and will return a handle for further requests.
        The external data provider will keep the resource open addressed by the handle until the
        'Close' request.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStructure(self, request, context):
        """
        'GetStructure' method will allow to retrieve information about the structure of the external data.
        This method is used by an import processor to create measurements, submatrices and localcolumns
        accordingly in an ASAM ODS database.
        The ASAM ODS server will use this information to retrieve data from the external data provider
        on client request later on.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetValues(self, request, context):
        """
        'GetValues' reads external data via/like ASAM ODS data-read interface.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetValuesEx(self, request, context):
        """
        Reads external data like ASAM ODS valuematrix-read in submatrix mode.
        With this method the channel names and/or data can be retrieved.
        Channels are addressed using pattern matching their names 
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Close(self, request, context):
        """
        Close external data to free resources.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ExternalDataReaderServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Open': grpc.unary_unary_rpc_method_handler(
                    servicer.Open,
                    request_deserializer=ods__external__data__pb2.Identifier.FromString,
                    response_serializer=ods__external__data__pb2.Handle.SerializeToString,
            ),
            'GetStructure': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStructure,
                    request_deserializer=ods__external__data__pb2.StructureRequest.FromString,
                    response_serializer=ods__external__data__pb2.StructureResult.SerializeToString,
            ),
            'GetValues': grpc.unary_unary_rpc_method_handler(
                    servicer.GetValues,
                    request_deserializer=ods__external__data__pb2.ValuesRequest.FromString,
                    response_serializer=ods__external__data__pb2.ValuesResult.SerializeToString,
            ),
            'GetValuesEx': grpc.unary_unary_rpc_method_handler(
                    servicer.GetValuesEx,
                    request_deserializer=ods__external__data__pb2.ValuesExRequest.FromString,
                    response_serializer=ods__external__data__pb2.ValuesExResult.SerializeToString,
            ),
            'Close': grpc.unary_unary_rpc_method_handler(
                    servicer.Close,
                    request_deserializer=ods__external__data__pb2.Handle.FromString,
                    response_serializer=ods__external__data__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ods.external_data.ExternalDataReader', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ods.external_data.ExternalDataReader', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ExternalDataReader(object):
    """
    EXD-API RPC service definition
    """

    @staticmethod
    def Open(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ods.external_data.ExternalDataReader/Open',
            ods__external__data__pb2.Identifier.SerializeToString,
            ods__external__data__pb2.Handle.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetStructure(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ods.external_data.ExternalDataReader/GetStructure',
            ods__external__data__pb2.StructureRequest.SerializeToString,
            ods__external__data__pb2.StructureResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetValues(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ods.external_data.ExternalDataReader/GetValues',
            ods__external__data__pb2.ValuesRequest.SerializeToString,
            ods__external__data__pb2.ValuesResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetValuesEx(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ods.external_data.ExternalDataReader/GetValuesEx',
            ods__external__data__pb2.ValuesExRequest.SerializeToString,
            ods__external__data__pb2.ValuesExResult.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Close(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ods.external_data.ExternalDataReader/Close',
            ods__external__data__pb2.Handle.SerializeToString,
            ods__external__data__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
