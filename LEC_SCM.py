import _pickle
import sys
import threading
import time
import os
import traceback
import types
import shelve
import keyword
import re
from copy import deepcopy
from collections import OrderedDict
import ctypes
from functools import reduce
from fractions import Fraction
from pprint import pprint
input('input() ...')
print('import wx')
import wx
print('import wx done')
input('input() ...')
print('from wx.stc import StyledTextCtrl')
from wx.stc import StyledTextCtrl
print('from wx.stc import StyledTextCtrl done')
input('input() ...')
print('import wx.stc')
import wx.stc
print('import wx.stc done')
input('input() ...')
print('import _insc')
import _insc
print('import _insc done')
input('input() ...')
print('import numpy')
import numpy
print('import numpy done')
input('input() ...')
print('import wx.html')
import wx.html
print('import wx.html done')
input('input() ...')
print('from random import randint')
from random import randint
print('from random import randint done')
input('input() ...')
print('import asammdf')
import asammdf
print('import asammdf done')
input('input() ...')



SCPTYPE_FOLDER = -1
SCPTYPE_INPUT = 1
SCPTYPE_OUTPUT = 2


# sys.stdout = None


def popuperror(func):
    def myfunc(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AssertionError as e:
            wx.LogError(str(e))
        except:
            wx.LogError(traceback.format_exc())

    return myfunc


class ScriptManage:
    def __init__(self):
        self.state_init()
        sys.path.append(os.path.join(self.cur_state.work_path, '_mypackages'))
        self.app = wx.App(redirect=False)
        # sys.stdout = None
        self.app.SetOutputWindowAttributes('StdError', size=(700, 500))
        self.gui = MainFrame(mainobj=self)  # 主框架
        self.app.SetTopWindow(self.gui)

        try:
            self.database_init()
        except Exception as e:
            wx.LogError('数据库初始化失败 !!\n' + str(e))

        if self.saved_state.script['active']:
            scppath = self.saved_state.script['path']
            self.tree_active(scppath)
            self.gui.left.tree_win.expand_itemFromList(scppath)

        sys.stdout = self.gui.mid.log_win
        sys.stderr = self.gui.mid.log_win
        # self.gui.ShowFullScreen(True, wx.FULLSCREEN_NOCAPTION)
        print('__ welcome __')

    def state_init(self):
        # print('state_init')
        self.cur_state = ScpManageState()
        try:
            with shelve.open(self.cur_state.work_path + r'\_manage_state\state') as stat:
                self.saved_state = stat['saved_state']
        except Exception:
            self.saved_state = ScpManageState()
        self._showst_()
        ...

    def database_init(self):
        # print('database_init()')

        def fun1(idx=0):
            dbname = self.load_anydatabase(idx)
            if dbname:
                # print('>' * 20, 'if dbname: self.database_refresh(dbname)')
                self.database_refresh(dbname)
            else:
                # print('>' * 20, 'if dbname:self.database_refresh()')
                self.database_refresh()
            self.tree_refresh()

        temp = self.saved_state.database
        # print('database_init() >> self.saved_state.database>>', temp)
        if temp:
            try:
                self.load_database(temp)
            except KeyError:
                print('key error')
                fun1()
            except _pickle.UnpicklingError:
                print('_pickle.UnpicklingError')
                fun1(-1)
            else:
                self.database_refresh(temp)
                self.tree_refresh()
        else:
            fun1()

        self._showdb_()
        self._showst_()
        print(self.saved_state.database)

    def save_database(self):
        """保存数据库"""
        # print('save_database()')
        if self.db.name:  # 如果不是空数据库（空数据库的名称是''）
            with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
                database[self.db.name] = self.db

    def load_database(self, dbname):
        """加载数据库"""
        # print('load_database()')
        with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
            self.db = database[dbname]
        self.cur_state.set_database(dbname)

    def load_anydatabase(self, idx=0):
        """加载其中一个数据库，没有的话创建空数据库"""
        # print('load_anydatabase()')
        with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
            key_list = list(database.keys())
            # print('load_anydatabase key_list >>', key_list)
            if key_list:
                rst = key_list[idx]
                self.db = database[rst]
                self.cur_state.set_database(rst)
            else:
                self.db = DataBase('')
                self.cur_state.set_database('')
                rst = ''
        return rst

    def close_manage(self):
        # print('on_close')
        self.refresh_scpCodeConfigDict()
        self.save_database()
        self.save_scpmangestat()

        self._showdb_()

    def database_change(self, dbname):
        """选择脚本库，刷新树窗口"""
        # print('on_choicetree')
        if dbname and dbname != self.cur_state.database:
            self.refresh_scpCodeConfigDict()
            self.save_database()
            self.load_database(dbname)
            self.tree_inactive()
            self.tree_refresh()

        self._showdb_()
        self._showst_()

    def database_refresh(self, cur_dbname=''):
        """数据库刷新"""
        with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
            dbname_list = [key for key in database.keys()]
        self.gui.left.refresh_TreeSelctWin(dbname_list, cur_dbname)

    def database_rename(self):
        """脚本库重命名"""
        # print('database_rename')
        with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
            keylist = list(database.keys())
        if keylist:
            oldname = self.db.name
            newname = wx.GetTextFromUser(' 输入脚本库名称 ', default_value=oldname)
            if newname:
                if newname in keylist:
                    print(' 脚本库名称重复 ')
                else:
                    with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
                        database[newname] = self.db
                        if oldname in keylist: del database[oldname]
                    self.db.name = newname
                    self.cur_state.set_database(newname)
                    self.database_refresh(newname)
        else:
            print(' 请先新增脚本库 ')

        self._showdb_()

    def database_add(self):
        """新增脚本库"""
        # print('database_add')
        dbname = wx.GetTextFromUser(' 输入新脚本库名称 ')
        if dbname:
            with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
                keylist = list(database.keys())
            if dbname in keylist:
                print(' 脚本库名称重复 ')
            else:
                self.refresh_scpCodeConfigDict()
                self.save_database()
                self.db = DataBase(dbname)
                with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
                    database[dbname] = self.db
                self.cur_state.set_database(dbname)
                self.tree_inactive()
                self.database_refresh(dbname)
                self.tree_refresh()

    def database_delete(self):
        """删除脚本库"""
        # print('database_delete')
        dbname = self.db.name
        if not dbname: return
        affirm = wx.MessageBox('确定要删除数据库: %s ?? ' % (dbname), style=wx.YES_NO)
        if affirm == wx.YES:
            self.tree_inactive()
            with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
                del database[dbname]
                keylist = list(database.keys())

            if keylist:
                self.database_refresh(keylist[0])
                self.load_database(keylist[0])
                self.tree_refresh()
            else:  # 没有数据库了
                self.database_refresh()
                self.db = DataBase('')
                self.cur_state.set_database('')
                self.cur_state.init_script()
                self.tree_refresh()

            self.tree_inactive()

            # print(keylist)
        self._showdb_()
        ...

    def _showdb_(self):
        # print('--------------------------- _showdb_ ---------------------------')
        # try:
        #     print(' db.tree_dic >>>', self.db.name, '>>>', self.db.tree_dic)
        #     with shelve.open(self.cur_state.work_path + r'\_database\db') as database:
        #         for key, val in database.items():
        #             print(key, '>>>', val.tree_dic, '\n\t\tconfig_dic key>>>', list(val.config_dic.keys()),
        #                   '\n\t\tcode_dic key>>>', list(val.code_dic.keys()))
        # except:
        #     print('_showdb_ error')
        # print('----------------------------------------------------------------')
        ...

    def _showcf_(self):
        print('-' * 20, '_showcf_', '-' * 20)
        try:
            a = self.db.config_dic[self.cur_state.script['id']]
            print('db.config_dic[id] >>>', a)
            for key, val in a.items(): print('\t%s : %s' % (key, val.__dict__))
        except:
            print('_showcf_ error', str(sys.exc_info()))
        print('-' * 50)
        ...

    def _showst_(self):
        # print('-' * 20, '_showst_', '-' * 20)
        # try:
        #     a = self.cur_state
        #     print('cur_state.database >>>', a.database)
        #     print('cur_state.script >>>', a.script)
        # except:
        #     print('_showst_ error')
        # print('-' * 50)
        ...

    def inputScpRun(self):
        """运行工况输入脚本"""

        def coderun(func):
            def func0(ins, evt, exit):
                try:
                    func(ins, evt, exit)
                except Exception as e:
                    exit()
                    raise e

            return func0

        scp = self.cur_state.script
        if scp['active'] and scp['type'] == SCPTYPE_INPUT:
            print('-' * 20, '输入脚本"%s"运行' % scp['name'], '-' * 20)

            self.gui.right.bt_ipscpstop.Enable()
            ins = _insc.IncaTestpanelControl()
            ctrlmode = self.cur_state.swconfig['testPanelCtrlMode']
            if ctrlmode == 1:
                ins.can_init()
            elif ctrlmode == 0:
                ins.serial_init(self.cur_state.swconfig['serialCOM'])
            ins.inca_init()

            code = self.getcode_fromid(self.cur_state.script['id'])
            evt = self.get_inputScpStatObj()

            # codeRun(code, ins, evt)
            mod = types.ModuleType('inputscpmod')
            exec(code, mod.__dict__)

            mod.init(ins, evt)
            ins.all_reset_read()

            th = InpuScpRunThread(self, daemon=True)
            self.ipscprun_thread = th
            runfunc = coderun(mod.run)
            th.initfunc(runfunc, ins, evt, cycle=evt.functioncycle, cycleperiod=evt.functioncycleperiod)
            th.start()

    def outputScpRun(self, filename):
        """输出校验脚本运行"""
        scp = self.cur_state.script
        if scp['active'] and scp['type'] == SCPTYPE_OUTPUT:
            configobj = self.db.config_dic[scp['id']]['default']
            dir = configobj.loaddir
            if dir:
                print('-' * 20, '校验脚本"%s"运行' % scp['name'], '-' * 20)
                loadpath = os.path.join(dir, filename)
                print('    loadpath', loadpath)
                basename, suffix = os.path.splitext(filename)

                if suffix == '.dat' or suffix == '.mdf':
                    filetype = 'mdf'
                else:
                    filetype = 'ascii'

                if configobj.mdfperiodmode == 1:
                    resampprd = configobj.mdfcustomperiod
                    assert resampprd and (
                            isinstance(resampprd, float) or isinstance(resampprd, int)), '采样周期不正确"%s"' % resampprd
                else:
                    resampprd = 0

                i = 1
                if filetype == 'ascii':
                    savepath = os.path.join(dir, '%s_p%s' % (basename, suffix))
                    while os.path.exists(savepath):  # 文件名重复时
                        savepath = os.path.join(dir, '%s_p_%d%s' % (basename, i, suffix))
                        i += 1
                    print('    savepath', savepath)
                else:
                    savepath = os.path.join(dir, '%s_p%s' % (basename, '.mdf'))
                    savepath2 = os.path.join(dir, '%s_p%s' % (basename, '.dat'))
                    while os.path.exists(savepath) or os.path.exists(savepath2):  # 文件名重复时
                        savepath = os.path.join(dir, '%s_p_%d%s' % (basename, i, '.mdf'))
                        savepath2 = os.path.join(dir, '%s_p_%d%s' % (basename, i, '.dat'))
                        i += 1
                    print('    savepath', savepath2)
                assert os.path.exists(loadpath), '%s 文件不存在' % loadpath

                code = self.getcode_fromid(scp['id'])

                mod = types.ModuleType('outputscpmod')
                exec(code, mod.__dict__)

                funcdic = {key: val for key, val in mod.__dict__.items() if isinstance(val, types.FunctionType)}
                funcinit, funccalc, funcname = None, None, None
                for name, func in funcdic.items():
                    if name.endswith('_name_'):
                        funcname = func
                    elif name.endswith('_init_'):
                        funcinit = func
                    elif name.endswith('_calc_'):
                        funccalc = func

                try:
                    scprun = OutputScpRun(funcinit, funccalc, funcname,
                                          device_name='CCP: 1', getcali_mode=2, datafiletype=filetype,
                                          mdf_period=configobj.mdfsysperiod, mdf_resampleraster=resampprd)
                    scprun.run(loadpath, savepath)
                except Exception as e:
                    self.gui.right.refresh_opFileListWin(dir)
                    self.gui.right.bt['运行脚本'].Enable()
                    print('-' * 20, '校验脚本"%s"结束' % scp['name'], '-' * 20)
                    raise e
                else:
                    self.gui.right.refresh_opFileListWin(dir)
                    self.gui.right.bt['运行脚本'].Enable()
                    print('-' * 20, '校验脚本"%s"结束' % scp['name'], '-' * 20)

    def save_scpmangestat(self):
        """保存软件状态"""
        # print('save_scpmangestat')
        with shelve.open(self.cur_state.work_path + r'\_manage_state\state') as stat:
            stat['saved_state'] = self.cur_state

    def refresh_scpCodeConfigDict(self):
        """检查 code_dict 与 config_dict 中是否有冗余的项目，有的话删除"""
        id_list = self.getidlist_fromdic(self.db.tree_dic)

        id_list_config = [id for id in self.db.config_dic if id not in id_list]
        id_list_code = [id for id in self.db.code_dic if id not in id_list]

        for id in id_list_config: del self.db.config_dic[id]
        for id in id_list_code: del self.db.code_dic[id]
        self._showdb_()
        self._showcf_()

    def getidlist_fromdic(self, dic):
        """得到某字典内包含的所有脚本ID"""

        def get_idlist_fromdic_cycle(dic, id_list):
            for val in dic.values():
                if isinstance(val, dict):
                    get_idlist_fromdic_cycle(val, id_list)
                else:
                    id_list.append(val[1])

        id_list = []
        get_idlist_fromdic_cycle(dic, id_list)
        return id_list

    def getdict_fromItemList(self, item_list):
        """通过各级字典的键列表得到最终的子字典与键值"""
        tempdic = self.db.tree_dic
        path0 = item_list[:-1]
        name = item_list[-1]
        for item in path0:
            tempdic = tempdic[item]
        return tempdic, name

    def tree_refresh(self):
        self.gui.left.tree_win.refresh_all_from_dict(self.db.tree_dic)
        if self.cur_state.script['active']:
            scppath = self.cur_state.script['path']
            self.gui.left.tree_win.expand_itemFromList(scppath, select=False)

    def tree_inactive(self):
        """脚本未激活"""
        self.gui.mid.refresh_codewin()
        if self.cur_state.script['type'] == SCPTYPE_INPUT:
            self.gui.right.refresh_inputscp()
            self.gui.right.refresh_iploadConfigWin()
        elif self.cur_state.script['type'] == SCPTYPE_OUTPUT:
            self.gui.right.cfwin_dirtext.SetLabel('')
            self.gui.right.refresh_opFileListWin()
            self.gui.right.refresh_opPrd()
            self.gui.right.disable_opPrd()
        self.gui.right.cfwin_text.SetLabel('')
        for button in self.gui.right.bt.values(): button.Disable()

        self.cur_state.init_script()

        self._showst_()

    def tree_active(self, item_list):
        """激活脚本"""
        # print('tree_active()')
        self._showdb_()
        self._showst_()
        tempdic, name = self.getdict_fromItemList(item_list)
        scptype, scpid, _ = tempdic[name]
        scp = self.cur_state.script

        if scpid != scp['id'] or scp['active'] == False:  # 激活了另一个项目 or 从未激活状态到激活状态

            self.gui.mid.refresh_codewin(self.getcode_fromid(scpid))
            rightpl = self.gui.right

            if scptype == SCPTYPE_INPUT:
                if scp['type'] != SCPTYPE_INPUT:
                    rightpl.DestroyChildren()
                    rightpl.inputConfigWin_init()
                rightpl.cfwin_text.SetLabel(name)
                cfdic = self.db.config_dic[scpid]
                if cfdic:  # 如果不是空字典，即拥有配置，则加载其中一个配置
                    if 'default' in list(cfdic.keys()):
                        cfname, configobj = 'default', cfdic['default']
                    else:
                        cfname, configobj = list(cfdic.items())[-1]
                    self.cur_state.set_script(config=cfname)
                    rightpl.refresh_inputscp(configobj)
                    name_list = list(self.db.config_dic[scpid].keys())
                    rightpl.refresh_iploadConfigWin(name_list, cfname)
                else:
                    rightpl.refresh_inputscp()
                    rightpl.refresh_iploadConfigWin()
                    self.cur_state.set_script(config=None)

            elif scptype == SCPTYPE_OUTPUT:
                if scp['type'] != SCPTYPE_OUTPUT:
                    rightpl.DestroyChildren()
                    rightpl.outputConfigWin_init()
                    rightpl.enable_opPrd()
                rightpl.cfwin_text.SetLabel(name)
                rightpl.cfwin_dirtext.SetLabel('')
                rightpl.refresh_opFileListWin()
                self.cur_state.set_script(config='default')
                configobj = self.db.config_dic[scpid]['default']
                rightpl.refresh_opPrd(configobj)
                defaultdir = configobj.loaddir
                if defaultdir:
                    self.output_chgLoadDir(defaultdir, scpid)
                else:
                    defaultdir = self.cur_state.opscppath
                    if defaultdir:
                        self.output_chgLoadDir(defaultdir, scpid)

            for button in rightpl.bt.values(): button.Enable()
            self.cur_state.set_script(active=True, name=name, id=scpid, type=scptype, path=item_list)

        self._showcf_()
        self._showst_()

    def tree_delete(self):
        """删除树窗口项目及数据库对应字典项目"""
        # print('tree_delete')
        affirm = wx.MessageBox('确定要删除 ?? ', style=wx.YES_NO)
        if affirm == wx.YES:
            paths = []
            for path in self.gui.left.tree_win.delete():
                tempdic = self.db.tree_dic
                path0 = path[:-1]
                target_name = path[-1]
                if path0:
                    for item in path0:
                        try:
                            temp = tempdic.__getitem__(item)
                            tempdic = temp
                        except KeyError:  # 项目被删去后，会导致删除其子项目时报错
                            break
                    else:
                        temp.__delitem__(target_name)
                else:
                    tempdic.__delitem__(target_name)

                paths.append(path)

            if self.cur_state.script['active']:
                activatedpath = self.cur_state.script['path']
                for path in paths:
                    if activatedpath[:len(path)] == path:  # 删除项目包含或等于激活的脚本时，初始化激活脚本
                        self.tree_inactive()
                        break

        self._showdb_()
        self._showst_()

    def tree_add(self, scptype):
        """添加脚本或文件夹"""

        # print('tree_add()')

        def _add(text, id, path):
            inform = (scptype, id, [None])
            newitem_path, newitem = self.gui.left.tree_win.additem(text, inform)
            i = 1
            while self.gui.left.tree_win.judge_redund(newitem):  # 有重复项时会重命名
                newtext = text + '_' + str(i)
                self.gui.left.tree_win.SetItemText(newitem, newtext)
                newitem_path[-1] = newtext
                i += 1

            tempdic = self.db.tree_dic
            path0 = newitem_path[:-1]
            target_name = newitem_path[-1]

            # print(newitem_path)
            # print(self.db.tree_dic)

            for item in path0:
                tempdic = tempdic[item]

            if scptype == SCPTYPE_FOLDER:
                tempdic[target_name] = {}  # 修改字典-添加脚本
            else:
                try:
                    code = self.getcode_frompath(path)
                except UnicodeDecodeError as e:
                    self.gui.left.tree_win.Delete(newitem)
                    time.sleep(0.01)
                    print(text, '编码错误,只接受"utf-8"编码', file=sys.stderr)
                    return
                except Exception as e:
                    print('-' * 20, '"%s" 导入代码时错误!!' % text, str(e), '-' * 20, sep='\n', file=sys.stderr)
                    return
                self.db.code_dic[id] = code
                self.db.config_dic[id] = {}
                tempdic[target_name] = inform  # 修改字典-添加脚本
                if scptype == SCPTYPE_OUTPUT:
                    self.db.config_dic[id]['default'] = OutputConfig()

        if scptype == SCPTYPE_FOLDER:
            text = path = wx.GetTextFromUser(' 输入文件夹名称 ')  # ,parent=self.gui)
            if text:
                id = -1
                _add(text, id, path)
        else:
            with wx.FileDialog(None, '选择脚本', style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fd:
                if fd.ShowModal() == wx.ID_CANCEL:
                    return
                paths = fd.GetPaths()
            if not paths:
                return
            for path in paths:
                text = os.path.basename(path)
                text = os.path.splitext(text)[0]
                id = int(time.time() * 1000000) * 1000 + randint(0, 1000)
                _add(text, id, path)
                time.sleep(0.0001)

        self._showdb_()
        self._showcf_()
        self._showst_()

    def tree_addtopfolder(self):
        # print('tree_addtopfolder')
        text = wx.GetTextFromUser(' 输入文件夹名称 ')
        if text:
            inform = (-1, -1, [None])
            newitem = self.gui.left.tree_win.addtopfolder(text, inform)

            newtext = text
            i = 1
            while self.gui.left.tree_win.judge_redund(newitem):  # 有重复项时会重命名
                newtext = text + '_' + str(i)
                self.gui.left.tree_win.SetItemText(newitem, newtext)
                i += 1
            if not newtext in list(self.db.tree_dic.keys()):
                self.db.tree_dic[newtext] = {}
            else:
                self.tree_refresh()
                assert False, '%d 已经存在该文件夹' % newtext

            self._showdb_()

    def tree_rename(self, item_list, newname):
        # print('tree_rename')

        tempdic, oldname = self.getdict_fromItemList(item_list)

        if newname in list(tempdic.keys()): return
        tempdic[newname] = tempdic[oldname]
        del tempdic[oldname]

        if self.cur_state.script['active']:
            activatedpath = self.cur_state.script['path']
            if activatedpath[:len(item_list)] == item_list:  # 改名项目包含或等于激活的脚本时
                self.tree_inactive()
        self._showst_()

    def tree_adddemoscp(self, scptype):
        """导入空脚本"""
        text = path = wx.GetTextFromUser(' 脚本名称: ')
        if text:
            id = int(time.time() * 1000000) * 1000 + randint(0, 1000)
            inform = (scptype, id, [None])
            newitem_path, newitem = self.gui.left.tree_win.additem(text, inform)
            i = 1
            while self.gui.left.tree_win.judge_redund(newitem):  # 有重复项时会重命名
                newtext = text + '_' + str(i)
                self.gui.left.tree_win.SetItemText(newitem, newtext)
                newitem_path[-1] = newtext
                i += 1

            tempdic = self.db.tree_dic
            path0 = newitem_path[:-1]
            target_name = newitem_path[-1]

            for item in path0:
                tempdic = tempdic[item]

            code = {SCPTYPE_INPUT: SCPCODE_INPUT, SCPTYPE_OUTPUT: SCPCODE_OUTPUT}[scptype]
            self.db.code_dic[id] = code
            self.db.config_dic[id] = {}
            tempdic[target_name] = inform  # 修改字典-添加脚本
            if scptype == SCPTYPE_OUTPUT:
                self.db.config_dic[id]['default'] = OutputConfig()

    def getcode_frompath(self, path):
        with open(path, 'rb') as f:
            code = f.read()
        if b'\x00' in code: code = code.replace(b'\x00', b'')
        code = code.decode('utf-8', errors='replace')
        return code

    def getcode_fromid(self, id):
        return self.db.code_dic[id]

    def get_inputScpStatObj(self):
        scp = self.cur_state.script
        evt = InputScpRunState()
        if scp['config']:
            configobj = self.db.config_dic[scp['id']][scp['config']]
            key_set = {key for key in configobj.__dict__.keys()}
            key_set = key_set - {'__doc__'}
            for key in key_set:
                evt.__setattr__(key, configobj.__dict__[key][0])
        return evt

    def ipconfig_add(self, config_name, fromdic=False, config_dic=None, doc=''):
        """新增配置，并刷新配置界面"""
        config_name = config_name.strip()
        if not config_name: config_name = 'default'
        scp = self.cur_state.script
        if config_name and scp['active']:
            tempname = config_name
            id = scp['id']
            names = list(self.db.config_dic[id].keys())
            i = 1
            while tempname in names:  # 与其它配置重名时
                tempname = config_name + '_' + str(i)
                i += 1

            if fromdic:
                configobj = InputConfig()
                for key, val in config_dic.items():
                    configobj.__setattr__(key, val)
                    for name in names:  # 从文件导入时，会在其它配置同步添加数据
                        tempobj = self.db.config_dic[id][name]
                        if not key in tempobj.__dict__.keys():
                            tempobj.__setattr__(key, val)
                if doc:
                    configobj.__doc__ = doc
                    for name in names:
                        tempobj = self.db.config_dic[id][name]
                        if not '__doc__' in tempobj.__dict__.keys():
                            tempobj.__doc__ = doc
            else:
                if names:  # 复制当前配置
                    cur_configobj = self.db.config_dic[id][scp['config']]
                    configobj = deepcopy(cur_configobj)
                else:  # 没有其它配置时，生成空配置
                    configobj = InputConfig()
            self.db.config_dic[id][tempname] = configobj
            self.gui.right.refresh_inputscp(configobj)
            names.append(tempname)
            self.gui.right.refresh_iploadConfigWin(names, tempname)
            self.cur_state.set_script(config=tempname)

        self._showcf_()
        self._showst_()

    def ipconfig_additem(self, param: str, value, unit='-', notes=''):
        """在输入脚本配置页新增配置参数"""
        scp = self.cur_state.script
        if scp['active'] and param:
            id = scp['id']
            config = scp['config']
            if config:
                assert (param[0].isalpha() or param[0] == '_'), '参数应该以字符开头'
                if unit == 'bool': value = bool(value)
                if param in list(self.db.config_dic[id][config].__dict__.keys()):  # 当前界面已经有了要新增的数据
                    obj = self.db.config_dic[id][config]
                    setattr(obj, param, [value, unit, notes, None])
                    self.gui.right.refresh_inputscp(obj)
                else:
                    if unit == 'bool':
                        self.gui.right.add_ipCfCheckItem(param, value)
                    else:
                        self.gui.right.add_ipCfListItem(param, value, unit)
                    for cfobj in self.db.config_dic[id].values():  # 每一个配置对象都同步增加属性
                        setattr(cfobj, param, [value, unit, notes, None])
            else:
                print('添加配置数据前应该先创建配置文件')
        self._showst_()

    # noinspection PyTypeChecker
    def ipconfig_savetofile(self):
        """把配置导出到文件"""
        # print('ipconfig_savetofile()')
        self._showcf_()
        self._showst_()
        scp = self.cur_state.script
        if scp['active'] and scp['config']:
            while True:
                path = wx.SaveFileSelector('', 'txt文本(*.txt)|*.txt|csv文件(*.csv)|*.csv', scp['config'] + '.txt')
                if path and os.path.exists(path):
                    affirm = wx.MessageBox('名称重复,确认要覆盖"%s"吗 ?? ' % os.path.basename(path), style=wx.YES_NO)
                    if affirm == wx.YES:
                        break
                else:
                    break

            if path:
                cfobj = self.db.config_dic[scp['id']][scp['config']]
                text = "'''\n%s'''\n" % cfobj.__doc__
                paramlist = [x for x in cfobj.__dict__.keys() if not x.startswith('__')]
                textlist = []
                for name in paramlist:
                    inform = cfobj.__dict__[name]
                    inform = inform[:3]
                    inform[0] = str(inform[0])
                    line = name + '\t' + '\t'.join(inform)
                    textlist.append(line)
                text += '\n'.join(textlist)
                # print(text)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)

    def ipconfig_change(self, configname):
        """更改工况输入脚本配置选项"""
        if self.cur_state.script['active']:
            obj = self.db.config_dic[self.cur_state.script['id']][configname]
            self.gui.right.refresh_inputscp(obj)
            self.cur_state.set_script(config=configname)
        self._showst_()

    def ipconfig_moditem(self, name, value):
        """修改工况输入脚本当前配置的其中一项数据"""
        self._showst_()
        scp = self.cur_state.script
        config = scp['config']
        if scp['active'] and config:
            obj = self.db.config_dic[scp['id']][config]
            cfitem_list = obj.__getattribute__(name)
            print(config, '>>', name, cfitem_list)
            cfitem_list[0] = value
        self._showcf_()
        self._showst_()

    def ipconfig_delete(self):
        self._showcf_()
        scp = self.cur_state.script
        config = scp['config']
        if scp['active'] and config:
            dic = self.db.config_dic[scp['id']]
            dic.pop(config)
            config_list = list(dic.keys())
            if config_list:
                newconfig = config_list[-1]
                self.gui.right.refresh_inputscp(dic[newconfig])
                self.gui.right.refresh_iploadConfigWin(config_list, newconfig)
                self.cur_state.set_script(config=newconfig)
            else:
                self.gui.right.refresh_inputscp()
                self.gui.right.refresh_iploadConfigWin()
                self.cur_state.set_script(config=None)
        self._showcf_()
        self._showst_()

    def ipconfig_delitem(self, itemtype='param', itemid=0, itemname=''):
        scp = self.cur_state.script
        config = scp['config']
        if scp['active'] and config:
            if itemtype == 'param':
                self.gui.right.delete_ipCfListSelectItem(itemid)
            elif itemtype == 'bool':
                self.gui.right.delete_ipCfCheckSelectItem(itemid)
            obj = self.db.config_dic[scp['id']][config]
            obj.__delattr__(itemname)
        self._showst_()
        self._showcf_()

    def ipconfig_showItemNotes(self, name):
        """显示配置数据的备注"""
        scp = self.cur_state.script
        config = scp['config']
        if scp['active'] and config:
            notes = self.db.config_dic[scp['id']][config].__getattribute__(name)[2]
            print('%s >> %s' % (name, notes))

    def ipconfig_showDoc(self):
        """显示配置说明"""
        scp = self.cur_state.script
        config = scp['config']
        if scp['active'] and config:
            doc = self.db.config_dic[scp['id']][config].__doc__
            print('%s 配置说明:\n"%s"\n' % (config, doc))

    def ipconfig_moddoc(self, text):
        """修改配置对象的文档字符串"""
        # print('ipconfig_moddoc()')
        scp = self.cur_state.script
        config = scp['config']
        if scp['active'] and config:
            for obj in self.db.config_dic[scp['id']].values():
                obj.__doc__ = text
        self._showdb_()
        self._showcf_()

    def ipconfig_moddoc0(self):
        # print('ipconfig_moddoc0()')
        scp = self.cur_state.script
        config = scp['config']
        if scp['active'] and config:
            obj = self.db.config_dic[scp['id']][config]
            doc = obj.__dict__.get('__doc__', '')
            ModInputScpCfDoc(parent=self.gui, mainobj=self, text=doc)
        self._showdb_()
        self._showcf_()

    def output_chgLoadDir(self, dirpath, scpid=None):
        """输出校验脚本选择导入文件夹"""
        if os.path.exists(dirpath):
            self.gui.right.cfwin_dirtext.SetLabel(dirpath)
            self.gui.right.refresh_opFileListWin(dirpath)
            scpid = scpid if scpid else self.cur_state.script['id']
            cfobj = self.db.config_dic[scpid]['default']
            cfobj.loaddir = dirpath
            self.cur_state.opscppath = dirpath
        else:
            self.gui.right.cfwin_dirtext.SetLabel('')
            self.gui.right.refresh_opFileListWin()
            scpid = scpid if scpid else self.cur_state.script['id']
            cfobj = self.db.config_dic[scpid]['default']
            cfobj.loaddir = ''
            self.cur_state.opscppath = ''

    def opconfig_setitem(self, **kwargs):  # item : value, item : value,...
        scp = self.cur_state.script
        if scp['active'] and scp['config'] and kwargs:
            obj = self.db.config_dic[scp['id']][scp['config']]
            for item, value in kwargs.items():
                setattr(obj, item, value)
        self._showcf_()

    def _get_paramlist(self, text):
        """通过用户输入的文本返回变量列表"""
        paramlist = text.split('\n')
        paramlist = [text.strip() for text in paramlist]  # 去掉变量2边的空格
        paramlist = [text for text in paramlist if text]  # 去掉空字符串
        return paramlist

    @popuperror
    def import_incaParam(self, text, samplerate_str, findin_RAMCal, skip_error):
        paramlist = self._get_paramlist(text)
        paramlist = list(set(paramlist))  # 去重复
        paramlist.sort()
        if paramlist:
            ins = _insc.IncaControl()
            ins.init()
            ins.element_openview(*paramlist, findin_RAMCal=findin_RAMCal, skip_error=skip_error)
            ins.set_element_samplerate(*paramlist, samplerate_str=samplerate_str, skip_error=skip_error)

    def code_save(self, code):
        scp = self.cur_state.script
        if scp['active']:
            self.db.code_dic[scp['id']] = code
            print('------- 成功保存代码 -------')

    def analyse_incaParam(self, text, dev='CCP: 1'):
        """归纳、分析INCA变量的信息，并输出HTML"""

        def getaccu_fromgain(gain):
            if gain == 0:
                accu = 'error'
            elif round(gain, 8) == int(gain):
                accu = '1/%d' % (int(gain))
            elif round(1 / gain, 8) == int(1 / gain):
                accu = str(int(1 / gain))
            else:
                accu = str(round(1 / gain, 8))
            return accu

        def geta2ldata_fromcompu(compu):
            conver = compu.GetConversionType()
            if conver == 'Linear':
                c, b = compu.GetParameterValues()
                if c == 0:
                    accu = getaccu_fromgain(b)
                else:
                    accu = 'imp = phy*{0}+{1}'.format(b, c)
            elif conver == 'Identity':
                accu = '1'
            elif conver == 'TAB_VERB':
                accu = '枚举'
            elif conver == 'Moebius':
                a, b, c, d, e, f = compu.FormulaCoefficients()
                if a == 0 and b != 0 and c == 0 and d == 0 and e == 0 and f != 0:
                    gain = b / f
                    accu = getaccu_fromgain(gain)
                else:
                    accu = 'imp=({0}*phy^2+{1}*phy+{2})/({3}*phy^2+{4}*pyh+{5})'.format(a, b, c, d, e, f)
            else:
                accu = 'error'
            unit = compu.GetUnit()
            return unit, accu

        def geta2ldata(elema2l):
            compu = elema2l.GetCompuMethod()
            unit, accu = geta2ldata_fromcompu(compu)
            lobound = str(elema2l.GetLowerBound())
            hibound = str(elema2l.GetUpperBound())
            addr = elema2l.GetAddressAsHexString()
            type = elema2l.GetDataType()
            comment = elema2l.GetComment()
            return unit, lobound, hibound, accu, addr, type, comment

        templist = self._get_paramlist(text)
        paramlist = []
        for x in templist:
            if (not x in paramlist): paramlist.append(x)
        if paramlist:
            ins = _insc.IncaControl()
            ins.init()
            assert dev in ins.device.keys(), 'INCA当前实验环境不支持数据源:"%s"' % dev
            ins.a2l_init(dev)
            data = {}

            data['nowdevice'] = dev
            data['device'] = tuple(ins.device.keys())
            assert dev in data['device'], '不存在的源数据集:"%s"' % dev
            data['a2l'] = ins.a2l.GetDescriptionFileName()

            ctup = ins.a2l.GetAllElementNamesOfType('allCharacteristics')
            mtup = ins.a2l.GetAllElementNamesOfType('allMeasurements')
            atup = ins.a2l.GetAllElementNamesOfType('allAxisPoints')

            data['found'] = found = []  # 找到的变量
            data['foundcs'] = foundcs = []  # 找到的单参标定量
            data['foundco'] = foundco = []  # 找到的一维表
            data['foundct'] = foundct = []  # 找到的二维表
            data['foundm'] = foundm = []  # 找到的测量量
            data['founda'] = founda = []  # 找到的轴
            data['nofound'] = nofound = []  # 没找到
            data['nosure'] = nosure = []  # 不确定类型的变量
            data['caliable'] = caliable = []  # 可标的
            data['calidisable'] = calidisable = []  # 不可标的
            data['inform'] = {}  # name : datatuple
            # (单位,下限,上限,精度,地址,数据类型,备注)
            data['value'] = {}  # 包含各标定量的值，类型有浮点数、列表、嵌套元组

            for name in paramlist:
                try:
                    print('find', name)
                    if name in ctup:
                        elem = ins.exp.GetExperimentElementInDevice(name, ins.device[dev])
                        elema2l = ins.a2l.GetCharacteristicNamed(name)
                        elemval = elem.GetValue()
                        compu = elema2l.GetCompuMethod()
                        if elem.IsScalar():  # 单参标定量
                            temp = geta2ldata(elema2l)
                            value = elemval.GetDoublePhysValue()

                            if elemval.IsWriteProtected():
                                calidisable.append(name)
                            else:
                                caliable.append(name)

                            data['inform'][name] = temp
                            data['value'][name] = value
                            found.append(name)
                            foundcs.append(name)
                        elif elem.IsOneDTable():  # 一维表
                            temp = geta2ldata(elema2l)
                            value = (elemval.GetValue().GetDoublePhysValue(),
                                     elemval.GetDistribution().GetDoublePhysValue())

                            if elemval.GetValue().IsWriteProtected():
                                calidisable.append(name)
                            else:
                                caliable.append(name)

                            data['inform'][name] = temp
                            data['value'][name] = value
                            found.append(name)
                            foundco.append(name)
                        elif elem.IsTwoDTable():  # 二维表
                            temp = geta2ldata(elema2l)
                            value = (elemval.GetValue().GetDoublePhysValue(),
                                     elemval.GetXDistribution().GetDoublePhysValue(),
                                     elemval.GetYDistribution().GetDoublePhysValue())

                            if elemval.GetValue().IsWriteProtected():
                                calidisable.append(name)
                            else:
                                caliable.append(name)

                            data['inform'][name] = temp
                            data['value'][name] = value
                            found.append(name)
                            foundct.append(name)
                        else:
                            nosure.append(name)
                            ...
                    elif name in mtup:  # 测量量
                        elema2l = ins.a2l.GetMeasurementNamed(name)
                        temp = geta2ldata(elema2l)

                        data['inform'][name] = temp
                        found.append(name)
                        foundm.append(name)
                    elif name in atup:  # 轴
                        elema2l = ins.a2l.GetAxisPointNamed(name)
                        elemval = ins.exp.GetExperimentElementInDevice(name, ins.device[dev]).GetValue()

                        temp = geta2ldata(elema2l)
                        value = elemval.GetDoublePhysValue()

                        if elemval.IsWriteProtected():
                            calidisable.append(name)
                        else:
                            caliable.append(name)

                        data['inform'][name] = temp
                        data['value'][name] = value
                        found.append(name)
                        founda.append(name)
                    else:
                        nofound.append(name)
                except Exception as e:
                    nosure.append(name)
                    raise e

            myhtml = self.get_htmlFromIncaInform(data)
            # with open(r'TEMP\demo.html', 'w', encoding='utf-8') as f:
            #     f.write(myhtml)
            self.gui.showhtml(myhtml)
            print('analyse done')

    def get_htmlFromIncaInform(self, data):
        def htmllist(myiter, ref=False):
            if myiter:
                temp = '<ol>\n'
                for x in myiter:
                    if ref:
                        temp += '<li><a href="#{0}">{0}</a></li>\n'.format(x)
                    else:
                        temp += '<li>{0}</li>\n'.format(x)
                temp += '</ol>\n'
            else:
                temp = "无"
            return temp

        def htmltabrow(myiter, th=False):
            temp = '<tr>\n'
            for x in myiter:
                if th:
                    temp += '<th>{0!s}</th>\n'.format(x)
                else:
                    temp += '<td>{0!s}</td>\n'.format(x)
            temp += '</tr>\n'
            return temp

        parag = OrderedDict()
        parag['overview'] = HTML_IncaInform_Overview.format(data=data, allnum=len(data['found']),
                                                            errnum=len(data['nofound']) + len(data['nosure']))

        parag['error'] = HTML_IncaInform_Error.format(htmllist(sorted(data['nofound'])),
                                                      htmllist(sorted(data['nosure'])))

        if data['inform']:
            informlist = []
            for i, key in enumerate(data['found']):
                x = data['inform'][key]
                ran = '{0!s}-{1!s}'.format(x[1], x[2])
                bgcolor = '#B4EEB4' if i % 2 == 0 else '#F5F5F5'
                informlist.append("""<tr style="background-color:{bgcolor}">
                <td><a name="{key}"><b>{key}</b></a></td>
                <td>{x[0]}</td>
                <td>{ran}</td>
                <td>{x[3]}</td>
                <td>{x[4]}</td>
                <td>{x[5]}</td>
                </tr>
                <tr style="background-color:{bgcolor}">
                <td colspan="6">{x[6]}</td>
                </tr>
                """.format(key=key, x=x, ran=ran, bgcolor=bgcolor))
            informstr = '\n'.join(informlist)
        else:
            informstr = ''
        parag['inform'] = HTML_IncaInform_Inform.format(informstr)

        if data['found']:
            valuelist = []
            for name in data['found']:
                if name in data['foundcs']:  # 单参标定量
                    val = data['value'][name]
                    valuelist.append('<li><b>{0}</b></li>\n{1!s}'.format(name, val))
                elif name in data['foundco']:  # 一维表
                    val = data['value'][name]
                    valuelist.append("""<li><b>{0}</b></li>
                    <table border="1" cellpadding="2" cellspacing="0">
                    {1}
                    {2}
                    </table>
                    """.format(name, htmltabrow(val[1]), htmltabrow(val[0])))
                elif name in data['foundct']:  # 二维表
                    val = data['value'][name]
                    tabstr = htmltabrow(('y|x',) + val[1])
                    temptuple = (val[2],) + val[0]  # 添加Y轴
                    tempmatrix = numpy.array(temptuple)
                    for row in tempmatrix.T:  # 转置
                        tabstr += htmltabrow(row)
                    valuelist.append("""<li><b>{0}</b></li>
                    <table border="1" cellpadding="2" cellspacing="0">
                    {1}
                    </table>\n""".format(name, tabstr))
                elif name in data['founda']:  # 轴
                    val = data['value'][name]
                    valuelist.append("""<li><b>{0}</b></li>
                    <table border="1" cellpadding="2" cellspacing="0">
                    {1}
                    </table>
                    """.format(name,
                               htmltabrow(val)))
            valuestr = ''.join(valuelist)
        else:
            valuestr = '无'
        parag['value'] = HTML_IncaInform_Value.format(valuestr)

        parag['foundm'] = HTML_IncaInform_Foundm.format(htmllist(sorted(data['foundm']), True))
        parag['foundcs'] = HTML_IncaInform_Foundcs.format(htmllist(sorted(data['foundcs']), True))
        parag['foundco'] = HTML_IncaInform_Foundco.format(htmllist(sorted(data['foundco']), True))
        parag['foundct'] = HTML_IncaInform_Foundct.format(htmllist(sorted(data['foundct']), True))
        parag['founda'] = HTML_IncaInform_Founda.format(htmllist(sorted(data['founda']), True))
        parag['caliable'] = HTML_IncaInform_Caliable.format(htmllist(sorted(data['caliable']), True))
        parag['calidisable'] = HTML_IncaInform_Calidisable.format(htmllist(sorted(data['calidisable']), True))

        return HTML_IncaInform_Main.format(body=''.join(parag.values())
                                           , h2style='{background-color:#B0E0E6;\npadding:8px;}\n')


######################################### GUI子类 ##################################################
class MainFrame(wx.Frame):
    def __init__(self, mainobj):
        wx.Frame.__init__(self, None, title='Script Manage')
        # self.SetSize(wx.GetClientDisplayRect())  # 显示器工作区尺寸(除开任务栏)
        self.SetBackgroundColour(wx.Colour(83, 134, 139))
        # self.Centre()
        self.Maximize()
        self.SetIcon(wx.Icon(IMGIcon.GetBitmap()))
        self.mainobj = mainobj
        self.sizeratio = [0.17, 0.6]

        self.spliwin_0 = wx.SplitterWindow(self, style=wx.SP_BORDER)
        self.spliwin_0.SetMinimumPaneSize(50)

        self.left = LeftPanel(self.spliwin_0, mainobj=self.mainobj)  # 左面板
        self.spliwin_1 = wx.SplitterWindow(self.spliwin_0, style=wx.SP_BORDER)
        self.spliwin_1.SetMinimumPaneSize(50)

        self.mid = MiddlePanel(self.spliwin_1, mainobj=self.mainobj)  # 中面板
        self.right = RightPanel(self.spliwin_1, mainobj=self.mainobj)  # 右面板

        self.spliwin_0.SplitVertically(self.left, self.spliwin_1)  # , 280)
        self.spliwin_1.SplitVertically(self.mid, self.right)  # , 650)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.toolbar_init()
        self.left.plinit()
        self.mid.plinit()
        # self.right.inputConfigWin_init()
        self.right.outputConfigWin_init()

        # self.SetWindowStyleFlag(wx.CAPTION | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER|wx.CLOSE_BOX)
        # self.ToggleWindowStyle(wx.CLOSE_BOX)
        self.Show()

        # self.ShowFullScreen(True,wx.FULLSCREEN_NOCAPTION)

    def toolbar_init(self):
        self.SetToolBar(MainFrameToolBar(self, self.mainobj))

    def on_size(self, event):
        size = self.GetSize().GetWidth()
        self.spliwin_0.SetSashPosition(int(size * self.sizeratio[0]))
        self.spliwin_1.SetSashPosition(int(size * self.sizeratio[1]))
        self.Layout()
        event.Skip()

    def on_close(self, event):
        try:
            self.mainobj.close_manage()
        except Exception as e:
            wx.LogError('close_manage() 出错\n' + str(e))
            event.Skip()
            raise e
        else:
            event.Skip()

    def showhtml(self, html):
        HtmlWin(parent=None, mainobj=self.mainobj, text=html)


class RightPanel(wx.Panel):
    def __init__(self, parent, mainobj=None):
        # print('RightPanel __init__ ')
        wx.Panel.__init__(self, parent)
        self.mainobj = mainobj

    def inputConfigWin_init(self):
        # print('_RightPanel__inputconfigwin_init')
        self.cfwin_text = wx.StaticText(self, size=(28, 28),
                                        style=wx.ALIGN_CENTRE_HORIZONTAL | wx.ST_NO_AUTORESIZE | wx.ST_ELLIPSIZE_MIDDLE, )
        self.cfwin_text.SetBackgroundColour(wx.Colour(121, 205, 205))
        self.cfwin_text.SetFont(
            wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName='微软雅黑'))  # 字体
        self.cfwin_check = wx.CheckListBox(self,
                                           style=wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.LB_SORT | wx.LB_SINGLE)
        self.cfwin_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_EDIT_LABELS | wx.LC_HRULES)
        self.cfwin_loadtext = wx.Choice(self)
        self.cfwin_savetext = wx.TextCtrl(self, size=(26, 26))
        self.bt = {}
        self.bt['配置主键'] = wx.Button(self, size=(26, 26), style=wx.BORDER_NONE)
        self.bt['配置主键'].SetBackgroundColour(wx.Colour(83, 134, 139))
        self.bt['配置主键'].SetBitmap(IMGList.GetBitmap())
        self.bt['配置主键'].SetBitmapCurrent(IMGList2.GetBitmap())
        self.bt['配置主键'].SetBitmapPressed(IMGList.GetBitmap())
        self.bt['创建配置'] = wx.Button(self, size=(26, 26), style=wx.BORDER_NONE)
        self.bt['创建配置'].SetBackgroundColour(wx.Colour(83, 134, 139))
        self.bt['创建配置'].SetBitmap(IMGAdd.GetBitmap())
        self.bt['创建配置'].SetBitmapCurrent(IMGAdd2.GetBitmap())
        self.bt['创建配置'].SetBitmapPressed(IMGAdd.GetBitmap())
        self.bt['运行脚本'] = wx.Button(self, label='运行脚本', size=(50, 28))
        self.bt_ipscpstop = wx.Button(self, size=(24, 24))
        self.bt_ipscpstop.SetBackgroundColour(wx.Colour(83, 134, 139))
        self.bt_ipscpstop.SetBitmap(IMGStop.GetBitmap())

        self.sizer = wx.GridBagSizer(4, 2)
        gridcol = 2
        ep = wx.EXPAND

        self.sizer.Add(self.cfwin_text, pos=(0, 0), span=(2, gridcol),
                       flag=ep | wx.RIGHT | wx.LEFT | wx.TOP, border=5)
        self.sizer.Add(self.cfwin_loadtext, pos=(2, 1), span=(1, 1), flag=ep | wx.RIGHT, border=4)
        self.sizer.Add(self.bt['配置主键'], pos=(2, 0), span=(1, 1), flag=wx.LEFT | wx.RIGHT, border=4)

        self.sizer.Add(self.cfwin_savetext, pos=(3, 1), span=(1, 1), flag=ep | wx.RIGHT, border=4)
        self.sizer.Add(self.bt['创建配置'], pos=(3, 0), span=(1, 1), flag=wx.LEFT | wx.RIGHT, border=4)

        self.sizer.Add(self.cfwin_check, pos=(4, 0), span=(3, gridcol),
                       flag=ep | wx.RIGHT | wx.LEFT, border=4)
        self.sizer.Add(self.cfwin_list, pos=(7, 0), span=(4, gridcol),
                       flag=ep | wx.RIGHT | wx.LEFT, border=4)

        self.sizer.Add(self.bt['运行脚本'], pos=(11, 1), span=(1, 1),
                       flag=ep | wx.LEFT | wx.RIGHT, border=30)
        self.sizer.Add(self.bt_ipscpstop, pos=(11, 0), span=(1, 1),
                       flag=wx.ALL, border=4)
        self.sizer.Add(10, 10, pos=(12, 0), span=(1, gridcol), flag=ep)

        self.sizer.AddGrowableCol(1)
        for i in range(4, 11):
            self.sizer.AddGrowableRow(i)
        self.sizer.AddGrowableRow(12)

        self.SetSizer(self.sizer)

        for button in self.bt.values(): button.Disable()
        self.bt_ipscpstop.Disable()

        wd = self.GetSize().GetWidth() - 10
        self.cfwin_colwid_dic = {0: 0.2, 1: 0.6, 2: 0.2}
        self.cfwin_list.InsertColumn(0, '值', width=int(wd * 0.2))
        self.cfwin_list.InsertColumn(1, '变量名', width=int(wd * 0.6))
        self.cfwin_list.InsertColumn(2, '单位', width=int(wd * 0.2))
        self.cfwin_list.SetColumnsOrder([1, 0, 2])

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, lambda e: self.PopupMenu(InputScpMainContextMenu(self.mainobj)), self.bt['配置主键'])
        self.Bind(wx.EVT_BUTTON, self.on_ipRun, self.bt['运行脚本'])
        self.Bind(wx.EVT_BUTTON, self.on_ipStop, self.bt_ipscpstop)
        self.Bind(wx.EVT_BUTTON,
                  lambda e: self.mainobj.ipconfig_add(self.cfwin_savetext.GetValue()), self.bt['创建配置'])
        self.cfwin_text.Bind(wx.EVT_LEFT_DOWN, self.on_ipclickStaticText)
        self.cfwin_check.Bind(wx.EVT_CONTEXT_MENU, self.on_ipwinCheckRightClick)
        self.cfwin_check.Bind(wx.EVT_CHECKLISTBOX, self.on_ipcheckListBox)
        self.cfwin_check.Bind(wx.EVT_LISTBOX, lambda e: self.mainobj.ipconfig_showItemNotes(e.GetString()))
        self.cfwin_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_ipwinListItemRightClick)
        self.cfwin_list.Bind(wx.EVT_CONTEXT_MENU, self.on_ipwinListRightClick)
        self.cfwin_list.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.on_ipendLabelEdit)
        self.cfwin_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
                             lambda e: self.cfwin_list.EditLabel(e.GetItem().GetId()))
        self.cfwin_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_ipwinListItemSelect)
        self.cfwin_loadtext.Bind(wx.EVT_CHOICE, lambda e: self.mainobj.ipconfig_change(e.GetString()))

        self.Layout()

    def outputConfigWin_init(self):
        self.cfwin_text = wx.StaticText(self, size=(28, 28),
                                        style=wx.ALIGN_CENTRE_HORIZONTAL | wx.ST_NO_AUTORESIZE | wx.ST_ELLIPSIZE_MIDDLE)
        self.cfwin_text.SetBackgroundColour(wx.Colour(121, 205, 205))
        self.cfwin_text.SetFont(
            wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName='微软雅黑'))  # 字体
        self.cfwin_dirtext = wx.StaticText(self, size=(24, 24), style=wx.ST_NO_AUTORESIZE | wx.ST_ELLIPSIZE_START)
        self.cfwin_dirtext.SetBackgroundColour(wx.Colour(225, 255, 255))
        self.cfwin_dirtext.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                                           faceName='微软雅黑'))  # 字体
        self.cfwin_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_HRULES)
        self.bt = {}
        self.bt['运行脚本'] = wx.Button(self, label='运行脚本', size=(50, 28))
        self.bt['选择路径'] = wx.Button(self, size=(24, 24), style=wx.BORDER_NONE)
        self.bt['选择路径'].SetBackgroundColour(wx.Colour(83, 134, 139))
        self.bt['选择路径'].SetBitmap(IMGDir.GetBitmap())
        self.bt['选择路径'].SetBitmapCurrent(IMGDir2.GetBitmap())
        self.bt['选择路径'].SetBitmapPressed(IMGDir.GetBitmap())
        self.prdmode_chioce = wx.RadioBox(self, label='数据采样周期', choices=['文件内周期', '自定义周期'])
        self.prdmode_chioce.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.sysprd_stctext = wx.StaticText(self, size=(80, 20), label='文件内周期:', style=wx.ST_NO_AUTORESIZE)
        self.sysprd_stctext.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.sysprd_text = wx.TextCtrl(self, size=(20, 20))
        self.sysprd_text.SetEditable(False)
        self.customprd_stctext = wx.StaticText(self, size=(80, 20), label='自定义周期(s):', style=wx.ST_NO_AUTORESIZE)
        self.customprd_stctext.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.customprd_text = wx.TextCtrl(self, size=(20, 20))
        self.customprd_text.SetEditable(False)

        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.Add(self.cfwin_text, pos=(0, 0), span=(1, 3),
                       flag=wx.EXPAND | wx.RIGHT | wx.LEFT | wx.TOP, border=5)
        self.sizer.Add(self.bt['选择路径'], pos=(1, 0), span=(1, 1), flag=wx.LEFT | wx.RIGHT, border=5)
        self.sizer.Add(self.cfwin_dirtext, pos=(1, 1), span=(1, 2), flag=wx.EXPAND | wx.RIGHT, border=5)
        self.sizer.Add(self.cfwin_list, pos=(2, 0), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                       border=5)
        self.sizer.Add(self.prdmode_chioce, pos=(3, 0), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        self.sizer.Add(self.sysprd_stctext, pos=(4, 0), span=(1, 2), flag=wx.LEFT | wx.RIGHT, border=5)
        self.sizer.Add(self.sysprd_text, pos=(4, 2), span=(1, 1), flag=wx.EXPAND | wx.RIGHT, border=5)
        self.sizer.Add(self.customprd_stctext, pos=(5, 0), span=(1, 2), flag=wx.LEFT | wx.RIGHT, border=5)
        self.sizer.Add(self.customprd_text, pos=(5, 2), span=(1, 1), flag=wx.EXPAND | wx.RIGHT | wx.BOTTOM, border=5)
        self.sizer.Add(self.bt['运行脚本'], pos=(6, 0), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=30)
        self.sizer.Add(30, 30, pos=(7, 0), span=(1, 3))

        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableRow(2)
        self.SetSizer(self.sizer)

        for button in self.bt.values(): button.Disable()

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_BUTTON, self.on_opselctLoadPath, self.bt['选择路径'])
        self.Bind(wx.EVT_BUTTON, self.on_opRun, self.bt['运行脚本'])
        self.cfwin_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_opItemRightClick)
        self.prdmode_chioce.Bind(wx.EVT_RADIOBOX, self.on_opPrdModeChoice)
        self.sysprd_text.Bind(wx.EVT_TEXT, self.on_opSysPrdText)
        self.customprd_text.Bind(wx.EVT_TEXT, self.on_opCustomPrdText)

        wd = self.GetSize().GetWidth() - 10
        self.cfwin_colwid_dic = {0: 0.8, 1: 0.2}
        self.cfwin_list.InsertColumn(0, '文件', width=int(wd * 0.8))
        self.cfwin_list.InsertColumn(1, '大小(KB)', width=int(wd * 0.2))
        self.Layout()
        self.sysprd_stctext.Refresh()
        self.customprd_stctext.Refresh()
        self.disable_opPrd()

    def on_ipwinListItemSelect(self, event):
        item = event.GetItem().GetId()
        name = self.cfwin_list.GetItemText(item, 1)
        self.mainobj.ipconfig_showItemNotes(name)

    def on_ipwinListItemRightClick(self, event):
        item = event.GetItem().GetId()
        name = self.cfwin_list.GetItemText(item, 1)
        scp = self.mainobj.cur_state.script
        obj = self.mainobj.db.config_dic[scp['id']][scp['config']]
        inform = getattr(obj, name)
        self.PopupMenu(InputScpParamContextMenu(self.mainobj, 0, item, iteminform=(name, inform)))
        event.Veto()

    def on_ipwinListRightClick(self, event):
        if self.mainobj.cur_state.script['config']:
            self.PopupMenu(InputScpParamContextMenu(self.mainobj, 1))

    def on_ipwinCheckRightClick(self, event):
        scp = self.mainobj.cur_state.script
        if scp['config']:
            item = self.cfwin_check.GetSelection()
            if item == wx.NOT_FOUND:
                self.PopupMenu(InputScpBoolContextMenu(self.mainobj, 1))
            else:
                obj = self.mainobj.db.config_dic[scp['id']][scp['config']]
                name = self.cfwin_check.GetString(item)
                inform = getattr(obj, name)
                self.PopupMenu(InputScpBoolContextMenu(self.mainobj, 0, item, iteminform=(name, inform)))

    def on_ipRun(self, event):
        self.bt['运行脚本'].Disable()
        self.mainobj.inputScpRun()

    def on_ipStop(self, event):
        self.mainobj.ipscprun_thread.exit()

    def on_opRun(self, event):
        item = self.cfwin_list.GetFocusedItem()
        if item != -1:
            self.bt['运行脚本'].Disable()
            filename = self.cfwin_list.GetItemText(item, 0)
            thdoprun = threading.Thread(target=self.mainobj.outputScpRun, args=(filename,), daemon=True)
            thdoprun.start()

    def on_size(self, event):
        wd = self.GetSize().GetWidth() - 10
        for i, ratio in self.cfwin_colwid_dic.items():
            self.cfwin_list.SetColumnWidth(i, int(wd * ratio))
        event.Skip()

    def on_ipendLabelEdit(self, event):
        item = event.GetItem().GetId()
        name = self.cfwin_list.GetItemText(item, 1)
        value = eval(event.GetLabel())
        self.mainobj.ipconfig_moditem(name, value)
        event.Skip()

    def on_ipcheckListBox(self, event):
        name = event.GetString()
        item = self.cfwin_check.FindString(name)
        value = 1 if self.cfwin_check.IsChecked(item) else 0
        self.mainobj.ipconfig_moditem(name, value)
        event.Skip()

    def on_ipclickStaticText(self, event):
        self.mainobj.ipconfig_showDoc()
        event.Skip()

    def on_opselctLoadPath(self, event):
        scp = self.mainobj.cur_state.script
        if scp['active']:
            dfpath = self.mainobj.db.config_dic[scp['id']]['default'].loaddir
            dirpath = wx.DirSelector(parent=self, default_path=dfpath)
            if dirpath:
                self.mainobj.output_chgLoadDir(dirpath)

    def on_opItemRightClick(self, event):
        dir = self.cfwin_dirtext.GetLabel()
        if dir:
            file = self.cfwin_list.GetItemText(event.GetIndex(), 0)
            path = os.path.join(dir, file)
            self.PopupMenu(OutputScpDirContextMenu(self.mainobj, path))

    def on_opPrdModeChoice(self, event):
        mode = event.GetString()
        if mode == '文件内周期':
            self.sysprd_text.SetEditable(True)
            self.customprd_text.SetEditable(False)
            self.mainobj.opconfig_setitem(mdfperiodmode=0)
        else:
            self.sysprd_text.SetEditable(False)
            self.customprd_text.SetEditable(True)
            self.mainobj.opconfig_setitem(mdfperiodmode=1)

    def on_opSysPrdText(self, event):
        text = event.GetString()
        self.mainobj.opconfig_setitem(mdfsysperiod=text)

    def on_opCustomPrdText(self, event):
        text = event.GetString().strip()
        if text:
            self.mainobj.opconfig_setitem(mdfcustomperiod=eval(text))
        else:
            self.mainobj.opconfig_setitem(mdfcustomperiod=0.0)

    def refresh_inputscp(self, obj=None):
        """刷新工况输入脚本窗口"""
        checkwin = self.cfwin_check
        checkwin.Clear()

        listwin = self.cfwin_list
        listwin.DeleteAllItems()

        if obj != None:
            obj_attributes = list(obj.__dict__.keys())
            if '__doc__' in obj_attributes: obj_attributes.remove('__doc__')
            i = 0
            for name in obj_attributes:
                val = getattr(obj, name)
                value = val[0]
                unit = val[1]
                if unit == 'bool':
                    item = checkwin.Append(name)
                    checkwin.Check(item, check=bool(value))
                else:
                    listwin.InsertItem(i, str(value))
                    listwin.SetItem(i, 1, name)
                    listwin.SetItem(i, 2, unit)
                    i += 1

    def refresh_iploadConfigWin(self, textlist=None, curtext=''):
        """刷新加载配置选择窗口"""
        win = self.cfwin_loadtext
        win.Clear()
        if textlist:
            textlist.sort()
            win.AppendItems(textlist)
            if curtext:
                win.SetSelection(win.FindString(curtext, True))

    def add_ipCfCheckItem(self, text, check=True):
        item = self.cfwin_check.Append(text)
        self.cfwin_check.Check(item, check=check)

    def add_ipCfListItem(self, name, value, unit='-'):
        listwin = self.cfwin_list
        i = listwin.GetItemCount()
        listwin.InsertItem(i, value.__str__())
        listwin.SetItem(i, 1, name)
        listwin.SetItem(i, 2, unit)

    def mod_ipCfCheckItem(self, text, check=True):
        item = self.cfwin_check.FindString(text, True)
        self.cfwin_check.Check(item, check.__bool__())

    def mod_ipCfListItem(self, name, value):
        win = self.cfwin_list
        for i in range(win.GetItemCount()):
            if name == win.GetItemText(i, 1):
                win.SetItemText(i, str(value))
                break

    def delete_ipCfCheckSelectItem(self, item):
        self.cfwin_check.Delete(item)

    def delete_ipCfListSelectItem(self, item):
        self.cfwin_list.DeleteItem(item)

    def refresh_opFileListWin(self, dir=''):
        """获取某文件夹下的文件，并显示到列表窗口上"""
        win = self.cfwin_list
        win.DeleteAllItems()
        if dir:
            childlist = os.listdir(dir)
            abschildlist = [os.path.join(dir, x) for x in childlist]
            filelist = list(filter(os.path.isfile, abschildlist))
            sizelist = ['{0:,d}'.format(int(os.path.getsize(x) / 1024 + 1)) for x in filelist]
            namelist = [os.path.basename(x) for x in filelist]
            i = 0
            for file, size in zip(namelist, sizelist):
                win.InsertItem(i, file)
                win.SetItem(i, 1, size)
                i += 1

    def refresh_opPrd(self, configobj=None):
        if configobj:
            self.sysprd_text.ChangeValue(configobj.mdfsysperiod)
            self.customprd_text.ChangeValue(str(configobj.mdfcustomperiod))
            mode = configobj.mdfperiodmode
            self.prdmode_chioce.SetSelection(mode)
            if mode:
                self.sysprd_text.SetEditable(False)
                self.customprd_text.SetEditable(True)
            else:
                self.sysprd_text.SetEditable(True)
                self.customprd_text.SetEditable(False)
        else:
            self.sysprd_text.ChangeValue('')
            self.customprd_text.ChangeValue('')

    def disable_opPrd(self):
        self.customprd_text.Disable()
        self.sysprd_text.Disable()
        self.prdmode_chioce.Disable()

    def enable_opPrd(self):
        self.customprd_text.Enable()
        self.sysprd_text.Enable()
        self.prdmode_chioce.Enable()


class MiddlePanel(wx.Panel):
    def __init__(self, parent, mainobj=None):
        # print('MiddlePanel __init__ ')
        wx.Panel.__init__(self, parent)
        self.mainobj = mainobj
        self.keystat = wx.KeyboardState()

    def plinit(self):
        # self.code_win = wx.TextCtrl(self.gui.mid, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL)
        self.code_win = StyledTextCtrl(self)
        self.log_win = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2)
        # self.toppl=wx.Panel(self)
        # self.bt={}
        # self.bt['查找']=wx.Button(self.toppl,label='查找',size=(32,20))

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # self.sizer.Add(self.toppl,3, flag=wx.EXPAND)
        self.sizer.Add(self.code_win, 84, flag=wx.EXPAND)
        self.sizer.Add(self.log_win, 16, flag=wx.EXPAND)

        self.code_win.Bind(wx.EVT_KEY_DOWN, self.on_codewinkeydown)
        self.code_win.Bind(wx.EVT_KEY_UP, self.on_codewinkeyup)
        # self.bt['查找'].Bind(wx.EVT_BUTTON,lambda e:print('asdasd'))

        self.SetSizer(self.sizer)
        self.codewin_init()

    def codewin_init(self):
        # print('codewin_init()')
        win = self.code_win

        m = wx.FontEnumerator()
        self.sys_fontlist = m.GetFacenames()
        # temp = m.GetEncodings('Consolas')
        # print('GetEncodings Consolas', temp)
        # self.sys_fontlist.sort()
        # for i, fff in enumerate(self.sys_fontlist):
        #     print('"%s"' % fff, end=',')
        #     if i % 8 == 7: print()
        # print()
        self.codewin_fontprior = ['JetBrains Mono', 'Consolas', 'Lucida Console', 'Comic Sans MS', 'Tahoma']  # 字体首选项
        for myfacename in self.codewin_fontprior:
            if myfacename in self.sys_fontlist:
                facename = myfacename
                break
        else:
            facename = 'Times New Roman'
        # print('font facename >>', facename)
        # font = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
        #                faceName=facename)
        font = wx.Font(wx.FontInfo().Weight(14).FaceName(facename))
        win.StyleSetFont(wx.stc.STC_STYLE_DEFAULT, font)
        # print(wx.stc.STC_STYLE_DEFAULT)
        # win.StyleSetFontAttr(wx.stc.STC_STYLE_DEFAULT, 12, facename, False, False, False)
        # win.SetFont(font)
        print('style facename >', win.StyleGetFaceName(wx.stc.STC_STYLE_DEFAULT))
        # win.StyleSetBackground(wx.stc.STC_STYLE_DEFAULT,wx.Colour(200,100,0))
        # win.SetUseHorizontalScrollBar(False)

        win.SetIndent(4)  # TAB键=4个空格
        win.SetUseTabs(False)  # 禁止空格制表符共用
        # win.SetControlCharSymbol(64)
        win.SetCodePage(wx.stc.STC_CP_UTF8)
        # win.SetLexerLanguage('Python')
        win.SetLexer(wx.stc.STC_LEX_PYTHON)
        kwstr = ' '.join(keyword.kwlist)
        win.SetKeyWords(0, kwstr)  # 导入关键词

        win.StyleSetSpec(wx.stc.STC_P_DEFAULT, 'fore:#696969')  # 语法高亮
        win.StyleSetSpec(wx.stc.STC_P_CLASSNAME, 'fore:#FF1493')
        win.StyleSetSpec(wx.stc.STC_P_DEFNAME, 'fore:#FF1493')
        win.StyleSetSpec(wx.stc.STC_P_STRING, 'fore:#228B22')
        win.StyleSetSpec(wx.stc.STC_P_CHARACTER, 'fore:#228B22')
        win.StyleSetSpec(wx.stc.STC_P_STRINGEOL, 'fore:#FF00FF')
        win.StyleSetSpec(wx.stc.STC_P_WORD, 'fore:#0000CD')
        win.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, 'fore:#DAA520')
        win.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, 'fore:#DAA520')
        win.StyleSetSpec(wx.stc.STC_P_DECORATOR, 'fore:#2F4F4F')
        win.StyleSetSpec(wx.stc.STC_P_IDENTIFIER, 'fore:#7E3712')
        win.StyleSetSpec(wx.stc.STC_P_NUMBER, 'fore:#EE2C2C')
        win.StyleSetSpec(wx.stc.STC_P_TRIPLE, 'fore:#228B22')
        win.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, 'fore:#228B22')
        win.StyleSetSpec(wx.stc.STC_P_OPERATOR, 'fore:#4B0082')
        win.StyleSetSpec(wx.stc.STC_P_WORD2, 'fore:#FF69B4')

        win.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)  # 左边界行数
        win.SetMarginWidth(1, 30)

    def refresh_codewin(self, text=None):
        # print('refresh_codewin()')
        self.code_win.ClearAll()
        if text:
            self.code_win.SetText(text)

    def on_codewinkeyup(self, event):
        keyw = event.GetKeyCode()
        if keyw == wx.WXK_CONTROL:
            self.keystat.SetControlDown(False)
        event.Skip()

    def on_codewinkeydown(self, event):
        keyw = event.GetKeyCode()
        if keyw == wx.WXK_CONTROL:
            self.keystat.SetControlDown(True)
        if keyw == ord('S') and self.keystat.ControlDown():
            self.mainobj.code_save(self.code_win.GetText())
        elif keyw == ord('F') and self.keystat.ControlDown():
            findwin = FindCodeStringWin(parent=self.mainobj.gui, codewin=self.code_win)
        event.Skip()


class LeftPanel(wx.Panel):
    def __init__(self, parent, mainobj=None):
        # print('LeftPanel __init__ ')
        wx.Panel.__init__(self, parent)
        self.mainobj = mainobj

    def plinit(self):
        # self.tree_win = wx.TreeCtrl(self.gui.left, style=wx.TR_HIDE_ROOT | wx.TR_SINGLE)
        self.tree_selct_win = wx.ComboBox(self, style=wx.CB_READONLY | wx.CB_SORT)
        self.tree_win = ScriptTree(self, mainobj=self.mainobj)
        self.bt_dbctrl = wx.Button(self, size=(20, 20), style=wx.BORDER_NONE)
        self.bt_dbctrl.SetBackgroundColour(wx.Colour(83, 134, 139))
        self.bt_dbctrl.SetBitmap(IMGAddDb.GetBitmap())
        self.bt_dbctrl.SetBitmapCurrent(IMGAddDb2.GetBitmap())
        self.bt_dbctrl.SetBitmapPressed(IMGAddDb.GetBitmap())

        self.grid_left = wx.GridBagSizer(0, 2)
        self.grid_left.Add(self.tree_selct_win, pos=(0, 0), span=(1, 1), flag=wx.EXPAND | wx.ALL, border=4)
        self.grid_left.Add(self.bt_dbctrl, pos=(0, 1), span=(1, 1), flag=wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM,
                           border=4)
        self.grid_left.Add(self.tree_win, pos=(1, 0), span=(1, 2), flag=wx.EXPAND)

        self.grid_left.AddGrowableCol(0)
        self.grid_left.AddGrowableRow(1)

        self.SetSizer(self.grid_left)

        self.tree_selct_win.Bind(wx.EVT_COMBOBOX, lambda e: self.mainobj.database_change(e.GetString()))
        self.bt_dbctrl.Bind(wx.EVT_BUTTON, lambda e: self.PopupMenu(DbCtrlContextMenu(self.mainobj)))

        self.Layout()

    def refresh_TreeSelctWin(self, dbname_list, dbname=''):
        """刷新数据库选择窗口"""
        # print('refresh_TreeSelctWin')
        self.tree_selct_win.Clear()
        for x in dbname_list: self.tree_selct_win.Append(x)
        if dbname:
            self.tree_selct_win.SetSelection(self.tree_selct_win.FindString(dbname))  # 选择database


class ScriptTree(wx.TreeCtrl):
    def __init__(self, parent,
                 style=wx.TR_HIDE_ROOT | wx.TR_MULTIPLE | wx.TR_HAS_BUTTONS | wx.TR_TWIST_BUTTONS | wx.TR_EDIT_LABELS,
                 mainobj=None):
        # print('ScriptTree __init__')
        wx.TreeCtrl.__init__(self, parent, style=style)
        self.mainobj = mainobj

        image_list = wx.ImageList(20, 20)
        image_list.Add(IMGFolder.GetBitmap())
        image_list.Add(IMGSteWhl.GetBitmap())
        image_list.Add(IMGNight.GetBitmap())
        image_list.Add(IMGChart.GetBitmap())

        self.AssignImageList(image_list)
        self.imageid_dict = {SCPTYPE_FOLDER: 0, SCPTYPE_INPUT: 1, SCPTYPE_OUTPUT: 3}

        self.Bind(wx.EVT_RIGHT_DOWN, self.on_rightdown)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.on_rename)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activated)

    def on_activated(self, event):
        """双击项目"""
        item = event.GetItem()
        item_list = self.get_dictpath(item)
        if self.scptype(item) == SCPTYPE_FOLDER:
            self.Toggle(item)
        else:
            self.mainobj.tree_active(item_list)

    def refresh_all_from_dict(self, dic=None):
        # print('ScriptTree refresh_all_from_dict')

        def refresh_all_from_dict_cycle(dic, parent):
            # print('ScriptTree refresh_all_from_dict_cycle')
            for key, val in dic.items():
                if isinstance(val, dict):
                    dir = self.InsertItem(parent, 0, key, data=(SCPTYPE_FOLDER, -1, [None]))
                    self.SetItemImage(dir, self.imageid_dict[SCPTYPE_FOLDER], wx.TreeItemIcon_Normal)
                    refresh_all_from_dict_cycle(val, dir)
                else:
                    item = self.InsertItem(parent, 0, key, data=val)
                    self.SetItemImage(item, self.imageid_dict[val[0]], wx.TreeItemIcon_Normal)
            self.SortChildren(parent)

        self.DeleteAllItems()
        if self.IsEmpty():
            self.AddRoot('root', data=(SCPTYPE_FOLDER, 0, [None]))
        if dic:
            refresh_all_from_dict_cycle(dic, self.GetRootItem())

    def get_dictpath(self, treeitem):
        """通过树得到字典项目路径"""

        # print('ScriptTree get_dictpath')

        def get_dictpath_cycle(child, item_list):
            # print('ScriptTree get_dictpath_cycle')
            parent = self.GetItemParent(child)
            if not parent == self.GetRootItem():
                item_list.insert(0, self.GetItemText(parent))
                get_dictpath_cycle(parent, item_list)

        item_list = []
        item_list.insert(0, self.GetItemText(treeitem))
        get_dictpath_cycle(treeitem, item_list)
        return item_list

    def delete(self):
        # print('ScriptTree delete')
        items = self.GetSelections()
        for item in items:
            yield self.get_dictpath(item)
            self.Delete(item)

    def additem(self, text, inform):
        """添加脚本或文件夹"""
        # print('ScriptTree additem')
        item = self.GetFocusedItem()
        imageid = self.imageid_dict[inform[0]]
        if item:
            if self.scptype(item) == SCPTYPE_FOLDER:
                newitem = self.InsertItem(item, 0, text, image=imageid, data=inform)
            else:
                parent = self.GetItemParent(item)
                newitem = self.InsertItem(parent, 0, text, image=imageid, data=inform)
            self.UnselectItem(item)
        else:
            newitem = self.InsertItem(self.GetRootItem(), 0, text, image=imageid, data=inform)
        self.SetFocusedItem(newitem)
        self.SelectItem(newitem)
        return self.get_dictpath(newitem), newitem

    def addtopfolder(self, text, inform):
        """添加顶层文件夹"""
        # print('ScriptTree addtopfolder')
        newitem = self.InsertItem(self.GetRootItem(), 0, text, image=self.imageid_dict[inform[0]], data=inform)
        return newitem

    def on_rename(self, event):
        # print('ScriptTree on_rename')
        text = event.GetLabel()
        item = event.GetItem()
        if text:
            item_list = self.get_dictpath(item)
            self.SetItemText(item, text)
            i = 0
            newtext = text
            while self.judge_redund(item):  # 有重复项时会重命名
                i += 1
                newtext = text + '_' + str(i)
                self.SetItemText(item, newtext)
            self.mainobj.tree_rename(item_list, newtext)
            if i > 0: self.mainobj.tree_refresh()
        else:
            time.sleep(0.05)
            self.mainobj.tree_refresh()

        self.mainobj._showdb_()

    def scptype(self, item):
        """返回脚本类型 1：工况输入脚本  2：输出校验脚本 -1：文件夹"""
        # print('ScriptTree scptype')
        return self.GetItemData(item)[0]

    def judge_redund(self, item):
        """判断同级项目里是否有重复项 True:有重复项 False:没用重复项"""
        # print('ScriptTree judge_redund')
        text = self.GetItemText(item)
        itemparent = self.GetItemParent(item)
        item0, cookie = self.GetFirstChild(itemparent)
        count = 0

        while item0.IsOk():  # 是否引用有效的树项
            if self.GetItemText(item0) == text: count += 1
            item0, cookie = self.GetNextChild(itemparent, cookie)
        if count <= 1:
            return False
        else:
            return True

    def on_rightdown(self, event):
        # print('ScriptTree on_rightdown')
        if self.mainobj.cur_state.database:
            self.PopupMenu(TreeWinContextMenu(self.mainobj))

    def expand_itemFromList(self, itemlist, select=True):
        """展开项目"""
        # print('tree expand_itemFromList()')
        # print(itemlist)
        path0 = itemlist[:-1]
        name = [-1]
        itemparent = self.GetRootItem()
        for folder in path0:
            itemchild, cookie = self.GetFirstChild(itemparent)
            while itemchild.IsOk():  # 是否引用有效的树项
                if self.GetItemText(itemchild) == folder:
                    self.Expand(itemchild)
                    itemparent = itemchild
                    break
                itemchild, cookie = self.GetNextChild(itemparent, cookie)
            else:
                print('未找到:%s' % folder)
                break

        itemfinal, cookie = self.GetFirstChild(itemparent)
        while itemfinal.IsOk():
            if self.GetItemText(itemfinal) == name:
                self.ScrollTo(itemfinal)
                if select:
                    self.UnselectAll()
                    self.SelectItem(itemfinal)
                    self.ClearFocusedItem()
                    self.SetFocusedItem(itemfinal)
                break
            itemfinal, cookie = self.GetNextChild(itemparent, cookie)


class ImportIncaParamWin(wx.Frame):
    """导入变量到INCA实验环境的窗口"""

    def __init__(self, parent, mainobj):
        wx.Frame.__init__(self, parent=parent, title='导入变量到INCA实验环境',
                          size=(650, 700), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.mainobj = mainobj

        self.pl = wx.Panel(self, size=(650, 700))

        self.textwin = wx.StaticText(self.pl, label='把测量量\标定量名称复制到下面窗口(以换行分隔)', style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.parwin = wx.TextCtrl(self.pl, style=wx.TE_MULTILINE | wx.TE_DONTWRAP)
        self.logwin = wx.TextCtrl(self.pl, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(100, 100))
        self.check = {}
        self.check['skiperror'] = wx.CheckBox(self.pl, label='跳过错误项目', size=(100, 20))
        self.check['ramcal'] = wx.CheckBox(self.pl, label='导入RamCal变量')
        self.textwin2 = wx.StaticText(self.pl, label='测量量采样率:')
        self.sampwin = wx.TextCtrl(self.pl, value='Task10ms')
        self.bt = wx.Button(self.pl, label='导入', size=(80, 40))

        self.check['skiperror'].SetValue(True)
        self.check['ramcal'].SetValue(False)

        self.sizer = wx.GridBagSizer(5, 10)
        self.sizer.Add(self.textwin, pos=(0, 0), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=10)
        self.sizer.Add(self.parwin, pos=(1, 0), span=(5, 1), flag=wx.EXPAND | wx.LEFT, border=10)
        self.sizer.Add(20, 20, pos=(1, 1), span=(1, 1), flag=wx.EXPAND)
        self.sizer.Add(self.check['skiperror'], pos=(2, 1), span=(1, 1), flag=wx.RIGHT, border=10)
        self.sizer.Add(self.check['ramcal'], pos=(3, 1), span=(1, 1), flag=wx.RIGHT, border=10)
        self.sizer.Add(self.textwin2, pos=(4, 1), span=(1, 1), flag=wx.EXPAND)
        self.sizer.Add(self.sampwin, pos=(5, 1), span=(1, 1), flag=wx.EXPAND | wx.RIGHT, border=10)
        self.sizer.Add(self.logwin, pos=(6, 0), span=(1, 1), flag=wx.EXPAND | wx.LEFT, border=10)
        self.sizer.Add(self.bt, pos=(6, 1), span=(1, 1), flag=wx.ALL, border=20)
        self.sizer.Add(20, 20, pos=(7, 0), span=(1, 2), flag=wx.EXPAND)

        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(1)
        self.pl.SetSizer(self.sizer)

        self.Bind(wx.EVT_BUTTON, self.on_button, self.bt)

        self.Centre()
        self.Show()
        self.pl.Layout()

    def on_button(self, event):
        text = self.parwin.GetValue()
        samprate = self.sampwin.GetValue().strip()
        ramcal = self.check['ramcal'].GetValue()
        skiperror = self.check['skiperror'].GetValue()
        sys.stdout = self.logwin
        print('-' * 10, '{:^20s}'.format('INCA导入变量'), '-' * 10)
        try:
            self.mainobj.import_incaParam(text, samprate, ramcal, skiperror)
        except Exception as e:
            print('-' * 47)
            sys.stdout = self.mainobj.gui.mid.log_win
            raise e
        print('-' * 47, '\n')
        sys.stdout = self.mainobj.gui.mid.log_win


class InformIncaParamWin(wx.Frame):
    """根据用户输入显示INCA变量信息的窗口"""

    def __init__(self, parent, mainobj):
        wx.Frame.__init__(self, parent=parent, title='INCA变量信息',
                          size=(650, 700), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.mainobj = mainobj

        self.pl = wx.Panel(self, size=(650, 700))

        self.textwin = wx.StaticText(self.pl, label='把测量量\标定量名称复制到下面窗口(以换行分隔)',
                                     style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.parwin = wx.TextCtrl(self.pl, style=wx.TE_MULTILINE | wx.TE_DONTWRAP)
        self.devchoice = wx.Choice(self.pl, style=wx.CB_SORT)
        self.bt = wx.Button(self.pl, label='开始', size=(80, 40))

        self.sizer = wx.GridBagSizer(5, 10)
        self.sizer.Add(self.textwin, pos=(0, 0), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=10)
        self.sizer.Add(self.parwin, pos=(1, 0), span=(3, 1), flag=wx.EXPAND | wx.LEFT, border=10)
        self.sizer.Add(20, 20, pos=(1, 1), span=(1, 1), flag=wx.EXPAND)
        self.sizer.Add(self.devchoice, pos=(2, 1), span=(1, 1), flag=wx.EXPAND | wx.RIGHT, border=10)
        self.sizer.Add(self.bt, pos=(3, 1), span=(1, 1), flag=wx.ALL, border=20)
        self.sizer.Add(20, 20, pos=(4, 0), span=(1, 2), flag=wx.EXPAND)

        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(1)
        self.pl.SetSizer(self.sizer)

        self.Bind(wx.EVT_BUTTON, self.on_button, self.bt)

        self.Centre()
        self.Show()
        self.pl.Layout()
        self.refresh_devchoice()

    @popuperror
    def refresh_devchoice(self, default='CCP: 1'):
        self.devchoice.Clear()
        ins = _insc.IncaControl()
        ins.init()
        for dev in ins.device:
            self.devchoice.AppendItems(dev)
        if default in ins.device:
            self.devchoice.SetSelection(self.devchoice.FindString('CCP: 1', True))
        else:
            self.devchoice.SetSelection(0)

    def on_button(self, event):
        self.bt.Disable()
        text = self.parwin.GetValue()
        dev = self.devchoice.GetStringSelection()
        if text and dev:
            try:
                self.mainobj.analyse_incaParam(text, dev)
            except Exception as e:
                wx.LogError(str(e))
                self.bt.Enable()
        self.bt.Enable()


class MainFrameToolBar(wx.ToolBar):
    def __init__(self, parent, mainobj):
        wx.ToolBar.__init__(self, parent=parent)
        self.mainobj = mainobj

        self.toolinit = (('添加变量', IMGNight.GetBitmap(), '添加变量到INCA实验环境', wx.ITEM_NORMAL),
                         ('变量信息', IMGNews.GetBitmap(), '通过INCA获得变量信息', wx.ITEM_NORMAL))
        self.tooldic = {}
        for i, x in enumerate(self.toolinit):
            self.tooldic[x[0]] = self.AddTool(i, 'asdasd', x[1], shortHelp=x[2], kind=x[3])
        self.Realize()

        self.Bind(wx.EVT_TOOL, lambda e: ImportIncaParamWin(self.mainobj.gui, self.mainobj), self.tooldic['添加变量'])
        self.Bind(wx.EVT_TOOL, lambda e: InformIncaParamWin(self.mainobj.gui, self.mainobj), self.tooldic['变量信息'])


class InputScpMainContextMenu(wx.Menu):
    """输入脚本配置的上下文菜单"""

    def __init__(self, mainobj):
        # print('InputScpMainContextMenu __init__')
        wx.Menu.__init__(self)
        self.mainobj = mainobj
        menuinit_list = [('从文件导入', wx.ITEM_NORMAL, None), ('导出到文件', wx.ITEM_NORMAL, None),
                         ('修改配置说明', wx.ITEM_NORMAL, None), ('删除', wx.ITEM_NORMAL, None)]
        menuitem_dict = {}
        for x, y, z in menuinit_list:
            temp = wx.MenuItem(parentMenu=self, id=wx.ID_ANY, text=x, kind=y, subMenu=z)
            menuitem_dict[x] = temp
            if x in ['导出到文件', '修改配置说明', '删除']: self.AppendSeparator()
            self.Append(temp)

        self.Bind(wx.EVT_MENU, self.on_loadconfig, menuitem_dict['从文件导入'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.ipconfig_savetofile(), menuitem_dict['导出到文件'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.ipconfig_moddoc0(), menuitem_dict['修改配置说明'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.ipconfig_delete(), menuitem_dict['删除'])

    def on_loadconfig(self, event):
        """从文件导入配置，处理文件"""
        # print('_InputScpMainContextMenu__on_loadconfig')
        file = wx.FileSelector('选择配置文件')
        if file:
            try:
                cfname = os.path.basename(file)
                cfname = os.path.splitext(cfname)[0]
                with open(file, 'rb') as f:
                    text = f.read()
                if b'\x00' in text: text = text.replace(b'\x00', b'')
                try:
                    text = text.decode('utf-8')
                except UnicodeDecodeError:
                    text = text.decode('GBK', errors='replace')

                if '\r' in text: text = text.replace('\r', '')
                if '\'\'\'' in text:
                    doc = text.split('\'\'\'')[1]
                    print('-' * 20, doc, '-' * 20)
                else:
                    doc = ''
                temp1 = text.split('\'\'\'')[-1].replace(' ', '')
                temp2 = temp1.split('\n')
                config_list = []
                # print('temp2 ', temp2)
                for str_temp in temp2:
                    # print('str_temp ', str_temp)
                    if '\t' in str_temp:
                        templist = str_temp.split('\t')
                        if len(templist) == 4:
                            config_list.append(templist)
                        else:
                            assert False, '配置文件格式错误：\n%s' % str_temp
            except Exception as e:
                wx.LogError('文件出错： %s\n%s' % (file, str(e)))
            else:
                tempdic = {}
                for templist in config_list:
                    templist += [None]
                    templist[1] = eval(templist[1])  # 从字符串转为数据
                    name = templist.pop(0)
                    tempdic[name] = templist
                # print(tempdic)
                if tempdic:
                    self.mainobj.ipconfig_add(cfname, True, tempdic, doc)

    def on_saveconfig(event):
        ...


class InputScpBoolContextMenu(wx.Menu):
    """工况输入脚本配置布尔窗口的上下文菜单"""

    def __init__(self, mainobj, menutype=1, itemid=0, iteminform=()):
        # print('InputScpBoolContextMenu __init__')
        wx.Menu.__init__(self)
        self.mainobj = mainobj
        menuinit_list = [('新增布尔值', wx.ITEM_NORMAL, None), ('修改', wx.ITEM_NORMAL, None),
                         ('删除', wx.ITEM_NORMAL, None)]
        menuitem_dict = {}
        for x, y, z in menuinit_list:
            temp = wx.MenuItem(parentMenu=self, id=wx.ID_ANY, text=x, kind=y, subMenu=z)
            menuitem_dict[x] = temp
            if x in ['修改', '删除']: self.AppendSeparator()
            self.Append(temp)

        self.Bind(wx.EVT_MENU, lambda e: AddInputScpCfWin(self.mainobj.gui, type='bool', mainobj=self.mainobj),
                  menuitem_dict['新增布尔值'])
        self.Bind(wx.EVT_MENU,
                  lambda e: AddInputScpCfWin(self.mainobj.gui, type='bool', mainobj=self.mainobj,
                                             title='修改', modify=iteminform),
                  menuitem_dict['修改'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.ipconfig_delitem('bool', itemid, itemname=iteminform[0]),
                  menuitem_dict['删除'])

        if menutype == 1:  # 代表没有选中项目
            menuitem_dict['删除'].Enable(False)
            menuitem_dict['修改'].Enable(False)


class InputScpParamContextMenu(wx.Menu):
    """工况输入脚本配置数据窗口的上下文菜单"""

    def __init__(self, mainobj, menutype=1, itemid=0, iteminform=()):
        # print('InputScpParamContextMenu __init__')
        wx.Menu.__init__(self)
        self.mainobj = mainobj
        menuinit_list = [('新增数据', wx.ITEM_NORMAL, None), ('修改', wx.ITEM_NORMAL, None),
                         ('删除', wx.ITEM_NORMAL, None)]
        menuitem_dict = {}
        for x, y, z in menuinit_list:
            temp = wx.MenuItem(parentMenu=self, id=wx.ID_ANY, text=x, kind=y, subMenu=z)
            menuitem_dict[x] = temp
            if x in ['修改', '删除']: self.AppendSeparator()
            self.Append(temp)

        self.Bind(wx.EVT_MENU, lambda e: AddInputScpCfWin(self.mainobj.gui, type='param', mainobj=self.mainobj),
                  menuitem_dict['新增数据'])
        self.Bind(wx.EVT_MENU,
                  lambda e: AddInputScpCfWin(self.mainobj.gui, type='param', mainobj=self.mainobj,
                                             title='修改', modify=iteminform),
                  menuitem_dict['修改'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.ipconfig_delitem('param', itemid, itemname=iteminform[0]),
                  menuitem_dict['删除'])

        if menutype == 1:  # 代表没有选中项目
            menuitem_dict['删除'].Enable(False)
            menuitem_dict['修改'].Enable(False)


class OutputScpDirContextMenu(wx.Menu):
    """输出校验脚本文件目录窗口的上下文菜单"""

    def __init__(self, mainobj, filepath):
        # print('OutputScpDirContextMenu __init__')
        wx.Menu.__init__(self)
        self.mainobj = mainobj
        self.filepath = filepath
        menuinit_list = [('打开', wx.ITEM_NORMAL, None), ('刷新', wx.ITEM_NORMAL, None),
                         ('打开文件夹', wx.ITEM_NORMAL, None)]
        menuitem_dict = {}
        for x, y, z in menuinit_list:
            temp = wx.MenuItem(parentMenu=self, id=wx.ID_ANY, text=x, kind=y, subMenu=z)
            menuitem_dict[x] = temp
            if x in ['刷新', '打开文件夹']: self.AppendSeparator()
            self.Append(temp)

        self.Bind(wx.EVT_MENU, self.on_open, menuitem_dict['打开'])
        self.Bind(wx.EVT_MENU, self.on_refresh, menuitem_dict['刷新'])
        self.Bind(wx.EVT_MENU, self.on_opendir, menuitem_dict['打开文件夹'])

    def on_open(self, event):
        def open():
            rslt = os.system(self.filepath)
            if rslt:
                print('无法打开:%s' % self.filepath)

        thread0 = threading.Thread(target=open, daemon=True)
        thread0.start()

    def on_refresh(self, event):
        dir = os.path.dirname(self.filepath)
        self.mainobj.gui.right.refresh_opFileListWin(dir)

    def on_opendir(self, event):
        dir = os.path.dirname(self.filepath)
        open = lambda: os.startfile(dir)
        thread0 = threading.Thread(target=open, daemon=True)
        thread0.start()


class TreeWinContextMenu(wx.Menu):
    """树窗口的上下文菜单"""

    def __init__(self, mainobj):
        # print('TreeWinContextMenu __init__')
        wx.Menu.__init__(self)
        self.mainobj = mainobj
        menuinit_list = [('刷新', wx.ITEM_NORMAL, None), ('添加顶层文件夹', wx.ITEM_NORMAL, None),
                         ('添加文件夹', wx.ITEM_NORMAL, None), ('导入 工况输入脚本', wx.ITEM_NORMAL, None),
                         ('导入 输出校验脚本', wx.ITEM_NORMAL, None), ('新增 工况输入脚本', wx.ITEM_NORMAL, None),
                         ('新增 输出校验脚本', wx.ITEM_NORMAL, None), ('删除', wx.ITEM_NORMAL, None)]
        menuitem_dict = {}
        for x, y, z in menuinit_list:
            temp = wx.MenuItem(parentMenu=self, id=wx.ID_ANY, text=x, kind=y, subMenu=z)
            menuitem_dict[x] = temp
            if x in ['添加顶层文件夹', '导入 工况输入脚本', '新增 工况输入脚本', '删除']: self.AppendSeparator()
            self.Append(temp)

        self.Bind(wx.EVT_MENU, self.on_delete, menuitem_dict['删除'])
        self.Bind(wx.EVT_MENU, self.on_addinputscp, menuitem_dict['导入 工况输入脚本'])
        self.Bind(wx.EVT_MENU, self.on_addoutputscp, menuitem_dict['导入 输出校验脚本'])
        self.Bind(wx.EVT_MENU, self.on_addfolder, menuitem_dict['添加文件夹'])
        self.Bind(wx.EVT_MENU, self.on_addtopfolder, menuitem_dict['添加顶层文件夹'])
        self.Bind(wx.EVT_MENU, self.on_refresh, menuitem_dict['刷新'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.tree_adddemoscp(SCPTYPE_INPUT), menuitem_dict['新增 工况输入脚本'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.tree_adddemoscp(SCPTYPE_OUTPUT), menuitem_dict['新增 输出校验脚本'])

    def on_delete(self, event):
        self.mainobj.tree_delete()

    def on_addinputscp(self, event):
        self.mainobj.tree_add(SCPTYPE_INPUT)

    def on_addoutputscp(self, event):
        self.mainobj.tree_add(SCPTYPE_OUTPUT)

    def on_addfolder(self, event):
        self.mainobj.tree_add(SCPTYPE_FOLDER)

    def on_addtopfolder(self, event):
        self.mainobj.tree_addtopfolder()

    def on_refresh(self, event):
        self.mainobj.tree_refresh()


class DbCtrlContextMenu(wx.Menu):
    """脚本库的上下文菜单"""

    def __init__(self, mainobj):
        # print('DbCtrlContextMenu __init__')
        wx.Menu.__init__(self)
        self.mainobj = mainobj
        menuinit_list = [('重命名', wx.ITEM_NORMAL, None), ('新增脚本库', wx.ITEM_NORMAL, None),
                         ('删除脚本库', wx.ITEM_NORMAL, None)]
        menuitem_dict = {}
        for x, y, z in menuinit_list:
            temp = wx.MenuItem(parentMenu=self, id=wx.ID_ANY, text=x, kind=y, subMenu=z)
            menuitem_dict[x] = temp
            if x in ['新增脚本库', '删除脚本库']: self.AppendSeparator()
            self.Append(temp)

        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.database_rename(), menuitem_dict['重命名'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.database_add(), menuitem_dict['新增脚本库'])
        self.Bind(wx.EVT_MENU, lambda e: self.mainobj.database_delete(), menuitem_dict['删除脚本库'])


class AddInputScpCfWin(wx.Frame):
    """工况输入脚本配置新增/修改变量的窗口"""

    def __init__(self, parent=None, type='bool', size=(400, 210), title='新增变量', mainobj=None, modify=()):
        wx.Frame.__init__(self, parent, size=size, title=title,style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.mainobj = mainobj

        self.pl = wx.Panel(self, size=(400, 210))

        editable = ['name', 'value', 'unit', 'notes']  # 可编辑的文本框
        statictext0 = ['变量名', '值', '单位', '备注']
        textctrl_dic0 = {'name': {'name': '变量名', 'size': (80, 26), 'style': wx.TE_PROCESS_ENTER},
                         'value': {'name': '值', 'size': (80, 26), 'style': wx.TE_PROCESS_ENTER},
                         'unit': {'name': '单位', 'size': (80, 26), 'style': wx.TE_PROCESS_ENTER},
                         'notes': {'name': '备注', 'style': wx.TE_PROCESS_ENTER}}
        if type == 'bool':
            textctrl_dic0['unit']['value'] = 'bool'
            textctrl_dic0['unit']['style'] = wx.TE_READONLY  # 不可编辑
            editable.remove('unit')
            textctrl_dic0['value']['value'] = '1'
        if modify:  # 修改变量
            textctrl_dic0['name']['value'] = modify[0]
            textctrl_dic0['name']['style'] = wx.TE_READONLY
            editable.remove('name')
            v, u, n, _ = modify[1]
            if type == 'bool': v = 1 if u else 0
            textctrl_dic0['value']['value'] = str(v)
            textctrl_dic0['unit']['value'] = u
            textctrl_dic0['notes']['value'] = n
        self.textctrl_dic = {}
        for key, val in textctrl_dic0.items():
            self.textctrl_dic[key] = wx.TextCtrl(self.pl, **val)
        self.statictext = {}
        for text in statictext0:
            self.statictext[text] = wx.StaticText(self.pl, label=text, style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.btconfirm = wx.Button(self.pl, label='确认', size=(35, 35))
        self.btcancel = wx.Button(self.pl, label='取消', size=(35, 35))

        self.sizer = wx.GridBagSizer(6, 6)

        temp = wx.EXPAND
        self.sizer.Add(self.statictext['变量名'], pos=(0, 0), span=(1, 1), flag=temp | wx.TOP, border=10)
        self.sizer.Add(self.statictext['值'], pos=(0, 1), span=(1, 1), flag=temp | wx.TOP, border=10)
        self.sizer.Add(self.statictext['单位'], pos=(0, 2), span=(1, 1), flag=temp | wx.TOP, border=10)
        self.sizer.Add(self.textctrl_dic['name'], pos=(1, 0), span=(1, 1), flag=temp | wx.LEFT, border=4)
        self.sizer.Add(self.textctrl_dic['value'], pos=(1, 1), span=(1, 1))
        self.sizer.Add(self.textctrl_dic['unit'], pos=(1, 2), span=(1, 1), flag=temp | wx.RIGHT, border=4)
        self.sizer.Add(self.statictext['备注'], pos=(2, 0), span=(1, 3), flag=temp)
        self.sizer.Add(self.textctrl_dic['notes'], pos=(3, 0), span=(1, 3), flag=temp | wx.RIGHT | wx.LEFT, border=4)
        self.sizer.Add(self.btconfirm, pos=(4, 1), span=(1, 1), flag=temp)
        self.sizer.Add(self.btcancel, pos=(4, 2), span=(1, 1), flag=temp | wx.RIGHT, border=4)
        self.sizer.AddGrowableCol(0)
        self.pl.SetSizer(self.sizer)

        self.btconfirm.Bind(wx.EVT_BUTTON, self.on_confirm)
        self.btcancel.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        for key in editable:
            self.textctrl_dic[key].Bind(wx.EVT_TEXT_ENTER, self.on_confirm)

        self.Centre()
        self.Show()

    def on_confirm(self, event):
        name = self.textctrl_dic['name'].GetValue()
        value = self.textctrl_dic['value'].GetValue()
        unit = self.textctrl_dic['unit'].GetValue()
        notes = self.textctrl_dic['notes'].GetValue()
        if name and value:
            self.mainobj.ipconfig_additem(name, eval(value), unit, notes)
            self.Close()


class ModInputScpCfDoc(wx.Frame):
    """修改输入脚本配置说明的窗口"""

    def __init__(self, parent=None, size=(500, 300), title='修改配置说明', mainobj=None, text=''):
        wx.Frame.__init__(self, parent, size=size, title=title)
        self.mainobj = mainobj

        self.pl = wx.Panel(self, size=(500, 300))

        self.textwin = wx.TextCtrl(self.pl, style=wx.TE_MULTILINE)
        self.btconfirm = wx.Button(self.pl, label='确认', size=(60, 35))
        self.btcancel = wx.Button(self.pl, label='取消', size=(60, 35))

        self.sizer = wx.GridBagSizer(6, 6)
        self.sizer.Add(self.textwin, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        self.sizer.Add(self.btconfirm, pos=(1, 1), span=(1, 1), flag=wx.ALL, border=10)
        self.sizer.Add(self.btcancel, pos=(1, 2), span=(1, 1), flag=wx.ALL, border=10)

        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
        self.pl.SetSizer(self.sizer)

        self.textwin.ChangeValue(text)

        self.btconfirm.Bind(wx.EVT_BUTTON, self.on_confirm)
        self.btcancel.Bind(wx.EVT_BUTTON, lambda e: self.Close())

        self.Centre()
        self.Show()

    def on_confirm(self, event):
        self.mainobj.ipconfig_moddoc(self.textwin.GetValue())
        self.Close()


class FindCodeStringWin(wx.Frame):
    """在代码内查找字符串的窗口"""

    def __init__(self, parent=None, size=(400, 240), title='查找', codewin=None,
                 style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT):
        wx.Frame.__init__(self, parent, size=size, title=title, style=style)
        self.codewin = codewin
        self.rslt = None

        self.CreateStatusBar()
        self.pl = wx.Panel(self, size=(400, 240))

        self.textwin = wx.TextCtrl(self.pl)
        self.btconfirm = wx.Button(self.pl, label='查找', size=(48, 32))
        self.radio = wx.RadioBox(self.pl, label='查找方式', choices=['常规', '正则表达式'])
        self.check = {}
        self.check['大小写'] = wx.CheckBox(self.pl, label='区分大小写')
        self.check['全词匹配'] = wx.CheckBox(self.pl, label='全词匹配')

        self.sizer = wx.GridBagSizer(6, 6)
        self.sizer.Add(self.textwin, pos=(0, 0), span=(1, 1), border=6, flag=wx.EXPAND | wx.ALL)
        self.sizer.Add(self.btconfirm, pos=(0, 1), span=(1, 1), border=6, flag=wx.ALL)
        self.sizer.Add(self.radio, pos=(1, 0), span=(1, 1), border=6, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        self.sizer.Add(self.check['大小写'], pos=(2, 0), span=(1, 1), border=6, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        self.sizer.Add(self.check['全词匹配'], pos=(3, 0), span=(1, 1), border=6, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)

        self.sizer.AddGrowableCol(0)
        self.pl.SetSizer(self.sizer)

        self.btconfirm.Bind(wx.EVT_BUTTON, self.on_confirm)

        self.textwin.SetFocus()

        self.Centre()
        self.Show()

    def on_confirm(self, event):
        text = self.textwin.GetValue()
        if text:
            if self.rslt == None or self.rslt == (-1, -1):
                start = 0
            else:
                start = self.rslt[1]
            if self.radio.GetSelection() == 0:
                flags = wx.stc.STC_FIND_POSIX
                if self.check['大小写'].GetValue(): flags |= wx.stc.STC_FIND_MATCHCASE
                if self.check['全词匹配'].GetValue(): flags |= wx.stc.STC_FIND_MATCHCASE
            else:
                flags = wx.stc.STC_FIND_REGEXP

            rslt = self.codewin.FindText(start, self.codewin.GetLength(), text, flags=flags)
            if rslt == (-1, -1):
                if start == 0:
                    self.SetStatusText('  "%s"  找不到!!!  ' % text)
                    self.rslt = rslt
                else:
                    self.rslt = rslt
                    self.on_confirm(None)  # 再从头找一次
            else:
                self.SetStatusText('')
                self.codewin.SelectNone()
                self.codewin.SetSelection(*rslt)
                self.codewin.ScrollRange(*rslt)
                self.rslt = rslt


class HtmlWin(wx.Frame):
    """HTML窗口"""

    def __init__(self, parent=None, title='HtmlWin', mainobj=None, text=''):
        wx.Frame.__init__(self, parent=parent, title=title, size=(1300, 700))
        self.mainobj = mainobj

        self.html = wx.html.HtmlWindow(self)
        self.toolbar = wx.ToolBar(self)
        self.sourse = text

        self.SetToolBar(self.toolbar)
        self.toolinit = [('添加变量', IMGNight.GetBitmap(), '添加变量到INCA实验环境', wx.ITEM_NORMAL)]
        self.tooldic = {}
        self.tooldic['保存'] = self.toolbar.AddTool(0, 'a', IMGFolder.GetBitmap(),
                                                  shortHelp='保存到文件', kind=wx.ITEM_NORMAL)
        self.toolbar.Realize()

        self.html.SetPage(text)
        self.html.SetStandardFonts(14, '黑体')
        self.Bind(wx.EVT_TOOL, self.on_save, self.tooldic['保存'])

        self.Centre()
        self.Layout()
        self.Show()

    def on_save(self, event):
        while True:
            path = wx.SaveFileSelector('', 'html文件(*.html)|*.html', '变量信息.html')
            if path and os.path.exists(path):
                affirm = wx.MessageBox('名称重复,确认要覆盖"%s"吗 ?? ' % os.path.basename(path), style=wx.YES_NO)
                if affirm == wx.YES:
                    break
            else:
                break
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.sourse)
            wx.LogMessage('保存成功')


#################### 非GUI #########################
class DataBase:
    def __init__(self, name):
        self.name = name
        self.tree_dic = {}
        self.config_dic = {}
        self.code_dic = {}

    name = ''
    tree_dic = {}  # 'scpname':(Type(int) , Id(int) , 占位列表( [None] ))
    config_dic = {}  # id : dict( 'configname':configobj , ... )
    code_dic = {}  # id : code(string)


class ScpManageState:
    def __init__(self):
        self.database = ''
        self.work_path = os.getcwd()
        self.script = {'active': False,
                       'name': None,
                       'id': None,
                       'type': None,
                       'path': [],
                       'config': None}
        # 'active': bool , 'name':string , 'id':int ,'type':SCPTYPE_INPUT or SCPTYPE_OUTPUT , 'path':[] , 'config':string
        self.swconfig = {'testPanelCtrlMode': 1, 'serialCOM': 'COM6'}  # 软件配置
        self.version = 100  # 代表1.00
        self.opscppath = ''

    database = ''
    work_path = os.getcwd()
    script = {'active': False, 'name': None, 'id': None, 'type': None, 'path': [], 'config': None}
    swconfig = {'testPanelCtrlMode': 1}
    version = 100
    opscppath = ''

    def set_database(self, text):
        self.database = text

    def set_script(self, **kwargs):
        for key, val in kwargs.items():
            self.script.__setitem__(key, val)

    def init_script(self):
        self.script = {'active': False, 'name': None, 'id': None, 'type': None, 'path': [], 'config': None}


class InputConfig:
    """输入脚本"""
    # self.demo = [ 5 , 'ms' ,' 备注 ',None]    #列表中分别为值、单位、备注、保留位
    pass


class OutputConfig:
    """输出脚本"""

    def __init__(self):
        self.loaddir = ''
        self.mdfperiodmode = 0  # 0 代表采用文件本身的数据采样周期,如'Task10ms'， 1 代表采用自定义的数据采用周期
        self.mdfsysperiod = 'Task10ms'  # 文件本身的采用周期
        self.mdfcustomperiod = 0.01  # 自定义的采用周期，单位:s

    loaddir = ''
    mdfperiodmode = 0
    mdfsysperiod = 'Task10ms'
    mdfcustomperiod = 0.01


class ExitableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

    def getid(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def exit(self):
        thread_id = self.getid()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)


class InpuScpRunThread(ExitableThread):
    def __init__(self, mainobj, *args, **kwargs):
        ExitableThread.__init__(self, *args, **kwargs)
        self.mainobj = mainobj

    def initfunc(self, func, ins, evt, kwargs=None, cycle=False, cycleperiod=0.01):
        self.myfunc = func
        self.myargs = (ins, evt, self.userexit)
        self.mykwargs = kwargs
        self.ins = ins
        self.cycle = cycle
        self.cycleperiod = cycleperiod
        self.Run = True
        if cycle: print('  函数周期 >> %.0f ms' % (cycleperiod * 1000))

    def run(self):
        if self.cycle:
            t0 = self.cycleperiod
            t1 = t0 / 100
            try:
                while self.Run:
                    self.thson = ExitableThread(target=self.myfunc, args=self.myargs, kwargs=self.mykwargs, daemon=True)
                    self.thson.start()
                    time.sleep(t0)
                    while self.thson.isAlive():
                        time.sleep(t1)
            except Exception as e:
                self.exitdeal()
                raise e
            else:
                self.exitdeal()
        else:
            try:
                if self.mykwargs:
                    self.myfunc(*self.myargs, **self.mykwargs)
                else:
                    self.myfunc(*self.myargs)
            except Exception as e:
                self.exitdeal()
                raise e
            else:
                self.exitdeal()

    def userexit(self):
        self.Run = False

    def exit(self):
        if self.cycle:
            self.thson.exit()
        ExitableThread.exit(self)
        self.exitdeal()

    def exitdeal(self):
        self.ins.all_reset()
        print('-' * 20, '输入脚本运行结束', '-' * 20)
        self.mainobj.gui.right.bt_ipscpstop.Disable()
        self.mainobj.gui.right.bt['运行脚本'].Enable()


class InputScpRunState:
    """输入脚本运行状态"""
    stat = 1
    functioncycle = False
    functioncycleperiod = 0.01  # 秒


class OutputScpRun:
    def __init__(self, func_init, func_calc, func_name=None, **cf):
        self.cf = deepcopy(OutputScpRun.cf)
        self.cf.update(cf)  # 配置
        self.ins = _insc.IncaControl()
        self.ins.init()
        self.ins.a2l_init(self.cf['device_name'])
        self.evt = OutputScpRunState()
        self.p = Output_val()
        self.func_init = func_init
        self.func_calc = func_calc
        self.func_name = func_name  # getcali_mode==2 时可以不用

    cf = {'device_name': 'CCP: 1', 'getcali_mode': 2, 'datafiletype': 'mdf',
          'mdf_period': 'Task10ms', 'mdf_resampleraster': 0.0}  # 配置

    # 'getcali_mode': 1 or 2 ,2 代表脚本运行时从INCA实验环境动态获取标定量
    # 'datafiletype': ’mdf' or 'ascii' ,数据文件类型
    # 'mdf_period': 如'Task10ms','Task100ms'等 ,代表获取mdf文件中该采样率下的测量数据组，以该组的时间戳为迭代器循环运行脚本
    # 'mdf_resampleraster‘:如0.01s, 非0时会将mdf文件内的所有数据重置采样率

    def read_asciifile(self, filepath):
        evt = self.evt
        read_state = 0
        rowidx = 0
        for line in open(filepath, 'r'):
            line = line.rstrip()

            if read_state == 5:  # 读取数据
                rowlist = line.split('\t')
                assert len(rowlist) == len(evt.TDN), 'ascii格式错误：%d 该行的数据列数不等于变量名称数' % (rowidx)
                for colidx, name in enumerate(evt.TDN):
                    evt.TD[name][rowidx] = eval(rowlist[colidx])
                rowidx += 1

            elif read_state == 0:  # 读取头部信息
                evt.ascii_head = line
                read_state = 1

            elif read_state == 1:  # 读取采样计数
                rowlist = line.split('\t')
                if rowlist[0].strip() == 'sampleCount':
                    evt.samplecnt = eval(rowlist[1])
                else:
                    assert False, 'ascii格式错误: line 2 '
                read_state = 2

            elif read_state == 2:  # 读取名称
                rowlist = line.split('\t')
                for colidx, name in enumerate(rowlist):
                    templist = name.split('\\')
                    rowlist[colidx] = templist[0]
                evt.TDN = rowlist.copy()
                evt.measNameList = rowlist.copy()
                evt.measNameList.remove('time')
                for name in evt.TDN:
                    evt.TD[name] = [0] * evt.samplecnt
                read_state = 3

            elif read_state == 3:  # 读取类型
                evt.TDType = line.split('\t')
                read_state = 4
            elif read_state == 4:  # 读取数据单位
                evt.TDUnit = line.split('\t')
                read_state = 5

        evt.TDCnt = len(evt.TD[evt.TDN[0]])
        assert evt.TDCnt == evt.samplecnt, 'ascii格式错误：sampleCount与实际数据行数不一致'

    def write_asciifile(self, filepath):
        evt = self.evt

        TDN = [name + '_p' for name in evt.TDN_p]
        TDN = evt.TDN + TDN
        TD = {key + '_p': val for key, val in evt.TD_p.items()}
        TD.update(evt.TD)

        with open(filepath, 'w') as f:

            f.write('%s\nsampleCount\t%d\n' % (evt.ascii_head, evt.samplecnt))

            # 打印名称行
            f.write('time\t')
            templist = TDN.copy()
            templist.remove('time')
            f.write('\\CCP:1\t'.join(templist))
            f.write('\\CCP:1')
            f.write('\n')

            # 打印类型行
            f.write('\t'.join(evt.TDType))
            templen = len(TDN) - len(evt.TDType)
            if templen:
                f.write('\t')
                templist = ['f8'] * templen
                f.write('\t'.join(templist))
            f.write('\n')

            # 打印单位行
            f.write('\t'.join(evt.TDUnit))
            templen = len(TDN) - len(evt.TDUnit)
            if templen:
                f.write('\t')
                templist = ['"-"'] * templen
                f.write('\t'.join(templist))
            f.write('\n')

            # 打印数据行
            templist = []
            for idx in range(evt.TDCnt):
                temp = [str(TD[name][idx]) for name in TDN]
                templist.append('\t'.join(temp))
            f.write('\n'.join(templist))
        print('ascii文件保存到 %s' % filepath)

    def init_userData(self):
        """将用户定义的结果名称和结果数据添加到相应的列表和字典中"""
        evt = self.evt
        for name, result_value in self.p.__dict__.items():
            if isinstance(result_value, list):
                for x in range(len(result_value)):
                    name = '%s_[%d]' % (name, x)
                    evt.TDN_p.append(name)
                    evt.TD_p[name] = [0] * evt.TDCnt
            else:
                evt.TDN_p.append(name)
                evt.TD_p[name] = [0] * evt.TDCnt

    def update_userData(self, p, idx):
        """将用户定义的结果数据写到evt.TD_p字典里"""
        evt = self.evt
        for name, value in p.__dict__.items():
            if isinstance(value, list):
                for i, x in enumerate(value):
                    name = '%s_[%d]' % (name, i)
                    evt.TD_p[name][idx] = x
            else:
                evt.TD_p[name][idx] = value

    def update_TDfromscalar(self, dic):
        """将标定量加入到变量数据里"""
        evt = self.evt
        if dic:
            for name, scalar_value in dic.items():
                evt.TDN.append(name)
                evt.TD[name] = [scalar_value] * evt.TDCnt
                unit = self.ins.a2l.GetCharacteristicNamed(name).GetCompuMethod().GetUnit()
                evt.TDUnit.append('"%s"' % unit)

    def refresh_caliValueDict(self):
        evt = self.evt
        for name in evt.scalarNameList:
            evt.scalarValueDict[name] = self.ins.cget(name)
            evt.scalarValueDict_d[name] = self.ins.cget_d_int(name)  # 机器值
        for name in evt.oneDTableNameList:
            evt.oneDTableValueDict[name] = self.ins.tabget(name)
            evt.oneDTableValueDict_d[name] = self.ins.tabget_d_int(name)
        for name in evt.twoDTableNameList:
            evt.twoDTableValueDict[name] = self.ins.tabget(name)
            evt.twoDTableValueDict_d[name] = self.ins.tabget_d_int(name)

    def getmeasValueTransFormula(self, name):
        """返回 测量量 的 转换公式(函数对象)"""
        mear = self.ins.a2l.GetMeasurementNamed(name)
        if mear == None:
            if re.match('[\w]+_\[[0-9]+(])$', name):  # like XXX_[16]
                name = re.findall('[\w]+(?=_\[[0-9]+])', name)[0]
            mear = self.ins.a2l.GetMeasurementNamed(name)
        if not mear:
            print('寻找测量量转换公式时出错：INCA找不到"%s"' % name)
            return lambda v: v
        compu_method = mear.GetCompuMethod()
        conver_type = compu_method.GetConversionType()
        if conver_type == 'Linear':
            c, b = compu_method.GetParameterValues()
            return lambda v: int(round(b * v + c))
        elif conver_type == 'Identity':
            return lambda v: int(round(v))
        elif conver_type == 'TAB_VERB':
            hextuple = compu_method.GetHexTab()
            verbtuple = compu_method.GetVerbalTab()
            transdic = dict(zip(verbtuple, hextuple))
            print('transdic', transdic)
            return lambda v: transdic.get(v)
        elif conver_type == 'Moebius':
            a, b, c, d, e, f = compu_method.FormulaCoefficients()
            if a == 0 and d == 0:
                return lambda v: int(round((b * v + c) / (e * v + f)))
            else:
                return lambda v: int(round((a * v ** 2 + b * v + c) / (d * v ** 2 + e * v + f)))
        else:
            assert False, '"%s"的转换方式"%s"未定义' % (name, conver_type)

    def refresh_measTransDict(self):
        # print('measnamelist', self.evt.measNameList)
        for name in self.evt.measNameList:
            self.evt.measTransDict[name] = self.getmeasValueTransFormula(name)

    def refresh_measValue(self, MV, idx):
        evt = self.evt
        MV['time'] = evt.TD['time'][idx]
        for name in evt.measNameList:
            phy = evt.TD[name][idx]
            MV[name] = phy
            MV[name + ' d'] = evt.measTransDict[name](phy)

    def refresh_caliValue(self):
        evt = self.evt
        SV = {key + ' d': val for key, val in evt.scalarValueDict_d.items()}
        SV.update(evt.scalarValueDict)
        D1V = {key + ' d': val for key, val in evt.oneDTableValueDict_d.items()}
        D1V.update(evt.oneDTableValueDict)
        D2V = {key + ' d': val for key, val in evt.twoDTableValueDict_d.items()}
        D2V.update(evt.twoDTableValueDict)
        return SV, D1V, D2V

    def read_mdffile(self, path):
        file = asammdf.MDF(path)
        MV = MeasDataSet(file, self.cf['mdf_period'], self.cf['mdf_resampleraster'])
        return MV._file, MV

    def update_mdffromscalar(self, scalardic, timefirst, timeend):
        sigs = []
        timestamps = [timefirst, timeend]
        for key, val in scalardic.items():
            if not self.mdffile.whereis(key):  # 如果没有记录该单参标定
                sig = asammdf.Signal([val, val], timestamps, name=key)
                sigs.append(sig)
        if sigs: self.mdffile.append(sigs, acq_name='PythonScalar', common_timebase=True)

    def write_mdffile(self, path, userdata, timestamps):
        sigs = []
        for key, val in userdata.items():
            sig = asammdf.Signal(val, timestamps, name=key + '_p')
            sigs.append(sig)
        if sigs: self.mdffile.append(sigs, acq_name='PythonMeasure', common_timebase=True)
        self.mdffile.save(path, overwrite=True)
        self.mdffile.close()
        os.rename(path, os.path.splitext(path)[0] + '.dat')  # asammdf包会自动将文件后缀改为.mdf,故在此再重命名为.dat后缀

    def gk_init(self, rowcnt):
        self.evt._gk_data = [set() for i in range(rowcnt)]  # 每一个元素是一个集合,每个集合代表对应行的工况点
        self.evt._rowidx = 0

    def gk_analyse(self, evt):
        """分析工况情况"""
        allgks = reduce(lambda a, b: a | b, evt._gk_data)
        allgks_str = {evt._gk_int2str[id] for id in allgks}
        gknum = len(allgks)
        if gknum > evt.gkcount: print('    evt.gkcount 设置错误 !!')
        gkcoverage = Fraction(gknum, evt.gkcount)

        t0 = time.time()
        gkrange = {}  # { gkname(string):某种工况点覆盖的范围(list) , ... }
        for gkstr, gkid in evt._gk_str2int.items():
            templist = [rowidx for rowidx, gkset in enumerate(evt._gk_data) if gkid in gkset]  # 某一工况达到的所有行
            tempset = set(templist)  # 判断集合的包含关系比列表快
            if len(templist) == 1:
                gkrange[gkstr] = [(templist[0], templist[0])]
                continue
            rangelist = []  # 例如:将[4, 5, 6, 9, 10, 15, 16, 17, 18, 27]转为[(4, 6), (9, 10), (15, 18), (27, 27)]
            begin = templist[0]
            setbegin = False
            gkskip = evt._gk_skip
            for row in range(begin, evt.TDCnt):
                if row + 1 in gkskip: continue
                if setbegin:
                    if row in tempset:
                        begin = row
                        setbegin = False
                elif row + 1 not in tempset:
                    rangelist.append((begin, row))
                    setbegin = True
            gkrange[gkstr] = rangelist
        print(time.time() - t0)

        gkdata = OrderedDict()  # 将工况数据缩减大小,将格式改为{ (起始行,结束行):工况id集合 , ... }
        if evt._gk_data:
            begin = 0
            rowidx = 0
            gkset_sourse = evt._gk_data[0]
            for rowidx, gkset in enumerate(evt._gk_data):
                if gkset != gkset_sourse:
                    gkdata[(begin, rowidx - 1)] = gkset_sourse
                    gkset_sourse = gkset
                    begin = rowidx
            gkdata[(begin, rowidx)] = gkset_sourse
        print('   ......... 工况覆盖度 ........')
        if gkcoverage != Fraction(1, 1):
            print('   ', gkcoverage, end='')
        print('   ', '%.0f%s' % (float(gkcoverage) * 100, '%'))
        print('  ', '.' * 40)
        print('   ......... 达到的工况 ........')
        pprint(dict(enumerate(sorted(allgks_str), 1)))
        print('  ', '.' * 40)
        # pprint(gkrange)
        # print('+++++++')
        # pprint(gkdata)

    def run(self, loadpath, savepath):
        """脚本运行"""
        if self.cf['datafiletype'] == 'ascii':
            self.read_asciifile(loadpath)
            self.refresh_measTransDict()
            MV = {}
            self.refresh_measValue(MV, 0)
        else:
            self.mdffile, MV = self.read_mdffile(loadpath)
            self.evt.TDCnt=len(MV._timestamps)
            MV._rowidx = 0

        self.gk_init(self.evt.TDCnt)

        if self.cf['getcali_mode'] == 1:
            self.func_name(self.evt)
            self.refresh_caliValueDict()
            SV, D1V, D2V = self.refresh_caliValue()
        else:
            SV = CaliDataSet(self.ins, 1)
            D1V = CaliDataSet(self.ins, 2)
            D2V = CaliDataSet(self.ins, 2)

        self.func_init(self.evt, MV, SV, D1V, D2V, self.p)
        self.func_calc(self.evt, MV, SV, D1V, D2V, self.p)
        self.init_userData()

        self.func_init(self.evt, MV, SV, D1V, D2V, self.p)

        if self.cf['datafiletype'] == 'ascii':
            refresh_MV = self.refresh_measValue
        else:
            refresh_MV = lambda MV, idx: setattr(MV, '_rowidx', idx)

        for idx in range(self.evt.TDCnt):
            self.evt._rowidx = idx
            refresh_MV(MV, idx)
            self.func_calc(self.evt, MV, SV, D1V, D2V, self.p)
            self.update_userData(self.p, idx)

        self.gk_analyse(self.evt)

        tempdic = self.evt.scalarValueDict if self.cf['getcali_mode'] == 1 else SV._dic
        if self.cf['datafiletype'] == 'ascii':
            self.update_TDfromscalar(tempdic)
            self.write_asciifile(savepath)
        else:
            self.update_mdffromscalar(tempdic, MV._timestamps[0], MV._timestamps[-1])
            self.write_mdffile(savepath, self.evt.TD_p, MV._timestamps)


class OutputScpRunState(object):

    def __init__(self):
        self.measNameList = []  # 导入文件时的所有测量量(不包括time)
        self.scalarNameList = []
        self.oneDTableNameList = []
        self.twoDTableNameList = []

        self.measTransDict = {}

        self.scalarValueDict = {}
        self.scalarValueDict_d = {}
        self.oneDTableValueDict = {}
        self.oneDTableValueDict_d = {}
        self.twoDTableValueDict = {}
        self.twoDTableValueDict_d = {}
        # 读取INCA监控数据的文本格式文件产生的变量
        self.TDType = []
        self.TDUnit = []
        self.TDN = []
        self.TDN_p = []  # 输出变量名称
        self.TD = {}
        self.TD_p = {}  # 输出变量数据
        self.TDCnt = 0  # 数据文件采样数
        self.samplecnt = 0  # ascii采样计数，与TDCnt相等
        self.ascii_head = ''

        self.gkcount = 1  # 工况点总数
        self._gk_str2int = {}  # string:integer
        self._gk_int2str = {}  # integer:string
        self._gk_data = []  # 每一个元素是一个集合,每个集合代表对应行的工况点
        self._gk_skip = set()  # 跳过对某些行进行工况条件的分析
        self._rowidx = 0

    def gk(self, text: str):
        try:
            gkid = self._gk_str2int[text]
        except KeyError:
            gkid = len(self._gk_str2int)
            self._gk_str2int[text] = gkid
            self._gk_int2str[gkid] = text
        self._gk_data[self._rowidx].add(gkid)

    def gkskip(self):
        self._gk_skip.add(self._rowidx)


class Output_val: pass


class CaliDataSet:
    """动态的标定量字典，如果查找字典中不存在的键，会动态地生成标定量数据"""

    def __init__(self, ins, mod=1):
        self.ins = ins

        def get(key):
            elemt = self.ins.exp.GetCalibrationElement(key)
            if not elemt: raise KeyError(' %s 不是INCA标定量' % key)
            return (elemt.GetValue().GetDoublePhysValue(),  # 物理值
                    elemt.GetValue().GetLongImplValue(),  # 机器值
                    elemt.GetAsap2Label().GetCompuMethod().GetUnit())  # 单位

        def get_tab(key):
            return (self.ins.tabget(key),
                    self.ins.tabget_d_int(key),
                    self.ins.a2l.GetCharacteristicNamed(key).GetCompuMethod().GetUnit())

        self._func = get if mod == 1 else get_tab
        self._dic = {}
        self._dic_d = {}
        self._dic_unit = {}
        self._allkeys = None

    def __getitem__(self, key):
        try:
            if key.endswith(' d'):
                return self._dic_d[key[:-2]]
            else:
                return self._dic[key]
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        keyraw = key[:-2] if key.endswith(' d') else key
        phy, dec, unit = self._func(keyraw)
        self._dic[keyraw] = phy
        self._dic_d[keyraw] = dec
        self._dic_unit[keyraw] = unit
        if keyraw == key:
            return phy
        else:
            return dec

    def __str__(self):
        return 'calibration phy: {0:s}\n{1:12s}dec: {2:s}\n{1:12s}unit: {3:s}'.format(
            str(self._dic), ' ', str(self._dic_d), str(self._dic_unit))

    def __copy__(self):
        return deepcopy(self)

    def __iter__(self):
        dic = {key + ' d': val for key, val in self._dic_d.items()}
        dic.update(self._dic)
        return iter(dic)

    def keys(self):
        if self._allkeys == None:
            self._allkeys = self.ins.a2l.GetAllElementNamesOfType('allCharacteristics')
        return self._allkeys

    def __contains__(self, key):
        return key in self.keys()

    def __bool__(self):
        return bool(self.keys())

    def items(self):
        raise AttributeError('SV D1V D2V 没有items()方法')

    def values(self):
        raise AttributeError('SV D1V D2V 没有values()方法')


class MeasDataSet:
    """伪字典，从MDF文件中动态获取测量量数据"""

    def __init__(self, mdffile, period='Task10ms', resampleraster: float = 0.0):
        self._rowidx = 0
        self._dic = {}
        self._dic_d = {}
        self._fileinfo = mdffile.info()
        self._resampleraster = resampleraster
        self._group = 0

        if resampleraster:
            self._file = mdffile.resample(resampleraster, time_from_zero=True)  # 重新取样,以resampleraster为周期，单位:s
            self._timestamps = self._file.get_master(0)
            self._dic['time'] = deepcopy(self._timestamps)
        else:
            self._file = mdffile

        cnt = 0
        maxrows=0
        maxrowgroup=0
        for idx in range(self._fileinfo['groups']):
            groupdic = self._fileinfo['group ' + str(idx)]
            if groupdic['cycles']>maxrows:
                maxrows=groupdic['cycles']
                maxrowgroup=idx
            if resampleraster:
                if groupdic['channels count'] > cnt:
                    cnt = groupdic['channels count']
                    self._group = idx # 重采样时选择变量数量最多的组作为默认组
            elif groupdic['comment'] == period:
                self._group = idx
                self._timestamps = mdffile.get_master(idx)
                self._dic['time'] = deepcopy(self._timestamps)
                break
        else:
            if not resampleraster: #找不到采样率时取行数(采样数)最多的组作为默认组
                self._group = maxrowgroup
                self._timestamps = mdffile.get_master(maxrowgroup)
                self._dic['time'] = deepcopy(self._timestamps)
                print('    找不到采样率:"%s"' % period)

    def __getitem__(self, key):
        if key.endswith(' d'):  # 机器值
            try:
                return self._dic_d[key[:-2]][self._rowidx]
            except KeyError:
                return self.__missing__(key[:-2], phymod=False)
        else:  # 物理值
            try:
                return self._dic[key][self._rowidx]
            except KeyError:
                return self.__missing__(key, phymod=True)

    def __missing__(self, key, phymod=True):
        sig = None
        try:
            sig = self._file.get(key, self._group, raw=True)
        except asammdf.blocks.utils.MdfException:  # 在设定采样率的group下找不到时，会去其它group寻找
            positions = self._file.whereis(key)
            if positions:
                for pos in positions:
                    sig = self._file.get(group=pos[0], index=pos[1], raw=True)
                    if not 'ramcal' in sig.name.split('\\')[1].lower():  # 不要RAMCal分组下的测量量
                        if not self._resampleraster:
                            sig = sig.interp(self._timestamps)
                        break
                else:
                    raise KeyError('不存在的测量量:"%s"' % key)
            else:
                raise KeyError('不存在的测量量:"%s"' % key)

        sigsamples = sig.samples.astype(int)
        sigsamplesphy = sig.physical().samples.astype(float)
        self._dic_d[key] = sigsamples
        self._dic[key] = sigsamplesphy

        if phymod:
            return sigsamplesphy[self._rowidx]
        else:
            return sigsamples[self._rowidx]


########################################## 函数 ####################################################
def update_software(software_path, mainobj):
    update_path = wx.FileSelector('选择更新包')
    if update_path:
        ...
    ...


def run_software():
    myapp = ScriptManage()
    myapp.app.MainLoop()


######################################### scpdemo ##################################################
SCPCODE_INPUT = r"""
from time import *

############################################### Script ####################################################
def init(ins, evt): # 初始化函数
    ins.ad_init_dic = {'增压温度': 2, '燃气温度': 3, '空调温度': 3, '冷却液温度': 2, '减压阀温度': 3, '进气温度': 3.5,
                       '曲轴通风': 3, 'GPF前温': 0.5, 'GPF后温': 0.3, '水箱温度': 3, 'CNG泄漏2': 3, 'CNG泄漏1': 3,
                       '后氧': 0.6, '前氧': 0.6, '预留T14': 3, '预留T15': 3, '气瓶压力': 3, '预留AO1': 3, '机械TPS': 3,
                       '进气压力': 0.7, '增压压力': 4, '燃气压力': 3, '踏板2': 0.4, '踏板1': 0.8, '预留AO8': 3, '预留AO9': 3,
                       '油箱压力': 3, '减压阀压力': 3, 'GPF压力': 3, '真空压力': 3, '脱附压力': 3, 'EGR阀位置': 3,
                       'CAM-0': 0, 'CAM-1': 0, '转速': 0, '车速': 0}
    ins.switch_on('上电')
    ins.switch_on('点火')
    for name, value in ins.ad_init_dic.items():
        ins.to(name, value)

    evt.functioncycle = False    # 选择周期运行run()函数
    evt.functioncycleperiod = 0.05  # run()函数运行周期，单位：秒
    ins.reset_cal_name = [] #脚本运行结束后会回滚该标定量

def run(ins, evt, exit): # 运行函数
    ...


########### 开发阶段测试 如果在管理软件内运行，则以下内容都不会执行 ###########
class ScriptRunState:  # 可以在这里设置配置参数，但是只在开发阶段有作用，如果在软件上运行，还需要在软件上新增配置
    ...

if __name__ == '__main__':
    from _insc import *
    import time as t

    ins = IncaTestpanelControl()
    evt = ScriptRunState()
    # ins.serial_init('COM6')
    ins.testpanel_ctrlmode = 1
    ins.inca_init()
    ins.can_init()
    init(ins, evt)
    ins.all_reset_read()
    def tempexit():
        tempexit.Run = False
    tempexit.Run = True
    if evt.functioncycle:
        t0 = evt.functioncycleperiod
        while tempexit.Run:
            t1 = t.time()
            run(ins, evt, tempexit)
            t1 = t.time() - t1
            t.sleep(max(t0 - t1, 0))
        ins.all_reset()
    else:
        run(ins, evt, tempexit)
        ins.all_reset()
    print('-- script end --')
"""
SCPCODE_OUTPUT = """
from utils.lcmath import *

def XX_init_(evt, MV, SV, D1V, D2V, p):
    ...

def XX_calc_(evt, MV, SV, D1V, D2V, p):
    ...
"""
########################################## HTML ####################################################

HTML_IncaInform_Main = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="author" content="XiePeng">
<title>变量信息</title>
<style type="text/css">
h2 {h2style}
</style>
</head>
<body>
{body}
</body>
</html>
"""

HTML_IncaInform_Calidisable = """<p>
<h2><a name="calidisable">不可标定标定量</a></h2>
{0}
</p>
"""

HTML_IncaInform_Caliable = """
<p>
<h2><a name="caliable">可标定标定量</a></h2>
{0}
</p>
"""

HTML_IncaInform_Founda = """
<p>
<h2><a name="founda">轴</a></h2>
{0}
</p>
"""

HTML_IncaInform_Foundct = """
<p>
<h2><a name="foundct">二维表</a></h2>
{0}
</p>
"""
HTML_IncaInform_Foundco = """
<p>
<h2><a name="foundco">一维表</a></h2>
{0}
</p>
"""
HTML_IncaInform_Foundcs = """
<p>
<h2><a name="foundcs">单参标定量</a></h2>
{0}
</p>
"""
HTML_IncaInform_Foundm = """
<p>
<h2><a name="foundm">测量量</a></h2>
{0}
</p>
"""
HTML_IncaInform_Value = """
<p>
<h2><a name="value">标定量数值</a></h2>
<ul>
{0}
</ul>
</p>
"""

HTML_IncaInform_Inform = """
<p>
<h2><a name="inform">变量信息</a></h2>
<dl>
<dt></dt>
    <dd>
    <table border="1" cellpadding="4" cellspacing="0">
    <tr>
        <th>变量名</th>
        <th>单位</th>
        <th>范围</th>
        <th>精度</th>
        <th>地址</th>
        <th>变量类型</th>
    </tr>
    {0}
    </table>
    </dd>
</dl>
</p>
"""

HTML_IncaInform_Error = """
<p>
<h2><a name="error">错误变量</a></h2>
<ul>
<li><b>未找到的变量</b></li>
{0}
<li><b>信息出错的变量</b></li>
{1}
</ul>
</p>
"""

HTML_IncaInform_Overview = """
<p>
<h2>总览</h2>
<ul>
<li><b>A2L描述</b>: {data[a2l]}</li>
<li><b>数据源</b>: {data[nowdevice]}</li>
<li><b>所有的数据源</b>: {data[device]}</li>
<li><b>找到变量</b>: {allnum} 个</li>
<li color="#DC143C"><b>出错的变量</b>: <strong>{errnum}</strong> 个</li>
<li><b>索引</b></li>
    <ul>
    <li><a href="#error">错误变量</a></li>
    <li><a href="#inform">变量信息</a></li>
    <li><a href="#value">标定量数值</a></li>
    <li><a href="#foundm">找到的测量量</a></li>
    <li><a href="#foundcs">找到的单参标定量</a></li>
    <li><a href="#foundco">找到的一维表</a></li>
    <li><a href="#foundct">找到的二维表</a></li>
    <li><a href="#founda">找到的轴</a></li>
    <li><a href="#caliable">可标定标定量</a></li>
    <li><a href="#calidisable">不可标定标定量</a></li>
    </ul>
</ul>
</p>
"""
########################################## 小图标 ###################################################
from wx.lib.embeddedimage import PyEmbeddedImage

IMGFolder = PyEmbeddedImage('iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAq0lEQVQ4T+3UPQ5BQRQG0KOxCDag1apsQKliFQq'
                            'rUNgErRWoJQpLoBCNjkQjhDwhET/vTuKVpr1fTr7cmUxJwadUsOcPqmDztNcZmjim7vp1h6/gBUP0igIj5+1Svz'
                            'VsYRFp9/kJ20f2E7jGAP1EcIxOHji9D2sJ4BkNzCMwBcuMJerY54ErlBPaZZEJ2sia3k70bCK3i9Fz6BdwhyoOeW'
                            'DUKJz/f5twRWHgCqDyHBU+4MpMAAAAAElFTkSuQmCC')
IMGSteWhl = PyEmbeddedImage('iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABbElEQVQ4T73UO0udQRSF4ccL2oggxDYQkCBYCEGN'
                            'mEKCYpPG1lbBIpGoZf5AWi+FhRBS2dvYiBcEFTGCQjBFsBAbCxuLIDFqkC3zgXycCx4OTjvMO2utvWZqVHnVVJnn'
                            'WYGN6MUwPiQnK1jGHq4LuSumsAML6EM9Lnhw8wK32MVHHOehhYAB20mgJXzFWQK+wheM4Abv8tA8MGyuJqthcxN3'
                            'ORV1eI+wH9aHHtvPA/uxhm/4VACWsQMakYxiEFvZRh44gyn04AC1aMop/JMu6sY+ZjFdDPgbbTjCecqtPYHjzP+0'
                            '9xeR51uc4HUp4EusIxS0Fin+FX7iDU5LAcPyJDpTVX6hJQe9TKBmHGKulOVsKIv4nMAxxcgo8o4LowURyTzGyw0l'
                            'q00XBvADDdhOwOjdP8T+RhpcydqEu6zYAfqOUBu2QuFEUjWWwGWLncX1+OlF52K6saJGUfQnPb0MWtXPoeJv8ln/'
                            'w4pU3gMQcE8V7F/D6QAAAABJRU5ErkJggg==')
IMGNight = PyEmbeddedImage('iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABGklEQVQ4T73UvytHURzG8dc3MdltrIr8DSSDpMgoK1n'
                           '8AcKgTFImg5KFwebHgpSN3SL/AKMIRX51dNV13XPvVTefusu9n/s+z/k8zzkNNVejZp5/B85gEhc4wjHu8BTbWZnCXp'
                           'ymfn7EFRaxj48suAjYil3056h5wzLm8Zr+HgO24AADROf8jmmsVwEuIDxNJSk4Rx+ev/vyFI5jKwN6QVCdrWt047YIO'
                           'IulpOEBm7jEWg7wBl1lwKBkNRn2Cu6xgdEc4AmGEHbwVTFTwvsQiU4coj3SO4K9KqY0YwpzaIsYs42JbBZjCsewU+By'
                           'iMxgcnJ+rBcD9qCjIDIBeJY2o2iG4UgNV7yFfgnKU1g7sKK4/Lay2+bP8NqBnxgQMhWrc8ShAAAAAElFTkSuQmCC')
IMGChart = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAB+SURBVDhP7Y7RCYAwDESjownip1M5hvOI4E560R6EUNsI/umDR0PtnZGfCAPcnWE0rHp6uMBHhTNkQMPEbsi5SgcZohv0ZYrORWwZsUXVAk8pxK2UEYZ+cPdggus1nrCsWqj4cG6bcGE0nLuTJp0W+4Dfo3fSpvM1Plj4OUQOChE4pm9wmOEAAAAASUVORK5CYII=')

IMGAddDb = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAB8klEQVQ4T7WUXUiTURjH/89539dNSGNCdWGCkFDd6kUQ4jeoOaIgY0HhteBF2F0sxsggAqEb6ToSFMQIZGsXtc0g7Ka8tGBB0Aco4bCBs23nPLL3zHQfud5Jz8W5OOf5/87/eXjOIVSIR7NvlpLuZq9LSoCyYDLsLGIJhglJJppy319P3ugaKJXT3sbD2ZVY2nWip9IF1fas7R9R/1hXv31pfvHPr7FhWNV0h55LmcWU7zzZwMBCgo9EK4iDo20aeHvqFTecbYWokaoApD59wWP/gAbeuR+zHWYsoOlMiyPs5uevqMtqyfS93mJgGUkQMpCwcvokawIWDJCq3KHqQEdeDzoMvGeYvxzKS9JzjZgOduiSkx+GeX75AhJbXsBIOQPLY2g9HsbN7nfwtL/cB+qhlIBIYiHuw8dU+6Hgcw2ruN47B5YeMPRLKgM6s1ae/f+A3UPj/OLBN4AK8+HYqokrd09jOfJE97Dv0pg9WCetDcwETAj8G1gRMBFkrGdO2Rai4afFwD1jQhGUkQajHkJJuDn/uAg7JMAi72EHJOvBonjA/wp0XHFB8AfYM3KLBdf6NWiaIoV46JkuOR+dfVfDde7G4Vrc/U6nFt/Gnl/Ts1whLvZfjrhdnkFFDGIBgu4V2+kSBIH09s/QSjzkLZXvAoMgshVQTYvoAAAAAElFTkSuQmCC')

IMGAddDb2 = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAHPSURBVDhPpZQ/LANRGMC/d9fSppdOhFjE6k8kjYWExSRhMFlqZJCYxNqKwYJOLISlJCpMGCQ2JAyig7KKSBNpmogWzdH3fN93vUqbVrT3a+76/v7u3ve9dwIqcLa2cJPytgdcUmItDyA0q0NRXQMpdGgyn+6GZ8I9VscvReHp+lLirbG1s1CtCePzOTEyG+qmMgtjG5tK03Qq1o2UeZiYnrLW4lRG2A4WfiRTQNFxAjkI6w3xZybTkH1Jc2Ot5HAuOQiOYXRxWXGtHCHgG99dx0QTeVyVjhOFqjx8MjRv74cq4ESXErhrrIvLVWQ2ljDv5T9HFBwsHO+LQYvnAXNfh1h6oBnnkoPgGGaPBnkdgnIt3uHqfgCSuQ5qqkqb5xH6uy7x8PhAFRZqjJ1j1BFb6BQS/p2UOmDh6l4zZtTJadEtB8JCIUyI7BuwdYBe7PwvuItg+xAgEjPYQXAMF4OjJTHUcKTUaEADCPyEuflgCvjCS+F+BCrJBhSWhj60c1w5hpIGKjdvbIV5M/H7Z+JQKuMSuK9cZsPCap21YDtYGI6eCAMycW6pAz9krslBZb6VsxIcin+Av5eeKhQ9014BDbfi6VOvt3O7FwFuLgLwAyvBmYU8jxyjAAAAAElFTkSuQmCC')

IMGStop = PyEmbeddedImage(
    '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsKDAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgr/wAARCAAYABgDASIAAhEBAxEB/8QAGQABAQADAQAAAAAAAAAAAAAAAAYEBQkH/8QAJxAAAgICAQIFBQEAAAAAAAAAAQIDBAAFBggRBxghUZYXVFdY05H/xAAYAQACAwAAAAAAAAAAAAAAAAADBwQFCP/EACQRAAICAgAEBwAAAAAAAAAAAAECAxEABAUHIZEGEiIxQVFx/9oADAMBAAIRAxEAPwDc6mzst/ta2i0VCxdvXbCQU6dSJpJZ5XYKkaIoJZmYgBQCSSAMuPLb1R/rb4gfDr38sgOmTlL1epLw9srP2MfONSwPf2uRHOw/1evffH/cXXBuDx8UiZ2cijXTNgcxOY294K3YIYIFkEik+okVRr4zkBtrGy0G1s6Le0LNK9SsPBcp24mjlglRirxujAFWVgQVIBBBBxmP1N8pe11JeIVlpz3k5xtnPr73JTjKGWo5WT6JGM7R2jt6UU56F1Vu4BzxXW8t2um2NfcajaTVbdSdJqtqtOySQyKwZXVge6sCAQR6gjK7zW9Rf585j8otf0xjBJNNEKRiPw1g9jR0dsgzxK5Ht5lBruMkdny3a7rY2Nxt9pLat253mtWrE5eSaRiWZ2YnuzEkkk+pJ74xjBkkmzklVVQABQGf/9k=')

IMGNews = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACBSURBVDhPYxgFVAP/KcQCQAwGTFAaBBjJxFgByBZyAUhvPxB3gDgwG0CCIDapBqPrgbuYUhfCMF4XEuNiDD2EDCQGkGQgMh8bwOkIQhrxAZBeGEZJh+SC31AaDGAG/gBiGwiTZLAXSn+C0mBQB8TfgRjZ+aTg20AcBMSjgGLAwAAAcP89mGQN3EQAAAAASUVORK5CYII=')

IMGList = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAA1ElEQVRIS+3VMWoCQRSH8Z9JZWuTylwhYJkD5AjiGbQyIHiHgLlGSJdOsLdU7O2stLA1hYUMpAiy6s4gs81uOfse3/v+PGYaMn2NTBw1KDnpyqNr4glbHJI1/jUWGT2gh3dM8IVpBGyMxXl9EegRQ3xghE8cI0BvmJUBhZoWXrDCPgJysbTIKJy9ootvzDGIgP1gU8Yoa3TtP6tgE6Z7jjDa4beMUajJAsoWXbZlyLbesdF1sLy1LPe4gvpYp4BCT5ZL9dZwSf8rf4+Spr7WVBslR3oCh8gwGwEBD9EAAAAASUVORK5CYII=')

IMGList2 = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFhSURBVEhLYxgFo4DugBFKo4AzafIa7779NRDiYr5gMuvhDagwRQCbRUxHkuQ2qgixut1593uXzbxH/qdT5V9D5YgBc01nPyyDsuGACUojA8Yvv/7xiHOzsIFoEN9EikOIWCzEyWwEMYY4IDTRQ6wQREO4lANsQcc43Vs8W5SbOfH117/zM7e+nLonVnY3VI4g0LDzOSSTOr0JyoUDFiiNDJgUBVmD3ZW5jXbe/foJyJ/urMTlDJEiDI68/XYOykQBWFPd+nBpr19//wewMTNuCFz5dNvaMGlvqBRBoCvG9lhtyv1LUC4cYEsMNAHYfMS8I0ZmDzDoHIBBd8BjyROX//Xqf6ByBMGFFz9XG858EAblwgHVE8PnX//6QMEN5RIEdEneJAXd0cffm4ClRz2UixNgSwz/ediYvpx48v0ziAbxzzz78Q4Xvv/+93mINvIA57ZomVAQDeGOglEw9AADAwBDUJxmL7OmFAAAAABJRU5ErkJggg==')

IMGAdd = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAIfSURBVEhL7ZXPaxNREMdn3ktiExLwUg8xiEJIK0hKL0pvHvTkf+BFTwoV8eQf4FXw4kGwZ/EiePagIHgoCIv0ElLPaaBaodvUpja7O868nWg3m21q/XGxH3g7b2ay75vdnfcGjjkqqDZFrbZQrFT2TkZRlPmb/RhjqNcrbHY6y30NJRi7yOzsxQavfwuBFtktxtGJ9BHwCRhaarfff9TYD1JCIkIhPQXEyxr6BXg5it6ixdujYlatQ15XLgf3EeG6hhIgJwDpDQG1gTBgd1pTP0E8i4R7U8Uz77a2OoFGwah1lMthiV/XFXVTEJFc7/C4EQXBsziahv/IonxfdR0JIaLBCTZzsZdF2KtUwAeLuxoYR3G0iBJCf5P/SYjgIRpzDnBwev9YXa2ve54XFAr9pdEcl8pNvTtFthBvdN8ffJKFh6PZrK8DvAg5S61W66v4wyF5Lv/N+OY0icqYmZmvAuXXZM5l/jICeIUEAZcjgrV8zKAplQbP+Yl26/W58wU7dUl2YijSwJfINnmf3RMvfvoPXTdnMoUy4QXKZfPZ9+GuNfaRRtOMCP2TYqhWq6UjC0WROyYORbfb3UkIIea/sVmJvWw8z5mDhPrSNnTuSAhtb9sdPupfqzsWovzVRsNe44UuaCiFtAvpTeo6EsUg/F6bYIgmtwlhY2Pty/Sp2rIc9ezO88i7xGSk8T1GCw8O1fiG/OlWfsw4cmoPAOA7G3jdNC8I7s8AAAAASUVORK5CYII=')

IMGAdd2 = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAJzSURBVEhL7ZVPaBNBFMZnd5JoQtOqNSmGFA+NmtQqSppiRMR6EAyeRBB76KGeIr3WU6EUwYO9iwiKeCio4FE9FDwUq61dmuaQxpaCh5DYJG3aZm3aJDvjzuQV3e5GYyE99QfLvPfNvPl2/rCL9tktArQGBK10aOUMJDUhDH+bglCHoREdOtUVW8Gj7UeUNpBqQq1ZVGt6jAx1Rszk6xJ+F2hRmkH6L9TaZbU2tNNMhBYIWmM5PPo3k+kMzkoZnE7+FIsgaWC1bA42F0gcjdHbXtmzXhQckBoyljDd6hmznl5YFSZB0tF+WGl7cSfvg5SjMcptUcuFlnIjpIY4rUS229EaFlEZJEMUoj2WHVtXP+pm9ChiTkHIqZvR/XOlYxByTNDq+PTDFJnJmsM2U7kEEufuK18EoTdECHjDz+PmBpA5Z5vpg05H+TqkGqquqEyQ/HACR9nEN1pplj0fCDdR1G566Ul8nuXbDxt3ANPNSjVCJ5qIE0KO5mY8u93h7/OWplk8k8WpIhGiIqKUd7KhAhLCkwdvSpK0ORzquBI6TgeYXBlB1VsrOq61lvwsG0/h0OWnsfcsZlTduvNHFbbHmn1m3PNs+R4jf/SquzDY6VS6QQbYYissrIlpCDl7cr1dLpdtT4ySyeSGxmhk1vb9y5JpHdKqSBJv4OyMUb8cmn6NkSzjjSYLzUBqSMBJRmb7C68bLcgDko65HF4cHLfPQcrR/Sa83q6TL7vliYBzl7+JNF7u/dhwMR6fmgeJozsjNoANZG8FUs2wGiMThm5F27jdQavdXjxECKk65k9EUaT5vGU1kfhcAGmff1L16/IbhH4BtYTlxAQrlwEAAAAASUVORK5CYII=')

IMGDir = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFNSURBVDhPnZTPTocwDMfZAgnhpFcDB/5c9ehb+Ei+kS+jye8mkMCJk1wgISCzbQoBN9DxSWCldN91tEw4BnzfT2BQcIkoihyllMArz/NPCjjBJCiTJPlmW6MoCmMSZwgQxOx2oC9NU5VlmfZui+TxX8CWxTAMJM4uDStBpK5r2vKR6O57xHFMQUII7VuZBKBQFLvQtu0bPUElled55PzNURFMC0DszQmC4OEoffSfvYNhXWyJXStqk8kWmHcPQ7vE/Sl4xnbuYsuu63I0rgAFmdhckU3TZGxbA32pVXLtwzAMv9i8BGz7BcdVEA6EOzatwD7cFo4EsUHneSaHLfg79n2P5iveSLAsS+sKb4FexiyfMdvdvwzOdzYvgYK7Tp+myXFd94Ndtjxpgmxehg4LtglonUcc4aAQ4zgaF4AsYJ4SGIPPS5yUcq6q6vYDT8iMBIXGh9kAAAAASUVORK5CYII=')

IMGDir2 = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEwSURBVDhPY2TAAnbHyUUzMjL+BwJGDg4Ohn//GRj/MzAwOsy+tRiqBCfAZiDT/3r1v1A2BmBsvInVEfgAI9BAoINQAUgMhqFCWAETlCYKwFyHz1CSDAQBQoaihAeyIvSwIuRVENj94NcDgl7AFQnY9Fx//esHw4lUhVBcBoLE8ckBKbhlMLXwGCXFJcgAqE8QSH2Am0PIQHwAWS+MzXTz/d+fIAa1AJPGpDscUDbJAJuv4OnwYZEazuxGDNhy68t0EA03UI6XkeREDgPIEUe2ITAA87aqEFs8iAYbSE4MowN1ETYuEI3iwjsFat+gTLIB3GWwcLj78f93sACJQJmfkRNEYxhIKUAJuzkhSqEgmhEY4f///wOLoQMmYNXwD1g1gNSAAEwdMxPTv8RVd9YCAGKJi0kY4skYAAAAAElFTkSuQmCC')

IMGIcon = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAaySURBVFhHnZcJVFRVGMf/7w0zrAOjguCAgBoqrghBaGCeXHLDtbQQl0otowVP2klPSbaa2tG0U7mQy9HC1FRKAwxTSRNzy9QwQg0DhFFh2LeZ13ffu8AAwzj0O+fjffeb++b+597vfvci4EFoNCLq6kIhCJGQpGCKBJKx96rI7pL7q6ASf5dMpkvU7jDtC3BxUaO6ejwNutI9eMBgz6HDQU+4dg+AZDajobIc9UYj7p49hcIjh6hdkUh93+Vv2017AnRkOzwjoyYNSFwFj36DlGg7ZE4fg/vnzowk95gSsR9rAtzIknvNj5/QJ2EZ1Fp3JdoONUV3kBbR+w653ZRIx2grQBQTOodGrIven84DzdSXGZGb9DnuHD1M019Kb4skUIshzoVXf94ctZV3s0U1vbRbCDtQwdtWBAhCXN8At405RSad/4w46MdPhmdkNAynTyJnyTwsHNsF00fq4aXToL5Bwu85RgR2c0FIHw/+Bc2UltfL1rWzI1ycVDyKUkjoKzx8sIg1rC2BruT4hOKyygb19u/zsD+jAJdpEC9fT+xa3htjIrvybu2TefEeXl19GZf+MvIIEOTvhk+XDsS4Yd6suVgIO7ieOdYE3BG17nIvhrm8DJlJ0Sivamh8+YH0iEnHrQK2S4H9ayIQu/wcauvN8HBTo/TEBBZuEiCyP6247bt1L3r+ck023az5uJBttHtwRuPgjInRPnIpYRgrlCWxxJqA87V//sFdwHXEGHyx7yZv/T+2vDUEyR+Fy6Z1deBRBWsCMiozM7gLOEcMw01Nd2xLyeORjlNgqMa/xYqpxJarbk3A0WqqblTVeBNgSzJ/XS7e2HAVdbSWjAJDjfy0RutfmbgpG0vWXZHtvrGORxXaCJDOT8Hsx3Qo3Z3EI9TJ3QOBqVn4siQEjpEpWLmZvnD9FQRMSGuR6Y1ED+nCPeC5lRdQXtkg+8Mp3tlDI/uNtNkFJEBXUlZf4hVzEn5706HWd+efKJTu3Ay3b9bilon2/eIVwPJ47EgcgjkTW/Zb/3UuDh0vRFWNCTqtGk8M7YrnJgfIPmFzF6CTuxrJK4KR//xT8sFjiSSZlSx/eRkwOBzYnYq5a3LAakYjLNPnxfjjwCePIGvnY9izKlwe3BpWBTCepGr35jhX/DPxUdTnWyQgEzR0BPDwMKWt6wxsO4RnScSPp+TihkfmnECnEYdly8mrQP+nMpraJXZswybeeykYu17xQcGkR3F3dSJqr11WBLi48h4cNy3w2W48vew35FOmW5Kcnm8zYW0KYMwc7Yu6rMlI9DmLbh/E4f7GVbRRDwPpKbwHx0ePsrjX8Py7F3mAdLk44Dsq5QxRsFZ07RDQSEJsL2TtGA7zuSnITxsH750fA7nX+aecKc8g7YYKxSW1cnNQkLu8S/r11MK7i6Mca43dAizRezpi64pQYA3tgtbMWthUbsP7dZKfPfQu8tMabQSs3JSt+z6T3S9sMzHKG341NL1FhTzCGUYJyhlIM8AY3NuDTnnZbUPTIc2JPvFn1ZHkYwZ3d42EoYMow23wU5YBf/uFAd56HiE0NNXnf8Uro7SYPb479F5OGB/lIx/Hw0O7YESYJ915hDQqZmdYd8sZWCS4uqVoFiT4Oq3dgiV7yymrz8FQ0rJ0NmKgddY40OuVlTxiQVAwwoI94O/jjKVzgsjX4YXpgbKvUrWcCla02QX0I7FXnxcdX1oKwVO5cDi9vwEHUg9iz6ivMO1xvVxG2a+5UVCN5NTbuJJbJmc5pjSXXUvq6pvPElsItDh7HULCn1QvXAyh9f7mmM6fgflWLqR7BgheXaEKjQQqylCzmifhggRgWpziM9auQPJog7yF26FFKV7ScPGsJBW3n3iqsEiop8+CZmEC1FNjIQb0hNg/BOrRMfIWm1v4HRAfC2Tze8Rf19C/p83bNN1oFUQq7v/QM6QmcbHJRMnTEdRxC3DdNQh+3s449oYXAtfEAx++iUBTMQmg6mgdNjid9wrNGSEIfejvCc3UWG+HyTOVmB1IVZWoefs1JMX7XXp2kv+lsS+fdvLxdPLa/k7obd7FEnYdT6Lpb/o3rvXudCbbLvr3mOH46nJab/vugdLdYlS/Pp8dAlSdkC0H7aR1HWA3h31SmfFqQ3pKlDnvhlbUdaKdYVuIUHIP5vw8NQlhBeFbJWof7dSnRoR59PsWCY5OESwRxcBeEH39KXNUkKqrYM67CdOFM5CKCouk2ho6pbCdrCnB7OEBAhREBwdns8kUQy6VPTxExk6WCkpgdhr9QJZD1qGBFYD/ACHJUFQhGYA9AAAAAElFTkSuQmCC')
########## 运行 ############
if __name__ == '__main__':
    run_software()

###################################### 开发阶段测试 #########################################
if __name__ == '_main__':
    def calc(evt, MV, SV, D1V, D2V, p):
        p.mymap = 78
        a = SV['K_IDLE_fEngSpdFlwMult']
        a = SV['K_IDLE_nEngSpdFlwOffs']
        m = MV['MAPHPa']
        mm = MV['IdleTrackSpeed']


    opobj = OutputScpRun(lambda a, b, c, d, e, f: None, calc, None, mdf_resampleraster=0.01, mdf_period='Task10ms')
    loadpath = r'E:\IDLE_track.dat'
    savepath = r'E:\IDLE_track___p.mdf'
    opobj.run(loadpath, savepath)
    print()

if __name__ == '_main__':
    a = """
    """
    app = ScriptManage()
    t0 = time.time()
    app.analyse_incaParam(a)
    app.app.MainLoop()
    print('analyse_incaParam time ', time.time() - t0)

if __name__ == '_main__':
    app = wx.App()
    f = wx.Frame(None, size=(500, 400))


    def fun1(e):
        d = wx.FontDialog(None, wx.FontData())
        d.Show()
        d.Layout()
        data = d.GetFontData()
        Font = data.GetChosenFont()
        print('fun1', Font)


    pl = wx.Panel(f)
    bt = wx.Button(pl, label='asd', pos=(200, 200), size=(60, 40))
    bt.Bind(wx.EVT_BUTTON, fun1)
    f.Show()
    app.MainLoop()

if __name__ == '_main__':
    with open(r'C:\Users\Administrator\Desktop\temp_scp\exht.py', 'rb') as f:
        temp = f.read()
    print(temp)
    print(temp.endswith(b'\x00'))
    print(temp[:-1])
    s = temp[:-1]
    # s = temp
    s = s.decode('utf-8')
    print(repr(s))
    # s = s.replace('\t', '    ')
    print(repr(s))
    mod = types.ModuleType('mymod')
    exec(s, mod.__dict__)
    fun1 = mod.exht_name_
    fun2 = mod.exht_init_
    fun3 = mod.exht_calc_
    a = OutputScpRun(fun2, fun3, fun1, getcali_mode=2)
    a.run(r'E:\exht02_1.ascii', r'E:\uuuiiii.ascii')
