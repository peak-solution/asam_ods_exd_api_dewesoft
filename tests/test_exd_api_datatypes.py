import logging
import pathlib
import unittest

from google.protobuf.json_format import MessageToJson

import ods_external_data_pb2 as oed
from external_data_reader import ExternalDataReader

# pylint: disable=E1101


class TestDataTypes(unittest.TestCase):
    log = logging.getLogger(__name__)

    def _get_example_file_path(self, file_name):
        example_file_path = pathlib.Path.joinpath(pathlib.Path(
            __file__).parent.resolve(), "..", "data", file_name)
        return pathlib.Path(example_file_path).absolute().resolve().as_uri()

    def test_unit_and_description(self):
        file_url = self._get_example_file_path(
            "data_01.dxd")

        service = ExternalDataReader()
        handle = service.Open(oed.Identifier(
            url=file_url, parameters=""), None)
        try:
            structure = service.GetStructure(
                oed.StructureRequest(handle=handle), None)
            self.log.info(MessageToJson(structure))

            self.assertEqual(
                structure.name, "data_01.dxd")
            self.assertEqual(len(structure.groups), 6)
            self.assertEqual(structure.groups[0].number_of_rows, 12500)
            self.assertEqual(len(structure.groups[0].channels), 8)
            self.assertEqual(
                1, structure.groups[0].channels[0].attributes.variables["independent"].long_array.values[0])
            self.assertEqual(" ", structure.groups[0].channels[0].unit_string)
            self.assertEqual("mV", structure.groups[0].channels[1].unit_string)
            self.assertEqual("mV", structure.groups[0].channels[2].unit_string)
            self.assertEqual("mV", structure.groups[0].channels[3].unit_string)

            values = service.GetValues(
                oed.ValuesRequest(
                    handle=handle, group_id=0, start=0, limit=4, channel_ids=[0, 1, 2, 3]), None
            )
            self.assertSequenceEqual(
                values.channels[0].values.double_array.values, [1200.02, 1200.022, 1200.024, 1200.026])
            self.assertSequenceEqual(
                values.channels[1].values.double_array.values, [4958.699345588684, 4958.738684654236, 4958.735704421997, 4958.730340003967])
            self.assertSequenceEqual(
                values.channels[2].values.double_array.values, [0.5932962894439697, 0.48637568950653076, 0.5893301963806152, 0.5781638622283936])
            self.assertSequenceEqual(
                values.channels[3].values.double_array.values, [4965.871572494507, 4965.800046920776, 4965.837597846985, 4965.866804122925])
        finally:
            service.Close(handle, None)
