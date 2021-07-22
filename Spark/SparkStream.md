# 基本概念
+ Spark的流有两种模型，旧模型被称为DStream，此模型的、以微批的形式模拟流处理，即一个时间段(1s)采集一次数据形成一个RDD,进行一次批处理，只要数据源源不断，就能达到流的效果。新模型被称为Structured Streaming，它将数据看作一个不断追加的无界表，每次数据到来就往表上追加一行，每次触发计算都可以得到一个最新的数据，将数据抽象为表可以很方便的利用sprark sql进行数据处理，且Structured Streaming也没有微批的概念，它不再强制要求采集数据的周期，而是利用触发器的方式触发计算，更像是流处理
+ Structured Streaming 模型由三部分组成(input,ResultTable,output) 其中ResultTable是查询方法的结果，每次触发计算以后都会更新，可以看出 Structured Streaming 不保存原始数据，只是保存 ResultTable，在流计算过程中极大的节省了存储空间


# 基本使用
    
     public static void main(String[] args) throws TimeoutException, StreamingQueryException {

        SparkSession spark = SparkSession
                .builder()
                .config("spark.master", "local[1]")
                .appName("RecommendVideo")
                .getOrCreate();

        //首先在控制台运行 ncat -lk 9999
        Dataset<Row> lines = spark
                .readStream()
                .format("socket")
                .option("host", "localhost")
                .option("port", 9999)
                .load();

        // Split the lines into words
        Dataset<String> words = lines
                .as(Encoders.STRING())
                .flatMap((FlatMapFunction<String, String>) x -> Arrays.asList(x.split(" ")).iterator(), Encoders.STRING());

        // Generate running word count
        Dataset<Row> wordCounts = words.groupBy("value").count();

        // Start running the query that prints the running counts to the console
        StreamingQuery query = wordCounts.writeStream()
                .outputMode("complete")
                .format("console")
                .start();

        query.awaitTermination();
    }

# 输出的三种模式
+ Complete Mode:
+ Append Mode:
+ Update Mode:

# 时间窗口
+ spark 的时间窗口操作类似分组聚合，spark将时间窗口看作一个列，每个窗口都是一个key，窗口操作就是根据这个key分组， 所以窗口操作都是结合聚合算子

# 时间类型
