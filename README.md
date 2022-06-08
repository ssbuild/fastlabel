# fastlabel 

## 简介
fastlabel是一款简洁高效的标注工具；

它是做深度学习的标注利器 ，既支持文本标注，也支持图形标注。  

文本标注支持：NER标注、关系标注、事件标注、分类文本标注。

图形标注支持： 矩形和点的快速标注。



## 标注工具fastlabel 升级方法 

1. 下载 
url: http://ssdog.cn/fastlabel
百度网盘 
https://pan.baidu.com/s/1pyOidMH446H5zEzyItgdgw 提取码：1111


## fastlabel批量导出步骤 

多人异地协作时，使用fastlabel非常方便。 只需要每个人标注不同的号段即可，协作标注完成后，每个人标注的号段数据需要导出并合并，这里提供一个导出合并工具。

1. 记录标注的 工程名称，例如“分类标注”

2. 给每个数据文件建一个目录,目录名命名格式为: "1-102,200-300"，
   数字表示号码段，如果有多个不连续的号段，则用逗号(中英文均可)分开; 
	
3. 把标注的`.db`文件放进上面的目录中，文件名只要以`db`结尾即可; 
 得到的结构如下：

```
SIGNED\DATAS
├─1-100,19901-20000
├─10001-10434
└─101-1206
```

4. 运行以下命令批量导出：

```
python src/data_export.py --task=export --fname=数据目录 --project=工程名称 --outpath=输出文件名
```

实际例子： 所有数据目录均在`datas`目录下
```
python src/data_export.py --task=export --fname=signed/datas --project=技术关键词 --outpath=signed/alldata_2022031.txt 

```




fastlabel 欢迎大家尝试。
![image](https://user-images.githubusercontent.com/14295852/116810356-eb2c3b80-ab75-11eb-8284-9653c797017f.png)


![image](https://user-images.githubusercontent.com/14295852/116810366-f97a5780-ab75-11eb-9ea8-5681e97daa83.png)
