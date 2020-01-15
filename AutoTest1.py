# -*- coding: UTF-8 -*-
import os
import re
import time
from DrozerServer import DrozerServer

class Fuzz():
    components_types = ["activity", "service", "broadcast", "provider"]
    scanner_types = ["traversal", "injection"]

    def __init__(self, _ipAdrr,_scanner_types,_components_types):
        self.session = DrozerServer(_ipAdrr).getSession()
        if _scanner_types:
            self.scanner_types = _scanner_types
        if _components_types:
            self.components_types = _components_types

    # 获取包名信息
    def get_packages(self, temp_root_path,packageName=None):
        '''
        拉取所有应用或者指定应用的包名信息
        :param temp_root_path:  应用包名信息测存储位置
        :param packageName:
        :return:
        '''
        no_exported_path = os.path.join(temp_root_path, "no_exported")
        no_exported_file = open(no_exported_path, "a+")
        self.no_exported_list = no_exported_file.readlines()
        no_exported_file.close()

        if packageName:
            self.scopPackage(temp_root_path,packageName,self.components_types)
        else:
            self.getAllPackage(temp_root_path,self.components_types)

        # 将所有的截图文件pull下来
        screencap_path = os.path.join(temp_root_path,"screencap")
        if not os.path.exists(screencap_path):
            os.mkdir(screencap_path)

        cmd = "adb pull /sdcard/tempimg/ %s" % screencap_path
        os.popen(cmd)

        # no_exported_file.writelines(self.no_exported_list)
        # no_exported_file.close()
        for ln in  self.no_exported_list:
            print ln

    # 查看指定应用的组件信息
    def scopPackage(self,temp_root_path,packageName,components_types):
        print "+ 正在处理应用：" + str(packageName)
        # packageName_path = os.path.join(temp_root_path, packageName)
        for components_type in components_types:
            self.getComponentsInfo(temp_root_path,packageName, components_type)
            time.sleep(5)

    # 获取到所有应用的组件信息
    def getAllPackage(self,temp_root_path,components_types):
        # package_path = os.path.join(temp_root_path, "package")
        # if not os.path.exists(package_path):
        #     package_file = open(package_path, "w+")
        #     self.session.stdout = package_file
        #     cmd = "app.package.list"
        #     self.session.do_run(cmd)
        #     time.sleep(2)
        #     package_file.close()

        package_path = self.run_drozer_cmd(temp_root_path,"package","app.package.list")


        curred_app_num = 1
        with open(package_path, "r") as package_file:
            lines = package_file.readlines()
            for line in lines:
                package_name = line[:line.rfind(' (')]
                app_name = line[line.rfind('('):line.rfind(')')].replace("(", "").replace(")", "")
                new_app_name = str(package_name) + "(" + str(app_name) +")"
                print "+ 共计："+str(len(lines))+"个应用,正在处理第"+ str(curred_app_num) +"个应用：" + new_app_name
                no_exported_num = 0
                for components_type in components_types:
                    exported_components_num = self.getComponentsInfo(temp_root_path, package_name, components_type)
                    no_exported_num = no_exported_num + exported_components_num
                    time.sleep(5)
                if no_exported_num == 0:
                    self.no_exported_list.append(new_app_name+"\n")
                curred_app_num = curred_app_num + 1
            package_file.close()

    # 获取应用的组件信息
    def getComponentsInfo(self, temp_root_path,package_name, components_type):
        # components_info_path = os.path.join(temp_root_path, package_name+"."+components_type)
        # if not os.path.exists(components_info_path):
        #     components_info_file = open(components_info_path, "w+")
        #     self.session.stdout = components_info_file
        #     cmd = "app.%s.info -a %s" % (components_type,package_name)
        #     print "\t |- 正在查询组件信息,命令为："+cmd
        #     self.session.do_run(cmd)
        #     time.sleep(2)
        #     components_info_file.close()

        cmd = "app.%s.info -a %s" % (components_type, package_name)
        components_info_path = self.run_drozer_cmd(temp_root_path, package_name+"."+components_type, cmd)

        modules = []
        components_names = self.getComponents(components_info_path,components_type)
        if components_type != "provider":
            print "\t\t |- 组件：" + components_type+" 可以被导出的数量为："+str(len(components_names))
        else:
            print "\t\t |- 组件："+components_type +"存在问题的内容数量为："+str(len(components_names))

        components_num = 0
        for components_name in components_names:
            if components_type == "provider":
                pattern = re.compile(r'[0-9]@_@')
                print "\t\t\t |-  可能存在问题的组件为:" + str(re.sub(pattern, "", components_name))
            else:
                print "\t\t\t |-  可以导出的组件名称为:" + components_name
            if components_type == "activity":
                modules = ["start"]
            elif components_type == "service":
                modules = ["start", "stop"]
            elif components_type == "broadcast":
                modules =["send"]
            else:
                modules =["projection","selection",""]
            self.runComponents(temp_root_path,components_type, modules, package_name, components_name,components_num)
            components_num = components_num + 1
        return len(components_names)

    # 执行组件并进行截图
    def runComponents(self,temp_root_path,components_type,modules,package_name,components_name,components_num):
        for module in modules:
            if components_type  == "provider":
                content_list = components_name.split("@_@")
                if content_list[0] == "1" and module.startswith("projection"):
                    self.injectioninQuery(temp_root_path, package_name, content_list[1], module,components_num)
                    continue
                if content_list[0] == "2" and module.startswith("selection"):
                    self.injectioninQuery(temp_root_path, package_name, content_list[1], module,components_num)
                    continue
                if content_list[0] == "3" and  module.startswith(""):
                    self.injectioninQuery(temp_root_path, package_name, content_list[1], module,components_num)
                    continue
            else:
                cmd = "app.%s.%s --component %s %s" % (components_type, module, str(package_name), str(components_name))
                print "\t\t\t\t |- 正在执行组件，命令为：" + cmd
                self.session.do_run(cmd)
                time.sleep(2)
                screencap_cmd = "adb shell screencap -p /sdcard/tempimg/%s_%s_%s.png" % (
                str(components_type), str(package_name), str(components_name))
                os.popen(screencap_cmd)
                os.popen("adb shell am start com.mwr.dz/com.mwr.dz.activities.MainActivity")



    def getComponents(self, components_info_path, components_type):
        components_names = []

        # 忽略0kb大小的文件
        if os.path.getsize(components_info_path) == 0:
            return components_names

        with open(components_info_path) as components_info_file:
            for line in components_info_file:
                le = line.replace(" ", "").replace("\n", "")
                # 忽略第一行的包信息
                if le.startswith("Package:"):
                    package = le.replace("Package:", "")
                    continue

                # 忽略没有组件导出的文件
                if le.startswith("Noexportedservices.") or le.startswith("Nomatchingreceivers.") or le.startswith(
                        "Nomatchingactivities.") or le.startswith("Nomatchingproviders."):
                    # print "no exported...."
                    return components_names

                if components_type == "provider":
                    if le.startswith("ReadPermission:null") or le.startswith("WritePermission:null"):
                        provider_root_path = os.path.join(temp_root_path, components_type)
                        if not os.path.exists(provider_root_path):
                            os.mkdir(provider_root_path)
                        self.scannerProvider(components_names,provider_root_path, package)
                        return components_names
                    else:
                        continue

                self.clStr(components_names, le)

            return components_names

    # 处理组件的基本信息
    def clStr(self,components_names,le) :
        # 忽略所有Permission行
        if not le.startswith("Permission"):
            # print "no Permission...."
            if not (le.startswith("ParentActivity:") or le.startswith("TargetActivity:")):
                if len(le)>0:
                    # print "====== add components_name to components_names:"+le
                    components_names.append(le)
            # else:
            #     print "is ParentActivity  and TargetActivity...."
        else:
            permission_package = le.replace("Permission:", "")
            if not permission_package.startswith("null"):
                # print "permission no is null ...."
                if len(components_names) != 0:
                    # print "====== remove components_name to components_names:" + components_names[len(components_names)-1]
                    components_names.remove(components_names[len(components_names)-1])

    # 扫描组件Provider的漏洞信息
    def scannerProvider (self,components_names,temp_root_path, package_name):
        for scanner_type in self.scanner_types:
            scanner_provider_path = os.path.join(temp_root_path, package_name + "."+scanner_type)
            if not os.path.exists(scanner_provider_path):
                scanner_provider_file = open(scanner_provider_path,"w+")
                self.session.stdout = scanner_provider_file
                cmd = "scanner.provider.%s -a %s" % (str(scanner_type),str(package_name))
                print "\t\t |- 正在扫描Provuder组件漏洞信息，命令为："+cmd
                self.session.do_run(cmd)
                time.sleep(2)
                scanner_provider_file.close()
            flag =0
            with open(scanner_provider_path) as scanner_provider_file:
                for line in scanner_provider_file:
                    le = line.replace(" ", "").replace("\n", "")

                    if le.startswith("NotVulnerable") or le.startswith("Novulnerabilitiesfound") or le.startswith("Scanning"):
                        continue

                    if le.startswith("InjectioninProjection"):
                        flag = 1
                        continue

                    if le.startswith("InjectioninSelection"):
                        flag = 2
                        continue

                    if le.startswith("VulnerableProviders"):
                        flag =3
                        continue

                    if flag != 0 and le.startswith("content://"):
                        components_names.append(str(flag)+"@_@"+le)

                scanner_provider_file.close()

    # 注入
    def injectioninQuery(self,temp_root_path,package_name,content_name,schme_type,components_num):
        injectionin_dir = os.path.join(temp_root_path,"injectionin")
        if not os.path.exists(injectionin_dir):
            os.mkdir(injectionin_dir)

        schme_type_err_provider_path = os.path.join(injectionin_dir, "err_"+package_name + "_"+str(components_num) +"." + schme_type)
        if os.path.exists(schme_type_err_provider_path):
            os.remove(schme_type_err_provider_path)
        # if not os.path.exists(schme_type_provider_path):
        scanner_provider_file = open(schme_type_err_provider_path, "a+")
        self.session.stderr = scanner_provider_file

        cmd = "app.provider.query %s --%s %s" % (str(content_name), str(schme_type),'\"\'\"')
        print "\t\t\t\t |- 正在进行注入操作，命令为：" + cmd
        self.session.do_run(cmd)
        scanner_provider_file.write(cmd + "\r")
        scanner_provider_file.close()

        return  schme_type_err_provider_path



    # 对内容组件进行操作并进行截图
    def actionProvider(self, components_name,):

        cmd = "scanner.provider.traversal -a %s" % (str(components_name))
        print "\t\t\t |- "+cmd
        self.session.do_run(cmd)

        time.sleep(2)

        cmd = "scanner.provider.injection -a %s" % (str(components_name))
        print "\t\t\t |- "+cmd
        self.session.do_run(cmd)


    def run_drozer_cmd(self,root_path,file_name,cmd_str,rwa_str="w+", sleep_time=2):
        '''
            运行drozer命令

            :param root_path: 输出drozer运行结果存储的根目录
            :param file_name: 输出drozer运行结果存储的文件名称
            :param cmd_str:  需要执行的命令信息
            :param rwa_str: drozer运行结果向文件中追加的权限信息
            :param sleep_time: 每次执行完毕后，等待的时间，单位为秒
            :return: 输出drozer运行结果存储的文件的绝对路径
        '''
        package_path = os.path.join(root_path, file_name)
        if not os.path.exists(package_path):
            package_file = open(package_path, rwa_str)
            self.session.stdout = package_file
            self.session.do_run(cmd_str)
            time.sleep(sleep_time)
            package_file.close()
        return package_path

if __name__ == '__main__':

    temp_root_path = "C:\\Users\\root\\Desktop\\temp"
    components_types =None
    scanner_types =None

    components_types = ["activity", "service", "broadcast", "provider"]
    # components_types = ["provider"]
    # scanner_types = ["traversal", "injection"]
    if False:
        ip = "192.168.43.1"
        port = "41415"
        ipAdrr = "%s:%s" % (ip, port)

        connect_cmd = "adb connect %s" % ip
        forward_cmd = "adb forward tcp:%s tcp:%s" % (port, port)
        dir_img_cmd = "adb shell mkdir /sdcard/tempimg/"
        rm_img_cmd = "adb shell rm -rf /sdcard/tempimg/*"

        connect = os.popen(connect_cmd)
        forward = os.popen(forward_cmd)
        dir_img = os.popen(dir_img_cmd)
        rm_img = os.popen(rm_img_cmd)
    else:
        ip = "127.0.0.1"
        port = "41415"
        ipAdrr = "%s:%s" % (ip, port)

        forward_cmd = "adb forward tcp:%s tcp:%s" % (port, port)
        rm_img_cmd = "adb shell rm -rf /sdcard/tempimg/*"
        dir_img_cmd = "adb shell mkdir /sdcard/tempimg/"

        forward = os.popen(forward_cmd)
        dir_img = os.popen(dir_img_cmd)
        rm_img = os.popen(rm_img_cmd)


    # Fuzz(ipAdrr,scanner_types,components_types).get_packages(temp_root_path,"com.mwr.example.sieve")
    Fuzz(ipAdrr, scanner_types, components_types).get_packages(temp_root_path,"com.android.phone")

