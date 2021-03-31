import folium
import pandas as pd
import numpy as np
import webbrowser
from folium.plugins import HeatMap
import xlrd

#绝对地址或同一目录下相对地址
file_name = "data.xlsx"
file = xlrd.open_workbook(file_name)
sheet = file.sheet_by_name("test")
col_value0 = sheet.col_values(0)
col_value1 = sheet.col_values(1)

#获取经纬度数据，使用两个变量存储
LAT_new = col_value0  #纬度
LNG_new = col_value1  #经度
LOC = []
#此处必须使用zip构成元组
for lng,lat in zip(list(LNG_new),list(LAT_new)):
    LOC.append([lat, lng])

Center=[np.mean(np.array(LAT_new,dtype='float32')),np.mean(np.array(LNG_new,dtype='float32'))]
m=folium.Map(location=Center,zoom_start=8.5)
HeatMap(LOC).add_to(m)

#保存格式为html文件，可使用绝对路径进行保存
name='ten_year_data.html'
m.save(name)

#将结果文件打开进行显示
webbrowser.open(name,new=2)

