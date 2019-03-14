# zabbix-kvm doc
#### 此文档适用于使用zabbix监视kvm虚拟机性能的zabbix-agent端
## 依赖
    需安装libvirt和python2并配置完成
    需安装python libvirt包:
    (本项目集成libvirt包 如需安装 请使用命令cd libvirt-python,python setup.py build,sudo python setup.py install)
    (详情请查看libvirt-python文件夹内的README)
## 使用方法
#### 1. 部署文件
    1 在所有zabbix-agent机器上部署此项目内的zabbix-kvm.py文件和userparameter_zabbix-kvm.conf文件
    2 将conf文件放置于zabbix-agent配置可以获取到的文件夹内
    3 将py文件放置于/etc/zabbix/文件夹内。若想自定义py文件放置位置 需更改conf文件 将其中的"/etc/zabbix/zabbix-kvm.py"换为py文件的实际位置
#### 2. 创建一个自动发现模版用来自动发现虚拟机
    1 创建一个模版 并于它创建一个自动发现规则 key值为"kvm.domain.discover"
    2 点开这个自动发现规则的主机模版 创建一个名为"{#DOMAINUUID}"的主机模版
#### 3. 创建一个监控模版
    1 创建一个模版
    2 在此模版上添加四个监控项 key值分别为
      kvm.domain.cpu_util[{HOST.NAME}];浮点型 单位'%'
      kvm.domain.mem_usage[{HOST.NAME}];浮点型 单位'%'
      kvm.domain.rd_bytes[{HOST.NAME}];整数型 单位'bps'
      kvm.domain.wr_bytes[{HOST.NAME}];整数型 单位'bps'
      kvm.domain.mem_used[{HOST.NAME}];浮点型 单位MB
      kvm.domain.disk_rate[{HOST.NAME}];浮点型 单位%
      kvm.domain.disk_used[{HOST.NAME}];浮点型 单位MB
    3 在此模版上添加一个自动发现规则用来发现网卡 key值为kvm.network.discover[{HOST.NAME}]
    4 在此模版的自动发现规则上添加两个监控项原型
      名字 {#VS_NIC} network_in /key值 kvm.domain.net_in[{#VS_NAME},{#VS_NIC}]
      名字 {#VS_NIC} network_out /key值 kvm.domain.net_out[{#VS_NAME},{#VS_NIC}]
    5 将此监控模版链接到步骤3创建的自动发现模版的主机模版上
#### 4. 启动
    1 将上述已链接过监控模版的自动发现模版配置于一台可以获取到所有虚拟机数据的agent机器上
    2 重启各自agent机器上的zabbix-agent客户端并等待数据刷新
#### 5. debug
    libvirt可能会隔一段时间无法执行 请重启libvirt和agent
    然后删除所有被发现的主机 然后取消模版到主机的链接并重新链接  