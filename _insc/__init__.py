print('import serial')
import serial
print('import serial done')
print('import win32com')
import win32com
print('import win32com done')
print('import win32com.client')
import win32com.client
print('import win32com.client done')
print('from canlib import canlib, Frame')
from canlib import canlib, Frame
print('from canlib import canlib, Frame done')


############################################ Serial #################################################
class TestSerialControl:
    """通过USB串口通讯控制测试台"""

    def init(self, com, baudrate=38400):
        self.m_srl = serial.Serial(com, baudrate)
        self.digit_stat_1 = 0x0003  # 保存'上电','点火'的状态
        self.digit_stat_2 = 0x0000  # 保存其它数字信号的状态,设置其中某一个时，不会影响其他的开关状态

        self._m_ad_name = ['增压温度', '燃气温度', '空调温度', '冷却液温度', '减压阀温度', '进气温度', '曲轴通风', 'GPF前温',
                           'GPF后温', '水箱温度', 'CNG泄漏2', 'CNG泄漏1', '后氧', '前氧', '预留T14', '预留T15',
                           '气瓶压力', '预留AO1', '机械TPS', '进气压力', '增压压力', '燃气压力', '踏板2', '踏板1',
                           '预留AO8', '预留AO9', '油箱压力', '减压阀压力', 'GPF压力', '真空压力', '脱附压力', 'EGR阀位置',
                           'CAM-0', 'CAM-1', '转速', '车速']
        self._m_ad_tar_cmd = [0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
                              0x4a, 0x4b, 0x4c, 0x4d, 0x56, 0x4e, 0x60, 0x61,
                              0x4f, 0x5d, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55,
                              0x5e, 0x5f, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c,
                              0x3e, 0x3f, 0x40, 0x41]  # 与串口通讯时，对应模拟信号的ID
        self._ad_dic = dict(zip(self._m_ad_name, enumerate(self._m_ad_tar_cmd)))  # ‘模拟信号名称’:(排序编号,通讯ID)

        self._m_dig_name = ['上电', '点火',
                            '离合器顶', '电气负载2', '刹车', '离合', '空调', '空调中压', '油气/再生', '排制/启动',
                            '巡航-', '巡航+', '巡航取消', '巡航开关', '空挡开关', '刹车灯', '电气负载1', '安全气囊']
        self._m_dig_bits = [0x01, 0x02,
                            0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01,
                            0x8000, 0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200, 0x0100]  # 与串口通讯时,对应数字信号的掩码
        self._digit_dic = dict(zip(self._m_dig_name, enumerate(self._m_dig_bits)))  # ‘数字信号名称’:(排序编号,掩码)

    ad_init_dic = {}

    def to(self, ad_name, target, step=0.0, period=0, keep=0):
        """改变模拟信号,形参分别为:信号名称字符串,目标值,每一周期改变的步长,步长周期,保持时间
            步长或周期为0时,直接改变信号至目标值
            步长,周期,保持时间均有值时,信号波动变化,以目标值为均值,每5ms变化步长值,变化periodms时间后,保持keepms,再反向变化"""
        idx, ad_cmd = self._ad_dic[ad_name]
        if idx <= 33:
            ad_target = int(target * 100)
            ad_target = max(ad_target, 0)
            ad_target = min(ad_target, 999)
        else:
            ad_target = int(target)
            ad_target = max(ad_target, 0)
            ad_target = min(ad_target, 10000)
        ad_hi = ad_target >> 8
        ad_lo = ad_target & 0x00ff

        if step == 0 or period == 0:
            hexList = [0xa5, 0x5a, 0x06, 0x83, 0x00, ad_cmd, 0x01, ad_hi, ad_lo]
        else:
            ad_step = int(step * 100) if idx <= 33 else int(step)
            ad_step = max(ad_step, 0)
            ad_step = min(ad_step, 255)
            ad_period = int(period / 5)
            ad_period = max(ad_period, 0)
            ad_period = min(ad_period, 255)
            ad_keep = int(keep / 5)
            ad_keep = max(ad_keep, 0)
            ad_keep = min(ad_keep, 255)
            hexList = [0xa5, 0x5a, 0x06, ad_cmd, ad_hi, ad_lo, ad_step, ad_period, ad_keep]
        self.m_srl.write(bytes(hexList))  # 向串口发送数据
        self.m_srl.flush()
        # time.sleep(0.0000001)
        # print(ad_name, target)

    def switch_on(self, *digit_name):
        """向串口发送数据,指示将某一数字信号置位"""
        send1_flag, send2_flag = 0, 0
        all_switch1 = self.digit_stat_1
        all_switch2 = self.digit_stat_2
        for name_temp in digit_name:
            idx, digit_bit = self._digit_dic[name_temp]
            if idx in [0, 1]:
                all_switch1 |= digit_bit
                send1_flag = 1
            else:
                all_switch2 |= digit_bit
                send2_flag = 1
        self.digit_stat_1 = all_switch1
        self.digit_stat_2 = all_switch2
        if send1_flag:
            switch_hi = all_switch1 >> 8
            switch_lo = all_switch1 & 0x00ff
            hexList = [0xa5, 0x5a, 0x06, 0x83, 0x00, 0x67, 0x01, switch_hi, switch_lo]
            self.m_srl.write(bytes(hexList))
            self.m_srl.flush()
        if send2_flag:
            switch_hi = all_switch2 >> 8
            switch_lo = all_switch2 & 0x00ff
            hexList = [0xa5, 0x5a, 0x06, 0x83, 0x00, 0x66, 0x01, switch_hi, switch_lo]
            self.m_srl.write(bytes(hexList))
            self.m_srl.flush()

    def switch_off(self, *digit_name):
        """向串口发送数据,指示将某一数字信号复位"""
        send1_flag, send2_flag = 0, 0
        all_switch1 = self.digit_stat_1
        all_switch2 = self.digit_stat_2
        for name_temp in digit_name:
            idx, digit_bit = self._digit_dic[name_temp]
            if idx in [0, 1]:
                all_switch1 &= (~digit_bit)
                send1_flag = 1
            else:
                all_switch2 &= (~digit_bit)
                send2_flag = 1
        self.digit_stat_1 = all_switch1
        self.digit_stat_2 = all_switch2
        if send1_flag:
            switch_hi = all_switch1 >> 8
            switch_lo = all_switch1 & 0x00ff
            hexList = [0xa5, 0x5a, 0x06, 0x83, 0x00, 0x67, 0x01, switch_hi, switch_lo]
            self.m_srl.write(bytes(hexList))
            self.m_srl.flush()
        if send2_flag:
            switch_hi = all_switch2 >> 8
            switch_lo = all_switch2 & 0x00ff
            hexList = [0xa5, 0x5a, 0x06, 0x83, 0x00, 0x66, 0x01, switch_hi, switch_lo]
            self.m_srl.write(bytes(hexList))
            self.m_srl.flush()

    def wave(self, ad_name, ad_hi, ad_lo, change_time_ms, keep_time_ms):
        """令某一模拟信号周期性波动
            在最大值ad_hi与最小值ad_lo之间波动,信号上升/下降的时间为change_time_ms
            信号保持在最大值/最小值的时间为keep_time_ms"""
        ad_target = (ad_hi + ad_lo) / 2
        ad_hi = max(ad_hi, ad_lo)
        ad_step = (ad_hi - ad_target) * 10 / change_time_ms
        ad_period = change_time_ms / 2
        if ad_step < 0.01: print('变化时间过长，无法进入AD波动变化')
        self.to(ad_name, ad_target, ad_step, ad_period, keep_time_ms)

    def read_all(self):
        return self.m_srl.read(self.m_srl.inWaiting())


############################################### CAN ################################################
class TestCanControl:
    """利用Kvaser-CAN控制测试台"""
    ad_init_dic = {}

    def init(self, can_channel=0, can_flags=canlib.Open.OVERRIDE_EXCLUSIVE, can_bitrate=canlib.canBITRATE_50K):
        self.m_can = canlib.openChannel(can_channel, flags=can_flags, bitrate=can_bitrate)
        self.m_can.setBusOutputControl(canlib.Driver.NORMAL)
        self.m_can.busOn()

        self._simubox_id = 0x7b  # canID
        self._m_ad_name = ['增压温度', '燃气温度', '空调温度', '冷却液温度', '减压阀温度', '进气温度', '曲轴通风', 'GPF前温',
                           'GPF后温', '水箱温度', 'CNG泄漏2', 'CNG泄漏1', '后氧', '前氧', '预留T14', '预留T15',
                           '气瓶压力', '预留AO1', '机械TPS', '进气压力', '增压压力', '燃气压力', '踏板2', '踏板1',
                           '预留AO8', '预留AO9', '油箱压力', '减压阀压力', 'GPF压力', '真空压力', '脱附压力', 'EGR阀位置',
                           'CAM-0', 'CAM-1', '转速', '车速']
        self._m_ad_tar_cmd = [0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
                              0x4a, 0x4b, 0x4c, 0x4d, 0x56, 0x4e, 0x60, 0x61,
                              0x4f, 0x5d, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55,
                              0x5e, 0x5f, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c,
                              0x3e, 0x3f, 0x40, 0x41]  # 与CAN通讯时，对应模拟信号的ID
        self._ad_dic = dict(zip(self._m_ad_name, enumerate(self._m_ad_tar_cmd)))  # ‘模拟信号名称’:(排序编号,通讯ID)

        self._m_dig_name = ['上电', '点火',
                            '离合器顶', '电气负载2', '刹车', '离合', '空调', '空调中压', '油气/再生', '排制/启动',
                            '巡航-', '巡航+', '巡航取消', '巡航开关', '空挡开关', '刹车灯', '电气负载1', '安全气囊']
        self._m_dig_bits = [0x01, 0x02,
                            0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01,
                            0x8000, 0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200, 0x0100]  # 与CAN通讯时,对应数字信号的掩码
        self._digit_dic = dict(zip(self._m_dig_name, enumerate(self._m_dig_bits)))  # ‘数字信号名称’:(排序编号,掩码)

    def to(self, name, target, start=None, step=0, period_ms=0, keep_time_ms=0):
        """改变模拟信号,形参分别为:信号名称字符串,目标值,起始值,每一周期改变的步长,步长周期,保持时间
            起始值、步长或周期为没有值时,直接改变信号至目标值,否则递变至起始值，再从起始值递变至目标值
            步长,周期,保持时间均有值时,信号波动变化,保持keepms,再反向变化"""
        if start == None:
            icmd = 0  # 立即改变
        elif step and period_ms:
            if keep_time_ms == 0:
                icmd = 1  # 递增
            else:
                icmd = 2  # 波动
        else:
            icmd = 0

        tempIdx, tempCmd = self._ad_dic[name]
        canId = self._simubox_id

        if tempIdx <= 33:
            target_lmt = target * 100
            target_lmt = max(target_lmt, 0)
            target_lmt = min(target_lmt, 999)
            if icmd:
                start_lmt = start * 100
                start_lmt = max(start_lmt, 0)
                start_lmt = min(start_lmt, 999)

                step_lmt = step * 100
                step_lmt = max(step_lmt, 0)
                step_lmt = min(step_lmt, 255)
        else:
            if tempIdx == 34:
                target = target / 2
            target_lmt = max(target, 0)
            target_lmt = min(target_lmt, 4096)
            if icmd:
                if tempIdx == 34:
                    start = start / 2
                start_lmt = max(start, 0)
                start_lmt = min(start_lmt, 4096)

                step_lmt = max(step, 0)
                step_lmt = min(step_lmt, 255)

        target_lmt = int(target_lmt)
        iTarHi = target_lmt >> 8
        iTarLo = target_lmt & 0x00FF

        if icmd:
            period_lmt = period_ms / 5
            period_lmt = max(period_lmt, 0)
            period_lmt = min(period_lmt, 255)

            keep_time_lmt = keep_time_ms / 5
            keep_time_lmt = max(keep_time_lmt, 0)
            keep_time_lmt = min(keep_time_lmt, 2550)

            start_lmt = int(start_lmt)
            iStRgHi = start_lmt >> 8
            iStRgLo = start_lmt & 0x00FF

            bHi = (iTarHi & 0x0F) + ((iStRgHi & 0x0F) << 4)

            iStep = int(step_lmt)
            iPrd = int(period_lmt)
            iKeep = int(keep_time_lmt)

        if icmd == 0:
            bHi = iTarHi & 0x0F
            can_frame = Frame(id_=canId, data=[0x54, tempCmd, bHi, iTarLo], dlc=4)
        elif icmd == 1:
            can_frame = Frame(id_=canId, data=[0x55, tempCmd, bHi, iTarLo, iStRgLo, iStep, iPrd], dlc=7)
        else:
            if iKeep <= 255:
                can_frame = Frame(id_=canId, data=[0x56, tempCmd, bHi, iTarLo, iStRgLo, iStep, iPrd, iKeep], dlc=8)
            else:
                can_frame = Frame(id_=canId, data=[0x57, tempCmd, bHi, iTarLo, iStRgLo, iStep, iPrd, iKeep // 10],
                                  dlc=8)
        self.m_can.writeWait(can_frame, timeout=200)
        # print(list(can_frame.data))

    def switch_on(self, *digit_name):
        """向CAN发送数据,指示将某一数字信号置位"""
        send1_flag, send2_flag = 0, 0
        all_mask1, all_mask2 = 0x00, 0x00
        canId = self._simubox_id
        for name_temp in digit_name:
            idx, digit_bit = self._digit_dic[name_temp]
            if idx in [0, 1]:
                all_mask1 |= digit_bit
                send1_flag = 1
            else:
                all_mask2 |= digit_bit
                send2_flag = 1
        if send1_flag:
            can_frame = Frame(id_=canId, data=[0x50, 0x01, 0xff, all_mask1], dlc=4)
            self.m_can.writeWait(can_frame, timeout=200)
            # print(list(can_frame.data))

        if send2_flag:
            mask_hi = (all_mask2 >> 8) & 0x00ff
            mask_lo = all_mask2 & 0x00ff
            can_frame = Frame(id_=canId, data=[0x51, 0x01, 0xff, mask_lo, 0xff, mask_hi], dlc=6)
            self.m_can.writeWait(can_frame, timeout=200)
            # print(list(can_frame.data))

    def switch_off(self, *digit_name):
        """向CAN发送数据,指示将某一数字信号复位"""
        send1_flag, send2_flag = 0, 0
        all_mask1, all_mask2 = 0x00, 0x00
        canId = self._simubox_id
        for name_temp in digit_name:
            idx, digit_bit = self._digit_dic[name_temp]
            if idx in [0, 1]:
                all_mask1 |= digit_bit
                send1_flag = 1
            else:
                all_mask2 |= digit_bit
                send2_flag = 1
        if send1_flag:
            can_frame = Frame(id_=canId, data=[0x50, 0x01, 0x00, all_mask1], dlc=4)
            self.m_can.writeWait(can_frame, timeout=200)
            # print(list(can_frame.data))

        if send2_flag:
            mask_hi = (all_mask2 >> 8) & 0x00ff
            mask_lo = all_mask2 & 0x00ff
            can_frame = Frame(id_=canId, data=[0x51, 0x01, 0x00, mask_lo, 0x00, mask_hi], dlc=6)
            self.m_can.writeWait(can_frame, timeout=200)
            # print(list(can_frame.data))

    def wave(self, ad_name, ad_hi, ad_lo, change_time_ms, keep_time_ms):
        """令某一模拟信号周期性波动
            在最大值ad_hi与最小值ad_lo之间波动,信号上升/下降的时间为change_time_ms
            信号保持在最大值/最小值的时间为keep_time_ms"""
        assert change_time_ms >= 5, 'Function wave() : change_time_ms应大于等于5ms'
        ad_step_unit, ad_step_max = (0.01, 5) if self._ad_dic[ad_name][0] <= 33 else (1, 8192)
        ad_step = ad_step_unit
        ad_delta = abs(ad_hi - ad_lo)
        while True:  # 从最小步长开始循环，若求出的period过于小,则增加步长，直到period合理
            ad_period_ms = change_time_ms * ad_step / ad_delta if ad_delta else 5
            if ad_period_ms >= 5 or ad_step >= ad_step_max: break
            ad_step += ad_step_unit
        TestCanControl.to(self, ad_name, ad_hi, ad_lo, ad_step, ad_period_ms, keep_time_ms)


############################################### INCA ##################################################
class IncaControl:
    """利用INCA接口控制INCA或读取INCA数据"""

    def init(self, expinit=True):
        self.inca = win32com.client.Dispatch('inca.inca')
        if expinit: self.exp_init()

    def exp_init(self):
        self.exp = self.inca.GetOpenedExperiment()
        assert self.exp, '无法连接到INCA实验环境'
        self.device = {}
        for dev in self.exp.GetAllDevices():  # 返回源数据集,如CCP: 1
            self.device[dev.GetName()] = dev

    def a2l_init(self, device_name='CCP: 1'):
        self.a2l = self.device[device_name].GetASAP2Module()
        self._a2ldevice = device_name

    reset_cal_name = []
    reset_cal_dict = {}

    def _getelement_m(self, name):
        a = self.exp.GetMeasureElement(name)
        assert a, '找不到该测量量:"%s"' % name
        return a

    def _getelement_c(self, name):
        a = self.exp.GetCalibrationElement(name)
        assert a, '找不到该标定量:"%s"' % name
        return a

    def mget(self, name):  # 返回测量量物理值
        """
        读取测量量的物理值

        name: 变量名称 字符串
        返回 浮点数
        """
        return self._getelement_m(name).GetValue().GetDoublePhysValue()

    def cget(self, name):  # 返回标定单参物理值(包括RAMCal数据)
        """
        读取标定单参的物理值(包括RAMCal数据)

        name: 变量名称 字符串
        返回 浮点数
        """
        return self._getelement_c(name).GetValue().GetDoublePhysValue()

    def mget_d(self, name):  # 返回测量量机器值
        """
        读取测量量机器值

        name: 变量名称 字符串
        返回 浮点数
        """
        return self._getelement_m(name).GetValue().GetImplValue()

    def mget_d_int(self, name):  # 返回测量量机器值
        """
        读取测量量机器值

        name: 变量名称 字符串
        返回 整数
        """
        return int(self._getelement_m(name).GetValue().GetImplValue())

    def cget_d(self, name):  # 返回标定单参机器值(包括RAMCal数据)
        """
        读取标定单参机器值(包括RAMCal数据)

        name: 变量名称 字符串
        返回 浮点数
        """
        return self._getelement_c(name).GetValue().GetImplValue()

    def cget_d_int(self, name):  # 返回标定单参机器值(包括RAMCal数据)(int)
        """
        读取标定单参机器值(包括RAMCal数据)

        name: 变量名称 字符串
        返回 整数
        """
        return self._getelement_c(name).GetValue().GetLongImplValue()

    def cset(self, name, value):  # 设置标定单参物理值(包括RAMCal数据)
        """
        设置标定单参物理值

        name: 变量名称 字符串
        value: 设定的数值 整数或浮点数
        返回 设置操作成功与否 布尔值
        """
        scalar = self._getelement_c(name).GetValue()
        assert scalar.IsScalar(), '标定量：' + name + '  不是单参'
        assert not scalar.IsWriteProtected(), '标定量：' + name + '  无法被标定'  # 可能不是在线标定数据
        return scalar.SetDoublePhysValue(value)

    def tabget(self, name):  # 读表格，返回数组，包含表格数据、X轴数据、Y轴数据
        """
        读取表格物理值

        如果读取的表格是一维表，则返回嵌套了2个一维列表的列表，嵌套的第1个列表存储了表格数据，嵌套的第2个列表存储了轴的数据
        如果读取的表格是二维表，则返回嵌套了3个列表的列表，嵌套的列表分别为保存表格数据的2维列表，保存X轴数据的1维列表，保存Y轴数据的1维列表
        其中表格2维数据结构是:[ [第1列], [第2列], [第3列], [第4列] ]  ，即索引方式是matrix_list[x][y]

        name: 变量名称 字符串
        返回 列表
        """
        tab = self._getelement_c(name).GetValue()
        if tab.IsTwoDTable():
            matrix = tab.GetValue().GetDoublePhysValue()
            matrix_list = []
            for tup in matrix:
                matrix_list.append(list(tup))  # 转为列表
            return [matrix_list, list(tab.GetXDistribution().GetDoublePhysValue()),
                    list(tab.GetYDistribution().GetDoublePhysValue())]
            # matrix_list : [ [第1列(x0)], [第2列(x1)], [第3列(x2)], [第4列(x3)] ]  matrix_list[x][y]
        elif tab.IsOneDTable():
            return [list(tab.GetValue().GetDoublePhysValue()), list(tab.GetDistribution().GetDoublePhysValue())]

    def tabget_d_int(self, name):  # 读表格，返回数组，包含表格数据、X轴数据、Y轴数据 (机器值整数)
        """
        读取表格物理值机器值

        与tabget()的不同之处在于存储的数据是整数机器值而非浮点数物理值

        name: 变量名称 字符串
        返回 列表
        """
        tab = self._getelement_c(name).GetValue()
        if tab.IsTwoDTable():
            matrix = tab.GetValue().GetImplValue()
            matrix_int = []
            for tup in matrix:
                matrix_int.append(list(int(a) for a in tup))
            return [matrix_int, list(int(a) for a in tab.GetXDistribution().GetImplValue()),
                    list(int(a) for a in tab.GetYDistribution().GetImplValue())]
        elif tab.IsOneDTable():
            return [list(int(a) for a in tab.GetValue().GetImplValue()),
                    list(int(a) for a in tab.GetDistribution().GetImplValue())]

    def reset_read(self, name):  # 读表格，返回数组，包含表格对象、表格数据、X轴数据、Y轴数据 # 增加读单参标定量
        """
        读取标定量对象物理值

        返回列表，2维表包含表格对象、表格数据、X轴数据、Y轴数据，1维表包含表格对象、表格数据、轴数据，单参包含标定量对象、标定数值

        name: 变量名称 字符串
        返回 列表
        """
        cal = self._getelement_c(name).GetValue()
        if cal.IsTwoDTable():
            return [cal, cal.GetValue().GetDoublePhysValue(), cal.GetXDistribution().GetDoublePhysValue(),
                    cal.GetYDistribution().GetDoublePhysValue()]
        elif cal.IsOneDTable():
            return [cal, cal.GetValue().GetDoublePhysValue(), cal.GetDistribution().GetDoublePhysValue()]
        else:
            return [cal, cal.GetDoublePhysValue()]

    def reset(self, obj, name=''):  # 重置标定量，输入标定量对象数组或标定量名称字符串
        """
        重置标定量

        将标定量的数据回滚到之前的某一状态

        obj: 通过reset_read()得到的列表 或 字符串名称（需要reset_cal_name里存在的）
        name: 标定量名称，不用填写
        返回 操作成功与否 布尔值
        """
        if isinstance(obj, str):
            obj = self.reset_cal_dict[obj]
        cal = obj[0]
        try:
            if cal.IsTwoDTable():
                a = cal.GetValue().SetDoublePhysValue(obj[1])
                b = cal.GetXDistribution().SetDoublePhysValue(obj[2])
                c = cal.GetYDistribution().SetDoublePhysValue(obj[3])
                rslt = a and b and c
            elif cal.IsOneDTable():
                a = cal.GetValue().SetDoublePhysValue(obj[1])
                b = cal.SetDistribution().SetDoublePhysValue(obj[2])
                rslt = a and b
            else:
                a = cal.SetDoublePhysValue(obj[1])
                rslt = a
            return bool(rslt)
        except:
            print('重置标定量:"%s"失败 ！！' % name)
            return False

    def all_reset_read(self):
        """
        读取reset_cal_name列表中的所有标定量数据并存放在reset_cal_dict里
        """
        for cal in self.reset_cal_name:
            self.reset_cal_dict[cal] = self.reset_read(cal)

    def all_reset(self):
        """
        将reset_cal_dict中的所有标定量数据回滚
        """
        for name, obj in self.reset_cal_dict.items():
            self.reset(obj, name)

    def tabset(self, name, value=None, xaxis_list=None, yaxis_list=None):  # 设置表格，输入单个量或是数组
        """
        设置表格物理值数据

        更改表格数据时参数可以是列表，也可以是数字，更改轴时参数必须是列表类型
        传入列表时，列表的大小应该与表格/轴的大小相同

        name: 变量名称 字符串
        value: 表格数据，可以是对应的1维or2维列表，也可以是一个整数/浮点数
        xaxis_list: X轴数据 列表
        yaxis_list: Y轴数据 列表
        返回 操作成功与否 布尔值
        """
        tab = self._getelement_c(name).GetValue()
        assert tab.IsCalibrationDataItem(), name + '  不是标定量'
        tab_value = tab.GetValue()
        assert (not tab_value.IsWriteProtected()) or (value == None), name + '  无法被标定'  # 可能不是在线标定数据
        input_way = 1 if isinstance(value, int) or isinstance(value, float) else 0
        vr, xr, yr = True, True, True
        if tab.IsTwoDTable():
            tab_xaxis = tab.GetXDistribution()
            tab_yaxis = tab.GetYDistribution()
            if input_way:
                x_size = tab_xaxis.GetSize()
                y_size = tab_yaxis.GetSize()
                value = [[value] * y_size] * x_size
            if yaxis_list:
                yr = tab_yaxis.SetDoublePhysValue(yaxis_list)
        else:
            tab_xaxis = tab.GetDistribution()
            if input_way == 1:
                x_size = tab_xaxis.GetSize()
                value = [value] * x_size
        if xaxis_list:
            xr = tab_xaxis.SetDoublePhysValue(xaxis_list)
        if value != None:
            vr = tab_value.SetDoublePhysValue(value)
        return bool(vr and xr and yr)

    def GetIdxFromAix(self, Axis, Vin):
        Nx = len(Axis)
        Vnew = Vin
        if Vnew <= Axis[0]:
            idx = 0
            Vnew = Axis[0]
        elif Vnew > Axis[Nx - 1]:
            idx = Nx - 2
            Vnew = Axis[Nx - 1]
        else:
            idx = 0
            for i in range(Nx):
                if Vnew > Axis[i]:
                    idx = i
                else:
                    break
        return Vnew, idx

    def get_idx_from_value(self, val_array, vin):
        for i in range(len(val_array) - 1):
            if (val_array[i] <= vin <= val_array[i + 1]) or (val_array[i] >= vin >= val_array[i + 1]):
                return i
        assert False, ' 反查表格时数据超出范围 '

    def lookup_tab(self, tab_name, x_value, y_value=0.0):
        """
        查表函数

        可以查1维或2维表格，利用物理值查表

        tab_name: 表格名称 字符串
        x_value: X轴数值 整数/浮点数
        y_value: Y轴数值（查1维表时不需要） 整数/浮点数
        返回 查表结果 浮点数
        """
        tab = self._getelement_c(tab_name).GetValue()
        if tab.IsOneDTable():
            val_array = tab.GetValue().GetDoublePhysValue()
            x_array = tab.GetDistribution().GetDoublePhysValue()
            x_value, x1 = self.GetIdxFromAix(x_array, x_value)
            x2 = x1 + 1
            ratio_x = (x_value - x_array[x1]) / (x_array[x2] - x_array[x1])
            z_value = val_array[x1] + (val_array[x2] - val_array[x1]) * ratio_x
            return z_value
        elif tab.IsTwoDTable():
            val_matrix = tab.GetValue().GetDoublePhysValue()
            x_array = tab.GetXDistribution().GetDoublePhysValue()
            y_array = tab.GetYDistribution().GetDoublePhysValue()
            x_value, x1 = self.GetIdxFromAix(x_array, x_value)
            x2 = x1 + 1
            y_value, y1 = self.GetIdxFromAix(y_array, y_value)
            y2 = y1 + 1

            ratio_y = (y_value - y_array[y1]) / (y_array[y2] - y_array[y1])
            ratio_x = (x_value - x_array[x1]) / (x_array[x2] - x_array[x1])
            dv_x1 = val_matrix[x1][y2] - val_matrix[x1][y1]
            temp1 = val_matrix[x1][y1] + dv_x1 * ratio_y
            dv_x2 = val_matrix[x2][y2] - val_matrix[x2][y1]
            temp2 = val_matrix[x2][y1] + dv_x2 * ratio_y
            z_value = temp1 + (temp2 - temp1) * ratio_x
            return z_value
        else:
            assert False, '这不是一个表格：' + tab_name

    def inverse_lookup_tab(self, tab_name, value):
        """
        反查表格，只能反查一维表，利用物理值查表

        tab_name: 表格名称 字符串
        value: 数值 整数/浮点数
        返回 查表结果 浮点数
        """
        tab = self._getelement_c(tab_name).GetValue()
        if tab.IsOneDTable():
            val_array = tab.GetValue().GetDoublePhysValue()
            x_array = tab.GetDistribution().GetDoublePhysValue()
            z1 = self.get_idx_from_value(val_array, value)
            z2 = z1 + 1
            ratio_z = (value - val_array[z1]) / (val_array[z2] - val_array[z1])
            x_value = x_array[z1] + (x_array[z2] - x_array[z1]) * ratio_z
            return x_value
        else:
            assert False, '只有一维表才能反查'

    def inverse_lookup_tab_for_temp(self, tab_name, value):
        """反查一维温度常数表"""
        tab = self._getelement_c(tab_name).GetValue()
        if tab.IsOneDTable():
            val_array = tab.GetValue().GetDoublePhysValue()
            x_array = tab.GetDistribution().GetDoublePhysValue()
            val_array_list = list(val_array)
            for i in range(len(val_array_list)):  # 无符号数变有符号数
                if int(round(val_array_list[i])) > 127: val_array_list[i] -= 256
            z1 = self.get_idx_from_value(val_array_list, value)
            z2 = z1 + 1
            ratio_z = (value - val_array_list[z1]) / (val_array_list[z2] - val_array_list[z1])
            x_value = x_array[z1] + (x_array[z2] - x_array[z1]) * ratio_z
            return x_value
        else:
            assert False, '只有一维表才能反查'

    def element_openview(self, *name, findin_RAMCal=False, skip_error=False):
        """
        将变量添加到INCA实验环境

        可以同时传入多个变量名称，且标定量与测量量都可以,如element_openview('MAPHPa','K_VVT_Select','EGRFlow',skip_error=True)

        skip_error不会忽略所有异常，只会跳过如’实验环境找不到变量‘这样的错误，‘系统不支持RamCal功能’这样的异常不会跳过
        name: 变量名称 字符串
        findin_RAMCal: 添加RAMCal变量 布尔值
        skip_error: 跳过错误 布尔值
        """
        if findin_RAMCal:
            for dev_name in self.device:
                if 'RAMCal' in dev_name:
                    ramcal_device = self.device[dev_name]
                    break
            else:
                assert False, '系统不支持RamCal功能'

        for name_temp in name:
            operate_rslt = True
            if findin_RAMCal:
                element = self.exp.GetExperimentElementInDevice(name_temp, ramcal_device)
                if element:
                    operate_rslt = element.OpenView()
            else:
                element = self.exp.GetExperimentElement(name_temp)
                if element:
                    operate_rslt = element.OpenView()

            assert element or skip_error, '找不到该变量:' + name_temp
            assert operate_rslt or skip_error, '添加变量到实验环境时操作失败' + name_temp
            temp = '成功' if operate_rslt and element else '失败 !!!!! '
            print('openview >> "%s" >> %s' % (name_temp, temp))

    def set_element_samplerate(self, *name, samplerate_str='Task10ms', skip_error=False):
        """
        设置测量量的采样率

        skip_error不会忽略所有异常，只会跳过如’实验环境找不到变量‘这样的错误，‘系统不存在该采样率’这样的异常不会跳过
        name: 测量量名称 字符串
        samplerate_str: 采样率名称,如'Task10ms',''Task100ms'' 字符串
        skip_error: 跳过错误 布尔值
        """
        for dev in self.device.values():
            if dev.IsAcquisitionRateAvailable(samplerate_str): break
        else:
            assert False, 'Function set_element_samplerate():系统不存在该采样率：' + samplerate_str
        for name_temp in name:
            var = self.exp.GetExperimentElement(name_temp)
            if var and var.IsMeasureElement():
                rslt = var.GetValue().SetCurrentAcquisitionRate(samplerate_str)
                assert rslt, '设置采样率失败(请先停止测量)：' + name_temp + '>>' + samplerate_str
            else:
                if not skip_error:
                    print(name_temp, '不是测量量')


############################################### 子类 ######################################################
class IncaTestpanelControl(IncaControl, TestCanControl, TestSerialControl):
    def serial_init(self, com, baudrate=38400):
        TestSerialControl.init(self, com, baudrate)

    def inca_init(self):
        IncaControl.init(self)

    def can_init(self, can_channel=0, can_flags=canlib.Open.OVERRIDE_EXCLUSIVE, can_bitrate=canlib.canBITRATE_50K):
        TestCanControl.init(self, can_channel, can_flags, can_bitrate)

    _name_dic = {'MAPHPa': '进气压力', 'AirTemp': '进气温度', 'WaterTemp': '冷却液温度', 'OxygenAD': '前氧',
                 'Oxygen2AD': '后氧', 'PedalPos1000': '踏板1', 'APSPrec': '踏板1', '踏板': '踏板1',
                 'DC_pTankPress': '油箱压力', 'DTNK_pTankPrsFlt': '油箱压力', 'StripPress': '脱附压力',
                 'VehicleSpeed': '车速', 'CarSpeed': '车速', 'EngineSpeed': '转速', 'FilteredRPM': '转速',
                 '水温': '冷却液温度', '油门': '踏板1'}

    valname_dic = _name_dic.copy()
    adname_list = ['增压温度', '燃气温度', '空调温度', '冷却液温度', '减压阀温度', '进气温度', '曲轴通风', 'GPF前温',
                   'GPF后温', '水箱温度', 'CNG泄漏2', 'CNG泄漏1', '后氧', '前氧', '预留T14', '预留T15',
                   '气瓶压力', '预留AO1', '机械TPS', '进气压力', '增压压力', '燃气压力', '踏板2', '踏板1',
                   '预留AO8', '预留AO9', '油箱压力', '减压阀压力', 'GPF压力', '真空压力', '脱附压力', 'EGR阀位置',
                   'CAM-0', 'CAM-1', '转速', '车速']
    digname_list = ['上电', '点火',
                    '离合器顶', '电气负载2', '刹车', '离合', '空调', '空调中压', '油气/再生', '排制/启动',
                    '巡航-', '巡航+', '巡航取消', '巡航开关', '空挡开关', '刹车灯', '电气负载1', '安全气囊']

    _switch_active_dict = {'刹车': 0x01, '离合': 0x02, '刹车灯': 0x04, '空挡开关': 0x08, '电气负载1': 0x10, '电气负载2': 0x20,
                           '排制/启动': 0x40, '油气/再生': 0x80}

    testpanel_ctrlmode = 1  # 1:CAN控制   0:串口控制

    def present_tpl_ctrl_class(self):
        return TestCanControl if self.testpanel_ctrlmode == 1 else TestSerialControl

    def ad_to_voltage(self, ad_8bit):
        return ad_8bit * 5.0 / 255

    def val_to_volt(self, name, value):
        """将INCA监控值转化为电压值或频率信号"""
        if name == '进气压力':
            assert (value < 101.4 or int(round(self.cget_d('K_BoostCtrlEnable')))), '非增压时进气压力应小于101.3kPa'
            mult = self.cget_d('K_MAP_Conv_Mult')
            offset = self.cget_d('K_MAP_Conv_Offset')
            if int(round(offset)) == 0: offset = self.cget_d('K_MAP_Conv_Offset_s16')
            ad = (value * 10 - offset) * 250 / (mult * 4)  # ad(8bit)
            ad = min(ad, self.cget_d('K_MAPHighVFault_Thrd'))
            ad = max(ad, self.cget_d('K_MAPLowVFault_Thrd'))
            return (2.0116 * ad + 1.7664) / 100  # 公式是采集的数据经最小二乘法得到
        elif name == '转速':
            return value
        elif name == '进气温度':
            value = max(value, -40)
            value = min(value, 127)
            ad = self.inverse_lookup_tab_for_temp('i16_MAT_conv_table', value)  # ad(8bit)
            return (2.0221 * ad - 0.3692) / 100
        elif name == '冷却液温度':
            value = max(value, -40)
            value = min(value, 127)
            ad = self.inverse_lookup_tab_for_temp('i16_CTS_conv_table', value)
            return (2.0228 * ad - 0.3363) / 100
        elif name in ['前氧', '后氧']:
            volt_raw = value * 5.27871622
            return (volt_raw * 1.0308 + 11.276) / 1000
        elif name == '踏板1':
            value = max(value, 0)
            value = min(value, 100)
            try:
                idle_ad = self.cget_d('IdleThroPosAD')
            except AssertionError:
                idle_ad = self.mget_d('IdleThroPosAD')
            ad = value * (self.cget_d('K_PedalPosAD_Max') - idle_ad) / 100 + (
                    idle_ad + self.cget_d('K_IdleThroPosAD_Hyst'))  # ad(8bit)
            try:
                ad_max = self.cget_d('K_APSHighVFault_Thrd')
                ad_min = self.cget_d('K_APSLowVFault_Thrd')
            except AssertionError:
                ad_max = self.cget('DFETC_rAPS1HiVoltFailThres_C') * 255 / 100
                ad_min = self.cget('DFETC_rAPS1LoVoltFailThres_C') * 255 / 100
            ad = min(ad, ad_max)
            ad = max(ad, ad_min)
            return (2.0119 * ad + 1.5706) / 100
        elif name == '油箱压力':
            ad = (value + self.cget_d('K_TankPress_Offset')) * 1000 / self.cget_d('K_TankPress_Mult')  # ad(12bit)
            ad = max(ad, self.cget_d('K_TankPressLowVFault_Thrd') * 16 + 16)
            ad = min(ad, self.cget_d('K_TankPressHighVFault_Thrd') * 16 - 16)
            return (1.258 * ad + 2.331) / 1000
        elif name == '脱附压力':
            ad = (1000 * value + self.cget_d('K_Strip_Conv_Offset')) / self.cget_d('K_Strip_Conv_Mult')  # ad(10bit)
            ad = max(ad, self.cget_d('K_StripPressLowVFault_Thrd') * 4 + 4)
            ad = min(ad, self.cget_d('K_StripPressHighVFault_Thrd') * 4 - 4)
            return (0.5027 * ad + 0.9004) / 100
        elif name == '车速':
            assert (int(self.cget_d_int('conSystemConfigID')) & 0x40), '没有装备车速传感器'
            # VSPulseWidth = 3600 * self.cget_d('conCarSpeedFactor') / value  # 单位：μs
            # return (2004.2 / VSPulseWidth) * 500
            try:
                temp = self.cget_d('conCarSpeedFactor')
            except AssertionError:
                try:
                    temp = self.cget_d('SetCarSpeedFactor')
                except AssertionError:
                    temp = self.mget_d('SetCarSpeedFactor')
            return 2004.2 * value * 500 / (3600 * temp)
        else:
            assert False, '目前不支持此变量：' + name

    def val_to_volt_step(self, name, step):
        """步长从物理值转为电压值"""
        if name == '进气压力':
            mult = self.cget_d('K_MAP_Conv_Mult')
            offset = self.cget_d('K_MAP_Conv_Offset')
            if int(round(offset)) == 0: offset = self.cget_d('K_MAP_Conv_Offset_s16')
            admax = (100 * 10 - offset) * 250 / (mult * 4)  # ad(8bit)
            admin = (20 * 10 - offset) * 250 / (mult * 4)
            ad = abs(admax - admin) * step / 80
            return max(0.020116 * ad, 0.01)  # 公式是采集的数据经最小二乘法得到
        elif name == '转速':
            return max(step, 1)
        elif name == '进气温度':
            tab = self._getelement_c('i16_MAT_conv_table').GetValue()
            val_array = tab.GetValue().GetDoublePhysValue()
            x_array = tab.GetDistribution().GetDoublePhysValue()
            val0 = val_array[4]
            val1 = val_array[-3]
            if val0 > 127: val0 -= 256
            if val1 > 127: val1 -= 256
            if val1 != val0:
                ad = step * abs(x_array[-3] - x_array[4]) / abs(val1 - val0)
            else:
                ad = 1
            return max(0.020221 * ad, 0.01)
        elif name == '冷却液温度':
            tab = self._getelement_c('i16_CTS_conv_table').GetValue()
            val_array = tab.GetValue().GetDoublePhysValue()
            x_array = tab.GetDistribution().GetDoublePhysValue()
            val0 = val_array[4]
            val1 = val_array[-3]
            if val0 > 127: val0 -= 256
            if val1 > 127: val1 -= 256
            if val1 != val0:
                ad = step * abs(x_array[-3] - x_array[4]) / abs(val1 - val0)
            else:
                ad = 1
            return max(0.020228 * ad, 0.01)
        elif name in ['前氧', '后氧']:
            voltstep = step * 5.27871622 * 1.0308 / 1000
            return max(voltstep, 0.01)
        elif name == '踏板1':
            try:
                idle_ad = self.cget_d('IdleThroPosAD')
            except AssertionError:
                idle_ad = self.mget_d('IdleThroPosAD')
            pedpos_max = self.cget_d('K_PedalPosAD_Max')
            ad = step * (pedpos_max - idle_ad) / 100
            return max(0.020119 * ad, 0.02)
        elif name == '油箱压力':
            ad = 1000 * step / self.cget_d('K_TankPress_Mult')  # ad(12bit)
            return (0.001258 * ad)
        elif name == '脱附压力':
            ad = 1000 * step / self.cget_d('K_Strip_Conv_Mult')  # ad(10bit)
            return (0.005027 * ad)
        elif name == '车速':
            try:
                temp = self.cget_d('conCarSpeedFactor')
            except AssertionError:
                try:
                    temp = self.cget_d('SetCarSpeedFactor')
                except AssertionError:
                    temp = self.mget_d('SetCarSpeedFactor')
            return 2004.2 * step * 500 / (3600 * temp)
        else:
            assert False, '目前不支持此变量：' + name

    def to(self, name, target, step=0.0, period_ms=0, keep_ms=0, start=None):
        """
        控制测试台模拟信号，参数是电压

        起始值、步长、周期都没有值时,直接改变信号至目标值
        有起始值、步长、周期时,递变至起始值，再从起始值递变至目标值
        如果有步长，周期，但没有传入起始值，则会从当下模拟信号的状态变化到目标值
        步长,周期,保持时间，起始值均有值时,信号波动变化,在最高/低位保持keep_ms
        如 to('进气压力',4.2,0.01,50,start=1.2) 代表进气压力信号以0.01V为步长,50ms为步长周期,递减到1.2V,再递增到4.2V,最后维持在4.2V

        name: 信号名称，详见adname_list列表 字符串
        target: 目标值（电压值） 浮点数/整数
        step: 递增或波动时变化的步长（电压值） 浮点数/整数
        period_ms: 每一步长的步长周期（单位:ms） 浮点数/整数
        keep_ms: 波动变化时在最高/最低点保持的时间（单位:ms） 浮点数/整数
        start: 起始值（电压值） 浮点数/整数
        """
        if self.testpanel_ctrlmode == 1:
            TestCanControl.to(self, name, target, start, step, period_ms, keep_ms)
        else:
            TestSerialControl.to(self, name, target, step, period_ms, keep_ms)

    def toval(self, name, target, step=0.0, period_ms=0, keep_ms=0, start=None):
        """
        以物理值为目标，改变对应的模拟信号

        各参数定义与 to() 函数一致，区别是目标值、起始值、步长的含义是物理值，而非具体的模拟量，如改变'车速'时，100代表100km/h而非100Hz
        该函数并没有覆盖所有的模拟信号，如请求不支持的信号，会产生异常，具体支持的模拟信号详见valname_dic字典
        请求变化踏板时，会同时变化踏板1与踏板2信号，如需只改变其中一个信号，请用 to() 函数
        如 toval('MAPHPa',45,1,500) 代表进气压力以1kPa为步长,500ms为步长周期,逐步变化到45kPa
        使用该函数的缺点是递增/递减时实际步长并不会严格等于给定的步长

        name: 信号名称，详见valname_dic字典,可以是该字典的键或值 字符串
        target: 目标值（物理值） 浮点数/整数
        step: 递增或波动时变化的步长（物理值） 浮点数/整数
        period_ms: 每一步长的步长周期（单位:ms） 浮点数/整数
        keep_ms: 波动变化时在最高/最低点保持的时间（单位:ms） 浮点数/整数
        start: 起始值（物理值） 浮点数/整数
        """
        if name in self._name_dic:
            name = self._name_dic[name]
        volt_target = self.val_to_volt(name, target)

        if start == None:
            volt_start = volt_target  # 信号从当前值递增到目标值
        else:
            volt_start = self.val_to_volt(name, start)

        if step:
            volt_step = self.val_to_volt_step(name, step)
        else:
            volt_step = 0

        if self.testpanel_ctrlmode == 1:
            TestCanControl.to(self, name, volt_target, volt_start, volt_step, period_ms, keep_ms)
            if name == '踏板1':
                TestCanControl.to(self, '踏板2', volt_target / 2, volt_start / 2, volt_step / 2, period_ms, keep_ms)
        else:
            TestSerialControl.to(self, name, volt_target, volt_step, period_ms, keep_ms)
            if name == '踏板1':
                TestSerialControl.to(self, '踏板2', volt_target / 2, volt_step / 2, period_ms, keep_ms)

    def waveval(self, name, val_hi, val_lo, change_time_ms, keep_time_ms):
        """
        以物理值为目标，周期波动模拟信号

        该函数并没有覆盖所有的模拟信号，如请求不支持的信号，会产生异常，具体支持的模拟信号详见valname_dic字典
        波动变化踏板时，会同时变化踏板1与踏板2信号
        如 waveval('进气压力',80,20,1000,500) 代表进气压力以80kPa、20kPa为高/低点进行波动，从80到20/20到80变化的时间是1000ms，并会在高/低点停留500ms
        keep_time_ms不应该等于0，否则函数可能无效

        name: 信号名称，详见valname_dic字典，可以是该字典的键或值 字符串
        val_hi: 周期波动的最高点（物理值） 浮点数/整数
        val_lo: 周期波动的最低点（物理值） 浮点数/整数
        change_time_ms: 高低点之间变化的时间（单位:ms） 浮点数/整数
        keep_time_ms: 在最高/最低点保持的时间（单位:ms） 浮点数/整数
        """
        if name in self._name_dic:
            name = self._name_dic[name]
        ad_hi = self.val_to_volt(name, val_hi)
        ad_lo = self.val_to_volt(name, val_lo)
        self.present_tpl_ctrl_class().wave(self, name, ad_hi, ad_lo, change_time_ms, keep_time_ms)
        if name == '踏板1':
            self.present_tpl_ctrl_class().wave(self, '踏板2', ad_hi / 2, ad_lo / 2, change_time_ms, keep_time_ms)

    def wave(self, ad_name, ad_hi, ad_lo, change_time_ms, keep_time_ms):
        """
        周期波动模拟信号

        如 wave('进气压力',4.2,0.5,1000,500) 代表进气压力以4.2V、0.5V为高/低点进行波动，从4.2到0.5/0.5到4.2变化的时间是1000ms，并会在高/低点停留500ms
        keep_time_ms不应该等于0，否则函数可能无效

        name: 信号名称，详见adname_list列表 字符串
        val_hi: 周期波动的最高点（电压值） 浮点数/整数
        val_lo: 周期波动的最低点（电压值） 浮点数/整数
        change_time_ms: 高低点之间变化的时间（单位:ms） 浮点数/整数
        keep_time_ms: 在最高/最低点保持的时间（单位:ms） 浮点数/整数
        """
        if self.testpanel_ctrlmode == 1:
            TestCanControl.wave(self, ad_name, ad_hi, ad_lo, change_time_ms, keep_time_ms)
        else:
            TestSerialControl.wave(self, ad_name, ad_hi, ad_lo, change_time_ms, keep_time_ms)

    def switch_on(self, *digit_name):
        """
        开启数字信号

        对于某些信号，如刹车、离合等，具体是将电压拉高或拉低取决于K_BrakeSwitch_Active_Level标定情况

        digit_name: 信号名称，详见digname_list列表 字符串
        """
        on_list, off_list = [], []
        for name_temp in digit_name:
            if name_temp in self._switch_active_dict.keys():
                switch_active = int(round(self.cget_d('K_BrakeSwitch_Active_Level')))
                if switch_active & self._switch_active_dict[name_temp]:
                    on_list.append(name_temp)
                else:
                    off_list.append(name_temp)
            else:
                on_list.append(name_temp)
        if on_list:
            self.present_tpl_ctrl_class().switch_on(self, *on_list)
        if off_list:
            self.present_tpl_ctrl_class().switch_off(self, *off_list)

    def switch_off(self, *digit_name):
        """
        关闭数字信号

        对于某些信号，如刹车、离合等，具体是将电压拉高或拉低取决于K_BrakeSwitch_Active_Level标定情况

        digit_name: 信号名称，详见digname_list列表 字符串
        """
        on_list, off_list = [], []
        for name_temp in digit_name:
            if name_temp in self._switch_active_dict.keys():
                switch_active = int(round(self.cget_d('K_BrakeSwitch_Active_Level')))
                if switch_active & self._switch_active_dict[name_temp]:
                    off_list.append(name_temp)
                else:
                    on_list.append(name_temp)
            else:
                off_list.append(name_temp)
        if on_list:
            self.present_tpl_ctrl_class().switch_on(self, *on_list)
        if off_list:
            self.present_tpl_ctrl_class().switch_off(self, *off_list)
