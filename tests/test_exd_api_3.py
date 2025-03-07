# Prepare python to use GRPC interface:
# python -m grpc_tools.protoc --proto_path=proto_src --pyi_out=. --python_out=. --grpc_python_out=. ods.proto ods_external_data.proto
import logging
import pathlib
import unittest

from google.protobuf.json_format import MessageToJson

import ods_external_data_pb2 as oed
import ods_pb2 as ods
from external_data_reader import ExternalDataReader
from tests.mock_servicer_context import MockServicerContext
import grpc

# pylint: disable=E1101


class TestExdApi(unittest.TestCase):
    log = logging.getLogger(__name__)

    def setUp(self):
        self.service = ExternalDataReader()
        self.mock_context = MockServicerContext()
        self.file_name = "Example_Drive01.d7d"

    def _get_example_file_path(self, file_name):
        example_file_path = pathlib.Path.joinpath(pathlib.Path(
            __file__).parent.resolve(), "..", "data", file_name)
        return pathlib.Path(example_file_path).absolute().as_uri()

    def test_open(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path(self.file_name), parameters=""), None)
        try:
            pass
        finally:
            self.service.Close(handle, None)

    def test_structure(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path(self.file_name), parameters=""), None)
        try:
            structure = self.service.GetStructure(
                oed.StructureRequest(handle=handle), None)
            self.assertEqual(structure.name, self.file_name)
            self.assertEqual(len(structure.groups), 5)
            self.assertEqual(structure.groups[0].number_of_rows, 9580)
            self.assertEqual(len(structure.groups[0].channels), 2)
            self.assertEqual(structure.groups[0].id, 0)
            self.log.info(MessageToJson(structure))
            self.assertEqual(structure.groups[0].channels[0].id, 0)
            self.assertEqual(structure.groups[0].channels[0].unit_string, " ")
            self.assertEqual(
                structure.groups[0].channels[0].name, "Independent")
        finally:
            self.service.Close(handle, None)

    def test_get_values_grp0(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path(self.file_name), parameters=""), None)
        try:
            values = self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=0, channel_ids=[
                                  0, 1, ], start=0, limit=4), self.mock_context
            )
            self.assertEqual(values.id, 0)
            self.assertEqual(len(values.channels), 2)
            self.assertEqual(values.channels[0].id, 0)
            self.assertEqual(values.channels[1].id, 1)
            self.log.info(MessageToJson(values))

            self.assertEqual(
                values.channels[0].values.data_type, ods.DataTypeEnum.DT_DOUBLE)

            print(values.channels[0].values.string_array.values)

            self.assertSequenceEqual(
                values.channels[0].values.double_array.values, [
                    0.0, 0.01, 0.02, 0.03]
            )
            self.assertEqual(
                values.channels[1].values.data_type, ods.DataTypeEnum.DT_DOUBLE)
            self.assertSequenceEqual(
                values.channels[1].values.double_array.values,
                [89.2578125, 89.263916015625, 89.27001953125, 89.2822265625],
            )

        finally:
            self.service.Close(handle, None)

    def test_get_values_grp1(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path(self.file_name), parameters=""), None)
        try:
            values = self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=1, channel_ids=[
                                  0, 1, ], start=0, limit=4), self.mock_context
            )
            # print('##################################')
            # print(values)
            # print('##################################')
            self.assertEqual(values.id, 1)
            self.assertEqual(len(values.channels), 2)
            self.assertEqual(values.channels[0].id, 0)
            self.assertEqual(values.channels[1].id, 1)
            self.log.info(MessageToJson(values))

            self.assertEqual(
                values.channels[0].values.data_type, ods.DataTypeEnum.DT_DOUBLE)

            self.assertSequenceEqual(
                values.channels[0].values.double_array.values, [
                    0.0, 0.01, 0.02, 0.03]
            )
            self.assertEqual(
                values.channels[1].values.data_type, ods.DataTypeEnum.DT_DOUBLE)
            self.assertSequenceEqual(
                values.channels[1].values.double_array.values, [
                    0.0, 0.0, 0.0, 0.0],
            )

        finally:
            self.service.Close(handle, None)

    def test_get_values_grp2(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path(self.file_name), parameters=""), None)
        try:
            values = self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=2, channel_ids=[
                                  0, 1, ], start=0, limit=888884), self.mock_context
            )
            # print('##################################')
            # print(values)
            # print('##################################')
            self.assertEqual(values.id, 2)
            self.assertEqual(len(values.channels), 2)
            self.assertEqual(values.channels[0].id, 0)
            self.assertEqual(values.channels[1].id, 1)
            self.log.info(MessageToJson(values))

            self.assertEqual(
                values.channels[0].values.data_type, ods.DataTypeEnum.DT_DOUBLE)

            vals = values.channels[0].values.double_array.values
            self.assertEqual(len(vals), 191)

            # self.assertSequenceEqual(
            #     values.channels[0].values.double_array.values, [
            #         0.0001196475641336292, 9.808456525206566e-05, 0.00011884687410201877, 0.00011659514711936936]
            # )
            self.assertEqual(
                values.channels[1].values.data_type, ods.DataTypeEnum.DT_DOUBLE)
            vals = values.channels[1].values.double_array.values
            self.assertEqual(len(vals), 191)

            # self.assertSequenceEqual(
            #     values.channels[1].values.double_array.values, [
            #         16.978660583496094, 2.0636370182037354, 16.424827575683594, 14.867319107055664],
            # )

        finally:
            self.service.Close(handle, None)

    def test_get_values_grp1_all_values(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path(self.file_name), parameters=""), None)
        try:
            values = self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=1,
                                  channel_ids=[], start=0, limit=9999994), self.mock_context
            )
            # print('##################################')
            # print(values)
            # print('##################################')
            self.assertEqual(values.id, 1)
            self.assertEqual(len(values.channels), 2)

            # Channel #0
            ch0_obj = values.channels[0]
            self.assertEqual(ch0_obj.id, 0)
            self.assertEqual(ch0_obj.values.data_type,
                             ods.DataTypeEnum.DT_DOUBLE)

            self.assertEqual(ch0_obj.values.data_type,
                             ods.DataTypeEnum.DT_DOUBLE)

            vals = ch0_obj.values.double_array.values
            self.assertEqual(len(vals), 9580)

            # self.assertSequenceEqual(ch0_obj.values.double_array.values,
            #                          [
            #                              0.0001196475641336292, 9.808456525206566e-05, 0.00011884687410201877, 0.00011659514711936936
            #                          ]
            #                          )

            # Chanel #1
            ch1_obj = values.channels[1]
            self.assertEqual(ch1_obj.id, 1)
            self.assertEqual(ch1_obj.values.data_type,
                             ods.DataTypeEnum.DT_DOUBLE)

            vals = ch1_obj.values.double_array.values
            self.assertEqual(len(vals), 9580)

            self.assertEqual(
                ch1_obj.values.data_type, ods.DataTypeEnum.DT_DOUBLE)
            # self.assertSequenceEqual(
            #     ch1_obj.values.double_array.values, [
            #         16.978660583496094, 2.0636370182037354, 16.424827575683594, 14.867319107055664],
            # )
            self.log.info(MessageToJson(values))

        finally:
            self.service.Close(handle, None)

    def test_open_non_existing_file(self):
        identifier = oed.Identifier(
            url="file:///non_existing_file.dxd", parameters="")
        with self.assertRaises(grpc.RpcError) as _:
            self.service.Open(identifier, self.mock_context)

        self.assertEqual(self.mock_context.code(), grpc.StatusCode.NOT_FOUND)

    def test_GetValues_param_errors(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path(self.file_name), parameters=""), None)
        # try:

        # Group index negative
        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=-12, channel_ids=[
                    2, 3], start=0, limit=4), self.mock_context
            )

        # Group index to big
        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=1212, channel_ids=[
                    2, 3], start=0, limit=4), self.mock_context
            )

        # Start value index negative
        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=1, channel_ids=[
                    1, 2], start=-12, limit=4), self.mock_context
            )

        # Channel ID to big
        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=1, channel_ids=[
                    1212, 2], start=0, limit=4), self.mock_context
            )

        # Channel ID to small
        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValues(
                oed.ValuesRequest(handle=handle, group_id=1, channel_ids=[
                    -12, 2], start=0, limit=4), self.mock_context
            )

        self.service.Close(handle, None)

    def test_non_existing_GetValuesEx(self):
        handle = self.service.Open(oed.Identifier(
            url=self._get_example_file_path(self.file_name), parameters=""), None)
        # try:

        with self.assertRaises(grpc.RpcError) as _:
            self.service.GetValuesEx(
                oed.ValuesExRequest(handle=handle, group_id=1, channel_names=[
                    '2', '3'], start=0, limit=4), self.mock_context
            )

        self.service.Close(handle, None)
