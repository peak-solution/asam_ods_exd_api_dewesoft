import pathlib
import unittest

from test.mock_servicer_context import MockServicerContext

from external_data_reader import ExternalDataReader

import ods_external_data_pb2 as oed

# pylint: disable=E1101


class AutoCloseHandle:
    def __init__(self, service, identifier):
        self.__service = service
        self.__identifier = identifier
        self.__handle = None

    def __enter__(self):
        self.__handle = self.__service.Open(self.__identifier, None)
        return self

    def handle(self):
        if self.__handle is None:
            raise ValueError("Handle is not open")
        return self.__handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.__handle is not None:
            self.__service.Close(self.__handle, None)
            self.__handle = None


class TestParallelOpen(unittest.TestCase):
    def setUp(self):
        self.service = ExternalDataReader()
        self.mock_context = MockServicerContext()

    def _get_example_file_path(self, file_name):
        example_file_path = pathlib.Path.joinpath(pathlib.Path(
            __file__).parent.resolve(), "..", "data", file_name)
        return pathlib.Path(example_file_path).absolute().as_uri()

    def test_open_one_file_twice_with_auto_close(self):
        file1_path = self._get_example_file_path("data_01.dxd")

        with AutoCloseHandle(self.service, oed.Identifier(url=file1_path, parameters="")) as s1:
            with AutoCloseHandle(self.service, oed.Identifier(url=file1_path, parameters="")) as s2:
                structure2 = self.service.GetStructure(
                    oed.StructureRequest(handle=s2.handle()), None)
                structure1 = self.service.GetStructure(
                    oed.StructureRequest(handle=s1.handle()), None)
                self.assertIsNotNone(structure1)
                self.assertIsNotNone(structure2)
                self.assertEqual(structure1.identifier.url, file1_path)
                self.assertEqual(structure2.identifier.url, file1_path)

    def test_open_two_file_twice_with_auto_close(self):
        file1_path = self._get_example_file_path("data_01.dxd")
        file2_path = self._get_example_file_path("data_02.dxd")

        with AutoCloseHandle(self.service, oed.Identifier(url=file1_path, parameters="")) as s1:
            with AutoCloseHandle(self.service, oed.Identifier(url=file2_path, parameters="")) as s2:
                structure2 = self.service.GetStructure(
                    oed.StructureRequest(handle=s2.handle()), None)
                structure1 = self.service.GetStructure(
                    oed.StructureRequest(handle=s1.handle()), None)
                self.assertIsNotNone(structure1)
                self.assertIsNotNone(structure2)
                self.assertEqual(structure1.identifier.url, file1_path)
                self.assertEqual(structure2.identifier.url, file2_path)

    def test_open_two_file_twice_close_async(self):
        file1_path = self._get_example_file_path("data_01.dxd")
        file2_path = self._get_example_file_path("data_02.dxd")

        with AutoCloseHandle(self.service, oed.Identifier(url=file1_path, parameters="")) as s1:
            with AutoCloseHandle(self.service, oed.Identifier(url=file2_path, parameters="")) as s2:
                structure2 = self.service.GetStructure(
                    oed.StructureRequest(handle=s2.handle()), None)
                s2.close()
                structure1 = self.service.GetStructure(
                    oed.StructureRequest(handle=s1.handle()), None)
                self.assertIsNotNone(structure1)
                self.assertIsNotNone(structure2)
                self.assertEqual(structure1.identifier.url, file1_path)
                self.assertEqual(structure2.identifier.url, file2_path)

    def test_access_values_of_two_files(self):
        file1_path = self._get_example_file_path("data_01.dxd")
        file2_path = self._get_example_file_path("data_02.dxd")

        with AutoCloseHandle(self.service, oed.Identifier(url=file1_path, parameters="")) as s1:
            with AutoCloseHandle(self.service, oed.Identifier(url=file2_path, parameters="")) as s2:
                self.service.GetValues(oed.ValuesRequest(
                    handle=s1.handle(), group_id=0, channel_ids=[0, 1], limit=100), None)
                self.service.GetValues(oed.ValuesRequest(
                    handle=s2.handle(), group_id=0, channel_ids=[0, 1], limit=100), None)
                self.service.GetValues(oed.ValuesRequest(
                    handle=s1.handle(), group_id=1, channel_ids=[0, 1], limit=100), None)
                self.service.GetValues(oed.ValuesRequest(
                    handle=s2.handle(), group_id=1, channel_ids=[0, 1], limit=100), None)

    def test_access_values_of_two_files_async(self):
        file1_path = self._get_example_file_path("data_01.dxd")
        file2_path = self._get_example_file_path("data_02.dxd")

        with AutoCloseHandle(self.service, oed.Identifier(url=file1_path, parameters="")) as s1:
            with AutoCloseHandle(self.service, oed.Identifier(url=file2_path, parameters="")) as s2:
                self.service.GetValues(oed.ValuesRequest(
                    handle=s2.handle(), group_id=0, channel_ids=[0, 1], limit=100), None)
                self.service.GetValues(oed.ValuesRequest(
                    handle=s2.handle(), group_id=1, channel_ids=[0, 1], limit=100), None)
                s2.close()
                self.service.GetValues(oed.ValuesRequest(
                    handle=s1.handle(), group_id=0, channel_ids=[0, 1], limit=100), None)
                self.service.GetValues(oed.ValuesRequest(
                    handle=s1.handle(), group_id=1, channel_ids=[0, 1], limit=100), None)
