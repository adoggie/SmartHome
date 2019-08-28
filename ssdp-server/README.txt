
Help Resource Links
---------------------

http://webpy.org/docs/0.3/tutorial

Rokid
------
https://developer.rokid.com/docs/rokid-homebase-docs/connect/http-remote-driver.html

pip install web.py


Main Module Services
---------------------
rokid.py - 若琪设备协议转换
agent.py - 符合若琪接入规范的服务
ssdp_server.py - 供若琪设备进行服务发现的服务



部署到arm主机
-----------
拷贝 pylibs/webpy 到 /python273/lib/site-packages/
mkdir /home/smartbox/rokid
拷贝  agent.py , profile-rokid.json , rokid.py , sensor_defs.py 到 /home/smartbox/rokid
运行  python agent.py 8088
