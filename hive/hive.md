# hive 脚本执行原理和优化
## group by
+ 原理: 
1. map任务将表的每一行转换为 key:<k表名,value>
2. shuffle 将key相同的数据分发个不同的reduce
3. reduce 将相同的key的的value进行聚合
 

## join
+ common join 原理
默认情况下 hive join 在reduce时进行数据聚合，称为common join，步骤如下：
	1. map端join 两侧表的每行数据封装为 key:<k表名,value>
	2. shuffle阶段将所有map输出数据按照key分发，保证相同的key被分发到同一个reduce端
	3. reduce得到两个表key相同的数据，对比key，将key相同的且表名不同的数据进行封装，封装为脚本需要的数据形式
	4. reduce得到的数据格式为 key:[<table1,value>,<table2,value>].且join前面的表数据一定在前，所以reduce在进行连接时如果发现第一个数据就是table2的数据，说明肯定不存在key值相等的数据。这一特性也解释了在进行join链接时，为什么小表在前速度可以更快，因为小表在前reduce判断数据时只需要扫描少量数据就可以确定结果中有哪些数据可以连接输出。

+ map join原理
如果两个表数据量差别很大，且小表足够小(小于25M)，hive会选择在map端进行连接，步骤如下：
	1. 大表的数据进行切分后会形成多个map任务，每个map任务拉取小表的所有数据，并保存在内存中
	2. map端将自己的数据与小表的数据对比key，最终形成一个连接好的数据集
	3. 最后reduce任务将所有map端链接好的数据进行汇总，

## order by
+ order by 语句会将所有的数据在一个reduce任务中进行全局排序，数据量很大的情况下性能很低

## sort by
+ 仅在reduce任务中进行局部排序

## distributed by
+ 用于指定的

# 大数据技术选型需要考虑的问题
1. 数据大小
2. 数据行数
3. 数据增长速度
4. 实时性
5. 事务
6. 全文搜索
