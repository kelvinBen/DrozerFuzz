# -*- coding: UTF-8 -*-
import os
from DrozerServer import DrozerServer


class AutoPullAll():
    def __init__(self,_ip,_port):
        ip_adrr = "%s:%s" % (_ip, _port)
        self.session = DrozerServer(ip_adrr).getSession()
        self.apk_path = "APKPath:"
        self.data_dir = "DataDirectory:"
        self.intiConfig(_port)

    def intiConfig(self,_port):
        connect_cmd = "adb connect %s" % ip
        forward_cmd = "adb forward tcp:%s tcp:%s" % (_port, _port)
        os.popen(connect_cmd)
        os.popen(forward_cmd)

    def getAllPackage(self,temp_root_path):
        package_path = os.path.join(temp_root_path, "package")
        if not os.path.exists(package_path):
            package_file = open(package_path, "w+")
            self.session.stdout = package_file
            cmd = "app.package.list"
            self.session.do_run(cmd)
            package_file.close()

        with open(package_path, "r") as package_file:
            for line in package_file:
                package_name = line[:line.rfind(' (')]
                self.getPackageInfo(temp_root_path,package_name)
            package_file.close()

    def getPackageInfo(self,temp_root_path,package_name):

        download_dir = self.mkdirs(temp_root_path,"download")
        info_dir = self.mkdirs(download_dir,"info")

        apk_info_path = os.path.join(info_dir, package_name+".info")
        if not os.path.exists(apk_info_path):
            apk_info_file = open(apk_info_path, "w+")
            self.session.stdout = apk_info_file
            cmd = "app.package.info -a  %s" %(package_name)
            self.session.do_run(cmd)
            apk_info_file.close()

        with open(apk_info_path, "r") as package_file:
            for line in package_file:
                le = line.replace(" ","").replace("\r", "").replace("\n", "")
                if (le.startswith(self.apk_path) or le.startswith(self.data_dir)):
                    self.pullData(le, package_name, download_dir)
            package_file.close()

    def pullData(self,le,package_name,root_dir):

        if (le.startswith(self.apk_path)):
            dir_name = "apk"
            file_path = le.replace(self.apk_path, "")

        if (le.startswith(self.data_dir)):
            dir_name = "data"
            file_path = le.replace(self.data_dir, "")

        pull_dir = file_path[1:file_path.rfind('/') + 1].replace("/", "\\")
        path = self.mkdirs(root_dir, dir_name)
        package_dir = self.mkdirs(path,pull_dir+package_name)

        print "正在下载 -->" + file_path

        adb_pull = 'adb pull %s %s' % (file_path, package_dir)
        print "下载命令为:" + adb_pull
        os.popen(adb_pull)

        if (le.startswith(self.apk_path)):
            apkname = le[le.rfind('/') + 1:le.rfind('.apk')]
            apktool = "java -jar D:\\tools\\apktool_2.4.0.jar d %s/%s.apk -o  %s/%s -f -r " % (
            package_dir, apkname, package_dir, apkname)
            print "正在对APK文件进行反编译处理，命令为：" + apktool
            os.popen(apktool)

    def mkdirs(self,root_path,dir_name):
        new_path = os.path.join(root_path, dir_name)
        if not os.path.exists(new_path):
            os.makedirs(new_path)
            # os.mkdirs(new_path)
        return new_path

if __name__ == '__main__':
    ip = "127.0.0.1"
    port = "41415"

    temp_root_path = "C:\\Users\\root\\Desktop\\temp"

    AutoPullAll(ip,port).getAllPackage(temp_root_path)