### 环境信息

##### 语言环境 
```
python 2.7
```

##### 需要进行环境变量配置的工具

ApkTool 工具最新版本(需配置在环境变量中)
adb 下载Android SDK里面内置 

### 批量反编译工具使用说明

在AutoPullAll.py文件的main函数中，对以下数据进行配置：

``` python
# 必填项，临时根文件路径，用于存储过程文件以及结果信息
temp_root_path = "C:\\Users\\root\\Desktop\\temp"

# 必填项，Drozer所在设备的IP地址
ip = "192.168.43.1"

# 必填项，Drozer所在设备的端口地址
port = "41415"

```
配置完毕直接运行即可。


### DrozerFuzz工具使用说明

在AutoTest.py文件的main函数中，对以下数据进行配置：

``` python
# 必填项，临时根文件路径，用于存储过程文件以及结果信息
temp_root_path = "C:\\Users\\root\\Desktop\\temp"

# 必填项，Drozer所在设备的IP地址
ip = "192.168.43.1"

# 必填项，Drozer所在设备的端口地址
port = "41415"

# 选填项，指定对某一个应用进行扫描，None为扫描所有应用
# 指定应用扫描：package_name = "com.android.phone"
package_name = None

# 可选项，指定对四大组件中的那一个进行扫描，至少需要有一个,None为同时对四大组件进行扫描 
# 对四大组件进行扫描:components_types = ["activity", "service", "broadcast", "provider"]
components_types = None

# 可选项，指定对内容组件的扫描方式，至少需要有一个，None为同时进行目录遍历以及注入进行扫描
# 同时扫描目录遍历以及注入：scanner_types = ["traversal", "injection"]
scanner_types = None

```
配置完毕直接运行即可。