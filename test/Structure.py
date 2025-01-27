import dwdatareader as dw
import os
import pathlib

# **********************************************************

example_file = pathlib.Path.absolute(pathlib.Path(r"./data/data_01.dxd"))
if not os.path.exists(example_file):
    raise ValueError(" File does not exist: " + str(example_file))


my_file = dw.open(str(example_file))

info = my_file.info

store_time = info.start_store_time
sample_rate = info.sample_rate
duration = info.duration

print(f'StartTime  :{store_time}')
print(f'samplerate :{sample_rate}')
print(f'duration   :{duration}')

number_of_channels = len(my_file.channels)
print(f'Number of Channels: {number_of_channels}')

group_dict = {}
channel_dict = {}

chn_number_in_grp = 0
grp_number = 0
for ch in my_file.channels:
    ch_series = ch.series()
    chn_length = len(ch_series)
    channel_index = ch.channel_index
    group_info = channel_index.split(';')
    group_name = group_info[0]
    if group_name in group_dict:
        channel_dict = group_dict[group_name]["channel_dict"]
        chn_number_in_grp = chn_number_in_grp+1
    else:
        # New Group
        chn_number_in_grp = 0
        channel_dict = {}
        # Independent Channel
        indep_channel = ch_series.index
        group_dict[group_name] = {"channel_dict": channel_dict,
                                  "group_number": grp_number,
                                  "indep_channel": chn_number_in_grp}
        # print(f"Independent: {indep_channel}")
        channel_dict[chn_number_in_grp] = {"name": "Index",
                                           "type": 0,
                                           "datatype": indep_channel.dtype,
                                           "length": chn_length,
                                           "description": "Independent",
                                           "long_name": "Independent",
                                           "unit": " ",
                                           "number_of_samples": len(indep_channel),
                                           "independent": 1}
        grp_number = grp_number + 1

    data_type = ch_series.dtype
    channel_dict[chn_number_in_grp] = {"name": ch.name,
                                       "type": ch.channel_type,
                                       "datatype": data_type,
                                       "length": chn_length,
                                       "description": ch.description,
                                       "long_name": ch.long_name,
                                       "unit": ch.unit,
                                       "number_of_samples": ch.number_of_samples}
    # print('********************************************')
    # print("  ArrayInfo        :" + str(ch.arrayInfo))
    # print("  ChannelIndex     :" + str(ch.channel_index))
    # print("  ChannelType      :" + str(ch.channel_type))
    # print("  Fields           :" + str(ch._fields_))
    # print("  ChannelDataFrame :" + str(ch.dataframe()))
    # print("  Channel.series   :" + str(ch.series()))

for key, value in group_dict.items():
    print(key)
    if key == 'Math':
        print(f"Group Name: {key}, Group Number: {value["group_number"]}")
        chdict = value["channel_dict"]
        for chindex in chdict:
            print(f"  Channel Index: {chindex}, Name: {chdict[chindex]["name"]}, Long Name: {chdict[chindex]["long_name"]}, Length: {
                  chdict[chindex]["length"]}, Datatype: {chdict[chindex]["datatype"]}, Unit: {chdict[chindex]["unit"]}")
        print('********************************************')
