"""
ASAM ODS EXD API implementation for Dewesoft data files (*.d7d, *.d7z or *.dxd)

Notes:
  - requires Dewesoft DWDataReaderLib.dll 4.0.0.0 or later
  - tested with Python 3.4
"""

import os
import logging
from pathlib import Path
import threading
from urllib.parse import urlparse, unquote
from urllib.request import url2pathname

import dwdatareader as dw

import grpc

# pylint: disable=E1101
import ods_pb2 as ods
import ods_external_data_pb2 as exd_api
import ods_external_data_pb2_grpc


def dw_get_structure(dw_file: dw.DWFile) -> dict:
    group_dict = {}
    channel_dict = {}
    chn_number_in_grp = 0
    grp_number = 0
    for ch in dw_file.channels:
        channel_index = ch.channel_index
        try:
            ch_series = ch.series()
        except dw.DWError as e:
            # skip ASYNC channels e.g. CAN
            logging.warning("Channel '%s' is ignored: %s",
                            ch.name if ch is not None else "unknown", e)
            continue

        chn_length = len(ch_series)
        group_info = channel_index.split(';')

        # the same group name could have channels with different length! Create a unique group name
        group_name = group_info[0] + ':' + str(chn_length)

        if group_name in group_dict:
            channel_dict = group_dict[group_name]["channel_dict"]
            # when the group name was found, the index of the next channel is calculated with the existing channels dict
            chn_number_in_grp = len(channel_dict)
        else:
            # New Group
            chn_number_in_grp = 0
            channel_dict = {}
            # the first channel in the group is the Ods-Independent-Channel
            group_dict[group_name] = {"channel_dict": channel_dict,
                                      "group_number": grp_number,
                                      "indep_channel": chn_number_in_grp}
            channel_dict[chn_number_in_grp] = {"name": "Index",
                                               "type": 0,
                                               "datatype": ods.DataTypeEnum.DT_DOUBLE,
                                               "length": chn_length,
                                               "description": "Independent",
                                               "long_name": "Independent",
                                               "unit": " ",
                                               "independent": 1}
            grp_number = grp_number + 1
            # next channel is the data of the first dw-channel
            chn_number_in_grp = chn_number_in_grp + 1

        data_type = ods.DataTypeEnum.DT_DOUBLE
        channel_dict[chn_number_in_grp] = {"name": ch.name,
                                           "type": ch.channel_type,
                                           "datatype": data_type,
                                           "length": chn_length,
                                           "description": ch.description,
                                           "long_name": ch.long_name,
                                           "unit": ch.unit,
                                           "independent": 0}

    return group_dict


class ExternalDataReader(ods_external_data_pb2_grpc.ExternalDataReader):
    """
    This class implements the ASAM ODS EXD API to read dewesoft d7d files.
    """

    def Open(self, identifier: exd_api.Identifier, context: grpc.ServicerContext) -> exd_api.Handle:
        """
        Signals an open access to an resource. The server will call `close`later on.

        :param exd_api.Identifier identifier: Contains parameters and file url
        :param dict context: Additional parameters from grpc
        :raises ValueError: If file does not exist
        :return exd_api.Handle: Handle to the opened file.
        """
        with self.lock:
            file_path = Path(self.__get_path(identifier.url))
            if not file_path.is_file():
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"File '{
                        identifier.url}' not found.",
                )

            connection_id = self.__open_dwfile(identifier)

            rv = exd_api.Handle(uuid=connection_id)
            return rv

    def Close(self, handle: exd_api.Handle, context: grpc.ServicerContext) -> exd_api.Empty:
        """
        Close resource opened before and signal the plugin that it is no longer used.

        :param exd_api.Handle handle: Handle to a resource returned before.
        :param context: Additional parameters from grpc.
        :return exd_api.Empty: Empty object.
        """
        with self.lock:
            self.__close_dwfile(handle)
            return exd_api.Empty()

    def GetStructure(self, structure_request: exd_api.StructureRequest, context: grpc.ServicerContext) -> exd_api.StructureResult:
        """
        Get the structure of the file returned as file-group-channel hierarchy.

        :param exd_api.StructureRequest structure_request: Defines what to extract from the file structure.
        :param dict context: Additional parameters from grpc.
        :raises NotImplementedError: If advanced features are requested.
        :return exd_api.StructureResult: The structure of the opened file.
        """
        with self.lock:
            if (
                structure_request.suppress_channels
                or structure_request.suppress_attributes
                or 0 != len(structure_request.channel_names)
            ):
                context.abort(
                    grpc.StatusCode.UNIMPLEMENTED, "Method not implemented!",
                )

            identifier = self.connection_map[structure_request.handle.uuid]
            dw_file_handle = self.__get_dw_file(structure_request.handle)
            dw_group_dict = dw_get_structure(dw_file_handle)

            rv = exd_api.StructureResult(identifier=identifier)
            rv.name = Path(identifier.url).name
            dw_info = dw_file_handle.info
            rv.attributes.variables["start_time"].string_array.values.append(
                dw_info.start_store_time.strftime("%Y%m%d%H%M%S%f"))
            rv.attributes.variables["duration"].double_array.values.append(
                dw_info.duration)
            rv.attributes.variables["sample_rate"].double_array.values.append(
                dw_info.sample_rate)
            dw_groups = []
            for key, value in dw_group_dict.items():
                dw_groups.append(key)
                new_group = exd_api.StructureResult.Group()
                new_group.name = key
                new_group.id = value["group_number"]
                ch_dict = value["channel_dict"]
                new_group.total_number_of_channels = len(ch_dict)
                new_group.number_of_rows = ch_dict[0]["length"]

                for ch_index in ch_dict:
                    new_channel = exd_api.StructureResult.Channel()
                    new_channel.name = ch_dict[ch_index]["long_name"]
                    new_channel.id = ch_index
                    new_channel.data_type = ch_dict[ch_index]["datatype"]
                    new_channel.unit_string = ch_dict[ch_index]["unit"]
                    channel_comment = ch_dict[ch_index]["description"]
                    # added attributes
                    if channel_comment is not None and "" != channel_comment:
                        new_channel.attributes.variables["description"].string_array.values.append(
                            channel_comment)
                    new_channel.attributes.variables["independent"].long_array.values.append(
                        ch_dict[ch_index]["independent"])
                    new_group.channels.append(new_channel)

                rv.groups.append(new_group)
            return rv

    def GetValues(self, values_request: exd_api.ValuesRequest, context: grpc.ServicerContext) -> exd_api.ValuesResult:
        """
        Retrieve channel/signal data identified by `values_request`.

        :param exd_api.ValuesRequest values_request: Defines the group and its channels to be retrieved.
        :param dict context: Additional grpc parameters.
        :raises NotImplementedError: If unknown data type is accessed.
        :return exd_api.ValuesResult: The chunk of bulk data.
        """
        with self.lock:
            dw_file = self.__get_dw_file(values_request.handle)

            # (1) get the structure create for the get_structure()
            dw_structure = dw_get_structure(dw_file)
            dw_group_index_dict = {}
            # (2) reorganize the data to be able to address the groups by index
            for key, source in dw_structure.items():
                group_no = source["group_number"]
                dw_group_index_dict[group_no] = {
                    "channel_dict": source["channel_dict"],
                    "group_name": key,
                    "indep_channel": source["indep_channel"]
                }

            if values_request.group_id < 0 or values_request.group_id >= len(dw_group_index_dict):
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Invalid group id {
                        values_request.group_id}!",
                )

            dw_group = dw_group_index_dict[values_request.group_id]

            nr_of_rows = dw_group["channel_dict"][0]["length"]

            if values_request.start > nr_of_rows or values_request.start < 0:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, f"Channel start index {
                        values_request.start} out of range!",
                )

            end_index = values_request.start + values_request.limit
            if end_index >= nr_of_rows:
                end_index = nr_of_rows

            if len(values_request.channel_ids) == 0:
                # empty id array means all channels of the group
                for ch in dw_group["channel_dict"]:
                    values_request.channel_ids.append(ch)

            for channel_id in values_request.channel_ids:
                if channel_id < 0 or channel_id >= len(dw_group["channel_dict"]):
                    context.abort(
                        grpc.StatusCode.INVALID_ARGUMENT, f"Invalid channel id {
                            channel_id}!",
                    )

            rv = exd_api.ValuesResult(id=values_request.group_id)
            for signal_index in values_request.channel_ids:
                channel = dw_group["channel_dict"][signal_index]
                chn_section = None
                if signal_index == 0:
                    channel_next = dw_group["channel_dict"][1]
                    # this is the index channel, e.g. time
                    chn_section = dw_file[channel_next['name']].series().index
                    channel_datatype = channel["datatype"]
                else:
                    chn_section = dw_file[channel['name']].series().values
                    channel_datatype = channel["datatype"]

                # restrict the number of data per channel like requested
                section = chn_section[values_request.start: end_index]

                new_channel_values = exd_api.ValuesResult.ChannelValues()
                new_channel_values.id = signal_index
                new_channel_values.values.data_type = channel_datatype

                self.__assign_channel_values(
                    channel_datatype, section, new_channel_values)

                rv.channels.append(new_channel_values)

            return rv

    def __assign_channel_values(self, channel_datatype, section, new_channel_values):
        if channel_datatype == ods.DataTypeEnum.DT_BOOLEAN:
            new_channel_values.values.boolean_array.values.extend(section)
        elif channel_datatype == ods.DataTypeEnum.DT_BYTE:
            new_channel_values.values.byte_array.values = section.tobytes()
        elif channel_datatype == ods.DataTypeEnum.DT_SHORT:
            new_channel_values.values.long_array.values[:] = section
        elif channel_datatype == ods.DataTypeEnum.DT_LONG:
            new_channel_values.values.long_array.values[:] = section
        elif channel_datatype == ods.DataTypeEnum.DT_LONGLONG:
            new_channel_values.values.longlong_array.values[:] = section
        elif channel_datatype == ods.DataTypeEnum.DT_FLOAT:
            new_channel_values.values.float_array.values[:] = section
        elif channel_datatype == ods.DataTypeEnum.DT_DOUBLE:
            new_channel_values.values.double_array.values[:] = section
        elif channel_datatype == ods.DataTypeEnum.DT_COMPLEX:
            real_values = []
            for complex_value in section:
                real_values.append(complex_value.real)
                real_values.append(complex_value.imag)
            new_channel_values.values.float_array.values[:] = real_values
        elif channel_datatype == ods.DataTypeEnum.DT_DCOMPLEX:
            real_values = []
            for complex_value in section:
                real_values.append(complex_value.real)
                real_values.append(complex_value.imag)
            new_channel_values.values.double_array.values[:] = real_values
        elif channel_datatype == ods.DataTypeEnum.DT_STRING:
            new_channel_values.values.string_array.values[:] = section
        elif channel_datatype == ods.DataTypeEnum.DT_BYTESTR:
            for item in section:
                new_channel_values.values.bytestr_array.values.append(
                    item.tobytes())
        else:
            raise NotImplementedError(
                f"Unknown np datatype {section.dtype} for type {
                    channel_datatype} not supported!"
            )

    def GetValuesEx(self, request: exd_api.ValuesExRequest, context: grpc.ServicerContext) -> exd_api.ValuesExResult:
        """
        Method to access virtual groups and channels. Currently not supported by the plugin

        :param exd_api.ValuesExRequest request: Defines virtual groups and channels to be accessed.
        :param dict context: Additional grpc parameters.
        :raises NotImplementedError: Currently not implemented. Only needed for very advanced use.
        :return exd_api.ValuesExResult: Bulk values requested.
        """
        context.abort(
            grpc.StatusCode.UNIMPLEMENTED, "Method not implemented!",
        )

    def __init__(self):
        self.connect_count = 0
        self.connection_map = {}
        self.file_map = {}
        self.lock = threading.RLock()

    def __get_id(self, identifier):
        self.connect_count = self.connect_count + 1
        rv = str(self.connect_count)
        self.connection_map[rv] = identifier
        return rv

    def __uri_to_path(self, uri):
        parsed = urlparse(uri)
        host = f"{os.path.sep}{os.path.sep}{parsed.netloc}{os.path.sep}"
        return os.path.normpath(os.path.join(host, url2pathname(unquote(parsed.path))))

    def __get_path(self, file_url) -> str:
        final_path = self.__uri_to_path(file_url)
        return final_path

    def __open_dwfile(self, identifier: exd_api.Identifier) -> str:
        with self.lock:
            connection_id = self.__get_id(identifier)
            connection_url = self.__get_path(identifier.url)
            if connection_url not in self.file_map:
                self.file_map[connection_url] = {
                    "dw_file": dw.open(connection_url), "ref_count": 0}
            self.file_map[connection_url]["ref_count"] = self.file_map[connection_url]["ref_count"] + 1
            return connection_id

    def __get_dw_file(self, handle: exd_api.Handle) -> dw.DWFile:
        with self.lock:
            identifier = self.connection_map[handle.uuid]
            connection_url = self.__get_path(identifier.url)
            rv: dw.DWFile = self.file_map[connection_url]["dw_file"]
            rv.activate()
            return rv

    def __close_dwfile(self, handle: exd_api.Handle):
        with self.lock:
            identifier = self.connection_map[handle.uuid]
            connection_url = self.__get_path(identifier.url)
            if self.file_map[connection_url]["ref_count"] > 1:
                self.file_map[connection_url]["ref_count"] = self.file_map[connection_url]["ref_count"] - 1
            else:
                self.file_map[connection_url]["dw_file"].close()
                del self.file_map[connection_url]
