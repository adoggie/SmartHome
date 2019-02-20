#coding:utf-8

import os,os.path,sys
sys.path.insert(0,'../src')

from mantis.BlueEarth.vendor.concox.gt03.accumulator import DataAccumulator
from mantis.BlueEarth.vendor.concox.gt03.message import *

data_login_req = '78 78 11 01 07 52 53 36 78 90 02 42 70 00 32 01 00 05 12 79 0D 0A'
data_heartbeat = '78 78 0A 13 40 04 04 00 01 00 0F DC EE 0D 0A'
data_gps_location = '78 78 19 10 10 01 0E 0F 39 2B C8 02 7A C7 34 0C 46 59 40 00 15 0F 00 01 01 8D 98 CA 0D 0A'
data_gps_alarm_data = '78 78 25 16 10 01 0E 0A 2A 33 CB 02 7A DE 7C 0C 46 50 00 1E 15 3A 09 01 CC 00 28 7D 00 1E 16 F0 06 04 05 01 00 49 FE 4B 0D 0A'
data_lbs_alarm_data = '78 78 12 19 01 CC 00 28 7D 00 1F 71 0A 05 04 03 01 00 0A A6 F7 0D 0A'
data_adjust_time = '78 78 05 8A 00 06 88 29 0D 0A'
data_lbs_extension = '78 78 3B 18 10 01 0F 0B 32 1B 01 CC 01 25 B1 00 6F F1 23 25 B1 00 6B 0E 17 25 AE 00 5F B7 13 25 B1 00 5C 90 13 25 B1 00 6F F0 11 25 B1 00 6B 0D 10 25 B1 00 5C 4A 0F FF 00 01 00 0A 77 95 0D 0A'
data_generic_message ='79 79 00 7F 94 04 41 4C 4D 31 3D 43 34 3B 41 4C 4D 32 3D 43 43 3B 41 4C 4D 33 3D 34 43 3B 53 54 41 31 3D 43 30 3B 44 59 44 3D 30 31 3B 53 4F 53 3D 2C 2C 3B 43 45 4E 54 45 52 3D 3B 46 45 4E 43 45 3D 46 65 6E 63 65 2C 4F 4E 2C 30 2C 32 33 2E 31 31 31 38 30 39 2C 31 31 34 2E 34 30 39 32 36 34 2C 34 30 30 2C 49 4E 20 6F 72 20 4F 55 54 2C 30 3B 4D 49 46 49 3D 4D 49 46 49 2C 4F 46 46 00 0A 06 1E 0D 0A'
data_command_response ='78 78 30 81 28 00 00 00 03 5b 56 45 52 53 49 4f 4e 5d 47 54 30 33 46 5f 32 30 5f 36 31 44 4d 32 52 31 5f 44 32 33 5f 52 30 5f 56 30 35 00 01 01 ea 00 d2 0d 0a'
data_command_response ='79 79 00 87 94 04 41 4c 4d 31 3d 44 35 3b 41 4c 4d 32 3d 44 35 3b 41 4c 4d 33 3d 35 37 3b 53 54 41 31 3d 32 30 3b 44 59 44 3d 30 31 3b 53 4f 53 3d 31 33 39 31 36 36 32 34 34 37 37 2c 31 38 36 30 31 36 33 36 33 34 36 2c 2c 3b 43 45 4e 54 45 52 3d 3b 46 45 4e 43 45 3d 46 65 6e 63 65 2c 4f 46 46 2c 30 2c 30 2e 30 30 30 30 30 30 2c 30 2e 30 30 30 30 30 30 2c 33 30 30 2c 49 4e 20 6f 72 20 4f 55 54 2c 31 3b 02 44 9e 17 0d 0a'
data_wifi = ' 78 78 56 2c 12 09 1c 02 02 36 01 cc 00 18 0b 00 67 0e 34 18 0b 00 67 37 2b 18 0b 00 66 c4 24 18 0d 00 66 56 1a 18 b9 00 67 b4 16 18 0b 00 66 9d 16 00 00 00 00 00 00 ff 04 ec 6c 9f aa 1a de 26 ec 6c 9f 9b ba fb 2d a0 a3 3b a3 3d 80 45 50 fa 84 78 b3 62 55 00 af 4b eb 0d 0a 78 78 56 2c 12 09 1c 02 05 36 01 cc 00 18 0b 00 67 0e 34 18 0b 00 67 37 2a 18 0b 00 66 c4 25 18 0d 00 66 56 1b 18 b9 00 67 b4 16 18 0b 00 66 9d 14 00 00 00 00 00 00 ff 04 ec 6c 9f aa 1a de 28 ec 6c 9f 9b bb 07 2d a0 a3 3b a3 3d 80 43 02 fa 84 78 b3 62 54 00 d4 91 c3 0d 0a 78 78 56 2c 12 09 1c 02 08 29 01 cc 00 18 0b 00 67 0e 32 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ff 04 ec 6c 9f aa 1a de 25 ec 6c 9f 9b bb 04 2e a0 a3 3b a3 3d 80 47 50 fa 84 78 b3 62 56 00 05 2d 24 0d 0a 78 78 56 2c 12 09 1c 02 0b 29 01 cc 00 18 0b 00 67 0e 34 18 0b 00 67 37 2a 18 0d 00 66 56 1a 18 0b 00 66 9d 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ff 04 ec 6c 9f aa 1a de 28 ec 6c 9f 9b bb 04 2f a0 a3 3b a3 3d 80 49 50 fa 84 78 b3 88 4f 00 29 a9 6c 0d 0a 78 78 5d 2c 12 09 1c 02 0e 29 01 cc 00 18 0b 00 67 0e 34 18 0b 00 67 37 31 18 0d 00 66 56 1a 18 b9 00 67 b4 18 18 0b 00 66 9d 15 18 b9 00 67 7a 14 00 00 00 00 00 00 ff 05 ec 6c 9f aa 1a de 28 ec 6c 9f 9b ba fe 2f a0 a3 3b a3 3d 80 48 02 fa 84 78 b3 88 51 50 fa 84 74 f3 18 54 00 4a 41 1d 0d 0a 78 78 56 2c 12 09 1c 02 11 29 01 cc 00 18 0b 00 67 0e 33 18 0b 00 67 37 30 18 0b 00 66 c4 20 18 0d 00 66 56 1c 18 0b 00 66 9d 15 00 00 00 00 00 00 00 00 00 00 00 00 ff 04 ec 6c 9f aa 1a de 26 ec 6c 9f 9b ba fe 2c a0 a3 3b a3 3d 80 42 02 fa 84 78 b3 88 53 00 6e 73 07 0d 0a 78 78 56 2c 12 09 1c 02 14 29 01 cc 00 18 0b 00 67 0e 33 18 0b 00 67 37 32 18 0d 00 66 56 1e 18 0b 00 66 c4 1c 18 b9 00 67 e6 17 18 b9 00 67 7a 16 18 0b 00 66 9d 14 ff 04 ec 6c 9f aa 1a de 27 ec 6c 9f 9b bb 07 2c a0 a3 3b a3 3d 80 44 02 fa 84 78 b3 88 4f 00 90 b3 d0 0d 0a 78 78 5d 2c 12 09 1c 02 17 29 01 cc 00 18 0b 00 67 0e 35 18 0b 00 67 37 32 18 0d 00 66 56 1e 18 b9 00 67 e6 17 18 0b 00 66 9d 15 00 00 00 00 00 00 00 00 00 00 00 00 ff 05 ec 6c 9f aa 1a de 28 ec 6c 9f 9b ba fb 2c a0 a3 3b a3 3d 80 43 02 fa 84 78 b3 88 50 ec 6c 9f 9c bd 86 52 00 b4 c7 2f 0d 0a 78 78 4f 2c 12 09 1c 02 1a 29 01 cc 00 18 0b 00 67 0e 34 18 0b 00 67 37 32 18 0d 00 66 56 1d 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ff 03 ec 6c 9f 9b bb 04 2c a0 a3 3b a3 3d 80 40 50 fa 84 78 b3 62 57 00 d8 de 8c 0d 0a 78 78 56 2c 12 09 1c 02 1d 16 01 cc 00 18 0b 00 67 0e 34 18 0d 00 66 56 1c 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ff 04 ec 6c 9f aa 1a de 29 ec 6c 9f 9b bb 04 2c a0 a3 3b a3 3d 80 42 02 fa 84 78 b3 88 50 00 05 f9 c6 0d 0a'
# 460	1	9649	28657	23.1067600250244	114.416069030762	广东省惠州市惠城区江北街道水北

data_ev25 = '78 78 25 26 12 09 1d 0e 37 14 c0 03 57 36 e9 0d 07 74 12 00 04 00 09 01 cc 0f 18 79 00 86 2a 08 06 04 03 01 01 db 71 d5 0d 0a'

# data_lbs_extension ='78 78 3b 18 12 09 16 13 3b 28 01 cc 00 18 79 00 86 2a 3d 18 79 00 86 51 27 18 86 00 68 a3 23 18 79 00 86 49 23 18 86 00 68 19 22 18 79 00 86 3e 1c 18 76 00 86 e4 1b ff 00 01 00 bd 48 89 0d 0a'

test_items =[
    # data_login_req,
    # data_heartbeat,
    # data_gps_location,
    # data_lbs_extension,
    # data_gps_alarm_data,
    # data_lbs_alarm_data,
    # data_adjust_time,
    # data_generic_message,
    # data_command_response
    # data_wifi
    # data_ev25
]

print MessageLogin.__name__

def test_main():
    for data in test_items:
        bytes = ''.join(map(chr,map(lambda _:int(_,16),data.split())))
        print 'Raw data:'
        print bytes
        acc = DataAccumulator()
        messages = acc.enqueue(bytes)
        print 'Message Parsed:'
        print messages
        for msg in messages:
            print msg.dict()
            if isinstance(msg,MessageLogin):
                print msg.extra.to_bytes()

            if isinstance(msg,MessageAdjustTime):
                print msg.response()

"""
原始数据：78 78 3B 18 10 01 0F 0B 32 1B 01 CC 01 25 B1 00 6F F1 23 25 B1 00 6B 0E 17 25 AE 00 5F B7 13 25 B1 00 5C 90 13 25 B1 00 6F F0 11 25 B1 00 6B 0D 10 25 B1 00 5C 4A 0F FF 00 01 00 0A 77 95 0D 0A

包类型：LBS扩展包(18)
   CRC：CRC正确，7795
   包长度  =59(3B)
   16年1月15日11:50:27(10010F0B321B)
   MCC:460(01CC)    MNC:1(01)    LAC:9649(25B1)    CELL_ID:28657(006FF1)    RSSI:35(23)
   LAC1:9649(25B1)    CELL_ID1:27406(006B0E)    RSSI1:23(17)     LAC2:9646(25AE)    CELL_ID2:24503(005FB7)    RSSI2:19(13)     
   LAC3:9649(25B1)    CELL_ID3:23696(005C90)    RSSI3:19(13)     LAC4:9649(25B1)    CELL_ID4:28656(006FF0)    RSSI4:17(11)     
   LAC5:9649(25B1)    CELL_ID5:27405(006B0D)    RSSI5:16(10)     LAC6:9649(25B1)    CELL_ID6:23626(005C4A)    RSSI6:15(0F)     
   TA（时间提前量）:255(FF)    语言:(0001)    序列号:10(000A)
"""

"""
相关问题： 
======
1. 如何修改上报gps的间隔时间？

"""
test_main()