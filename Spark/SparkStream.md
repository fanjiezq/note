# 基本概念
+ Spark Stream是Spark为流式处理提供的一个功能.由于Spark本身是批处理框架,所以Spark并不是真正的流出里框架,而是使用"微批"的概念模拟出流式处理的效果
+ 因为Spark Stream本质上还是批处理,所以实时性方面无法达到真正流式处理框架的级别,只能做到准实时
+ Spark Stream的实现原理就是使用一个采集器,采集固定时间单元的数据,组成一个个很小的RDD,然后传递到后端处理.只要数据采集的时间段够小,就能源源不断的产生RDD达到流的效果.但是如果产生的RDD太小,就无法充分利用集群的并发特性,吞吐量就会变小


# 基本使用
    
    object SparkStreamScala {
        def main(args: Array[String]): Unit = {
            val conf = new SparkConf().setMaster("local").setAppName("NetworkWordCount")
            val context = new StreamingContext(conf,Seconds(3))

            val lines = context.socketTextStream("localhost",9999)
            lines.print()
            
            context.start()
            context.awaitTermination()
        }
    }


# 数据采集器
将数据从各类数据源运输到Spark Stream 数据引擎的工具

    object MyReceiverDemo  {
        def main(args: Array[String]): Unit = {
            val conf = new SparkConf().setMaster("local[2]").setAppName("NetworkWordCount")
            val context = new StreamingContext(conf,Seconds(3))

            val value = context.receiverStream(new MyReceiver)
            value.print()

            context.start()
            context.awaitTermination()

        }

        class MyReceiver extends Receiver[String](StorageLevel.MEMORY_ONLY){
            private var flag:Boolean= true

            override def onStart(): Unit = {
            new Thread(() => {

                while (flag){
                store("data")
                Thread.sleep(1000)
                }
            }).start()
            }

            override def onStop(): Unit = {
            flag = false
            }
        }
    }
