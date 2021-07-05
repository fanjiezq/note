# 基础
+ SparkSql是Spark提供的一种以sql的方式编写spark程序的功能，与hive类似
+ SparkSql需要依赖结构化的数据，所以spark提供了DataFrame和DataSet来配合SparkSql。 DataFrame就是描述信息的RDD，类似数据库的表结构，每个DataFrame都有列名，数据也是以列和行的形式组织管理。虽然只是增加了的一个列名，但是数据的组织管理方式完全不同了，简化了代码的编写，在数据计算过程中可以去除很多无效的数据。DataFrame的缺点是数据结构信息太少，只有列名没有数据类型，数据引擎无法进行编译期校验，对数据结构的分析还是需要依赖手动编写代码
+ DataSet在DataFrame更进一层，表结构描述增加了数据类型，所以DataSet是强类型的，每个列数据的类型更加严格，DataFrame 可以看作一个类型为Row的DataSet
+ RDD、DataFrame、DataSet 三者之间可以互相转换，RDD是Spark最原始最基础的数据结构，虽然后两者功能更强，但都是基于RDD，很多情况还是需要RDD

# 基本使用
  
    package com.sparck;

    import org.apache.spark.api.java.JavaRDD;
    import org.apache.spark.sql.*;

    import java.io.Serializable;
    import java.util.Arrays;
    import java.util.List;

    public class SqlTest {

        public static void main(String[] args) throws AnalysisException {

            SparkSession spark = SparkSession.builder().appName("Java Spark SQL basic example").getOrCreate();
          
            //创建无类型的DataSet.此处因为没有指定类型， 所以可以看作是一个DataFrame
            Dataset<Row> dataset1 = spark.read().json("people.json");
            //创建有类型的DataSet.此处因为没有指定类型， 所以可以看作是一个DataFrame
            List<Person> people = Arrays.asList(new Person(), new Person(), new Person());
            Dataset<Person> dataset2 = spark.createDataset(people, Encoders.bean(Person.class));


            //创建表
            dataset1.createGlobalTempView("table1");
            //查询表
            Dataset<Row> res1 = dataset1.select("name");
            Dataset<Row> res2 = spark.sql("select * from table1");

            //RDD、DataSet、DataFrame 之间相互转换
            JavaRDD<Person> stringJavaRDD = spark.read().textFile("/people.txt")
                    .javaRDD()
                    .map(line -> {
                        String[] parts = line.split(",");
                        Person person = new Person();
                        person.setName(parts[0]);
                        person.setAge(Integer.parseInt(parts[1].trim()));
                        return person;
                    });
            // RDD -> DF
            Dataset<Row> dataFrame1 = spark.createDataFrame(stringJavaRDD, Person.class);
            // RDD -> DS
            Dataset<Person> dataset4 = spark.createDataset(stringJavaRDD.rdd(), Encoders.bean(Person.class));
            // DF -> DS
            Dataset<Person> dataset5 = dataFrame1.as(Encoders.bean(Person.class));
            // DS -> DF
            Dataset<Row> dataFrame2 = dataset4.toDF();

        }

        public static class Person implements Serializable {
            private String name;
            private long age;

            public String getName() {
                return name;
            }

            public void setName(String name) {
                this.name = name;
            }

            public long getAge() {
                return age;
            }

            public void setAge(long age) {
                this.age = age;
            }
        }
    }
    
    {"name":"Michael"}
    {"name":"Andy", "age":30}
    {"name":"Justin", "age":19}


