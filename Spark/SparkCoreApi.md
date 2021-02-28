# 基本使用
    object WordCountScale {
        def main(args: Array[String]): Unit = {
            val conf = new SparkConf().setAppName("test").setMaster("local[*]")
            val sc = new SparkContext(conf)
            val arrRdd = sc.parallelize(Array(new Tuple2("name","2"),new Tuple2("name","1"),new Tuple2("age","10"),new Tuple2("age","20")),2)
            arrRdd.saveAsTextFile("output")
        }
    }

# 分区器
    object WordCountScale {
        def main(args: Array[String]): Unit = {
            val conf = new SparkConf().setAppName("test").setMaster("local[*]")
            val sc = new SparkContext(conf)
            val arrRdd = sc.parallelize(Array(new Tuple2("name","2"),new Tuple2("name","1"),new Tuple2("age","10"),new Tuple2("age","20")),2)
            arrRdd.partitionBy(new MyPartitioner)
            arrRdd.saveAsTextFile("output")
        }
    }

    class MyPartitioner extends Partitioner{
        override def numPartitions: Int = 2

        override def getPartition(key: Any): Int = {
            key match {
            case "name" => 1
            case "age" => 2
            case _ => 0
            }
        }
    }