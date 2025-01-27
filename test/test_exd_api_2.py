# Prepare python to use GRPC interface:
# python -m grpc_tools.protoc --proto_path=proto_src --pyi_out=. --python_out=. --grpc_python_out=. ods.proto ods_external_data.proto
import logging
import pathlib
import unittest

from google.protobuf.json_format import MessageToJson
import grpc

import ods_external_data_pb2 as oed
import ods_pb2 as ods
from external_data_reader import ExternalDataReader
from test.mock_servicer_context import MockServicerContext

# pylint: disable=E1101


class TestExdApi(unittest.TestCase):
    log = logging.getLogger(__name__)

    def setUp(self):
        self.service = ExternalDataReader()
        self.mock_context = MockServicerContext()

    def _get_example_file_path(self, file_name):
        example_file_path = pathlib.Path.joinpath(pathlib.Path(
            __file__).parent.resolve(), "..", "data", file_name)
        return pathlib.Path(example_file_path).absolute().as_uri()

    def test_open(self):
        service = ExternalDataReader()
        handle = service.Open(oed.Identifier(
            url=self._get_example_file_path("data_02.dxd"), parameters=""), None)
        try:
            pass
        finally:
            service.Close(handle, None)

    def test_structure(self):
        service = ExternalDataReader()
        handle = service.Open(oed.Identifier(
            url=self._get_example_file_path("data_02.dxd"), parameters=""), None)
        try:
            structure = service.GetStructure(
                oed.StructureRequest(handle=handle), None)
            self.assertEqual(structure.name, "data_02.dxd")
            self.assertEqual(len(structure.groups), 5)
            self.assertEqual(structure.groups[0].number_of_rows, 30000)
            self.assertEqual(len(structure.groups[0].channels), 8)
            self.assertEqual(structure.groups[0].id, 0)
            self.log.info(MessageToJson(structure))
            self.assertEqual(structure.groups[0].channels[0].id, 0)
            self.assertEqual(structure.groups[0].channels[0].unit_string, " ")
            self.assertEqual(
                structure.groups[0].channels[0].name, "Independent")
        finally:
            service.Close(handle, None)

    def test_get_values(self):
        service = ExternalDataReader()
        handle = service.Open(oed.Identifier(
            url=self._get_example_file_path("data_02.dxd"), parameters=""), None)
        try:
            values = service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=0, channel_ids=[
                                  0, 1, 2, 3], start=0, limit=4), None
            )
            self.assertEqual(values.id, 0)
            self.assertEqual(len(values.channels), 4)
            self.assertEqual(values.channels[0].id, 0)
            self.assertEqual(values.channels[1].id, 1)
            self.log.info(MessageToJson(values))

            self.assertEqual(
                values.channels[0].values.data_type, ods.DataTypeEnum.DT_DOUBLE)

            self.assertSequenceEqual(
                values.channels[0].values.double_array.values, [
                    1230.0, 1230.002, 1230.004, 1230.006]
            )

            self.assertEqual(
                values.channels[1].values.data_type, ods.DataTypeEnum.DT_DOUBLE)
            self.assertSequenceEqual(
                values.channels[1].values.double_array.values,
                [4958.624243736267, 4958.677291870117,
                    4958.699345588684, 4958.67908000946],
            )

        finally:
            service.Close(handle, None)

    def test_open_non_existing_file(self):
        identifier = oed.Identifier(
            url="file:///non_existing_file.dxd", parameters="")
        with self.assertRaises(grpc.RpcError) as _:
            self.service.Open(identifier, self.mock_context)

        self.assertEqual(self.mock_context.code(), grpc.StatusCode.NOT_FOUND)

    def test_GetValues_param_errors(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path("data_01.dxd"), parameters=""), None)
        # try:

        # Group index negative
        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValues(
                oed.ValuesExRequest(handle=handle, group_id=-12, channel_names=[
                    '2', '3'], start=0, limit=4), self.mock_context
            )

        # Start index negative
        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValues(
                oed.ValuesExRequest(handle=handle, group_id=1, channel_names=[
                    '1', '2'], start=-12, limit=4), self.mock_context
            )

        self.service.Close(handle, None)

    def test_non_existing_GetValuesEx(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path("data_01.dxd"), parameters=""), None)
        # try:

        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValuesEx(
                oed.ValuesExRequest(handle=handle, group_id=1, channel_names=[
                    '2', '3'], start=0, limit=4), self.mock_context
            )

        self.service.Close(handle, None)
