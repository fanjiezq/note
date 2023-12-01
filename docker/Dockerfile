# 创建一个大数据环境的DockerFile
# 基于ubuntu
FROM ubuntu
ENV LANG en_US.utf8

# 安装基础软件
RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak 
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse" >> /etc/apt/sources.list  
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse" >> /etc/apt/sources.list  
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse" >> /etc/apt/sources.list  
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse" >> /etc/apt/sources.list  
RUN apt update -y 
RUN apt install -y vim 
RUN apt install -y xz-utils 
RUN apt-get install -y locales && rm -rf /var/lib/apt/lists/* && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

# 安装java 环境
ADD jdk-17.0.7_linux-x64_bin.tar.gz /usr/local/ 
ADD hadoop-3.3.6.tar.gz /usr/local/
ADD apache-zookeeper-3.9.1-bin.tar.gz /us/local/ 
ADD kafka_2.12-3.6.0.tgz /usr/local/
ADD flink-1.18.0-bin-scala_2.12.tgz /usr/local

# 设置java环境变量
ENV PATH=$PATH:/usr/local/include/jdk-17.0.7/bin

