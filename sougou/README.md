data should be set in **./SougouQ/**

1. data download: http://www.sogou.com/labs/resource/q.php

2. data format:

   | 1        | 2      | 3      | 4                       |        5         |       6       |
   | -------- | ------ | ------ | ----------------------- | :--------------: | :-----------: |
   | 访问时间 | 用户ID | 查询词 | 该URL在返回结果中的排名 | 用户点击的顺序号 | 用户点击的URL |

3. re-encode data: dealt

   - access_log.20060815.decode.filter
   - access_log.20060821.decode.filter
   - access_log.20060831.decode.filter 

   以上三个文件解码有问题，只解码出部分数据

