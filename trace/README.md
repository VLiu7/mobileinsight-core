# trace目录下每个.py脚本都是做什么的？

* `mcs.py`: 绘制MCS(Modulation Coding Scheme)随时间变化的曲线图
* `sat_signal.py`: 绘制信号强度随时间变化的曲线图(目前认为-130~-110为合法范围，进行过滤)
* `signal_and_snr.py`: 绘制信号强度和信噪比随时间变化的曲线图（为了寻找二者之间可能存在的correlation，当然结果是没有)
* `smac_crc_error.py`: 统计MAC层出现CRC error的频率
* `split_into_layers.py`: 按照ip、mac、rlc将一个log中的消息分成三类，分别写进三个文件，命名为原文件名+'_ip'、原文件名+'_mac'、原文件名+'_rlc'
* `rlc_throughput.py`: 绘制上下行链路的序列号随时间的变化曲线图；传输字节数随时间变化曲线图
* `downlink_retransmission.py`: 统计下行链路的block因为"out of receiving window"被rejected的频率；统计duplicate block，retransmission block，第一次传输就失败的block的频率