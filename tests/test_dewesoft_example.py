# Prepare python to use GRPC interface:
# python -m grpc_tools.protoc --proto_path=proto_src --pyi_out=. --python_out=. --grpc_python_out=. ods.proto ods_external_data.proto
import unittest
import pathlib
import logging
import sys
import os

import dwdatareader as dw

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")


# pylint: disable=E1101


class TestDewesoftExample(unittest.TestCase):
    log = logging.getLogger(__name__)

    def test_lib(self):
        example_file = pathlib.Path.joinpath(pathlib.Path(
            __file__).parent.resolve(), "../data", "data_01.dxd")
        # example_file = pathlib.Path.joinpath(pathlib.Path(
        #     __file__).parent.resolve(), "../data", "Example_Drive01.d7d")
        print("File: " + str(example_file))
        if not os.path.exists(example_file):
            print(" File does not exist: " + str(example_file))
        with dw.open(str(example_file)) as f:
            print(f.info)
            number_of_channels = len(f.channels)
            print("Number of Channels: " + str(number_of_channels))
            self.assertEqual(number_of_channels, 90)
            ch: dw.DWChannel
            for ch in f.channels:
                print("Channel Name:" + ch.name)
                print(ch)

            # print(f['GPSvel'])
            # ch1 = f['GPSvel'].series()
            # print(ch1.dtype)
            # print(ch1.name)
            # print(len(ch1))
            # print(ch1.shape)
            # print(ch1[0])  # der Wert
            # print(ch1)

        #  for ch in f.values():
        #    print(ch.name, ch.series().mean())


if __name__ == "__main__":
    unittest.main()
