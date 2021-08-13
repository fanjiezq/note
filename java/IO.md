# IO的执行过程
1. 用户线程调用操作系统函数发起IO请求，要求操作系统读取数据放入一个用户缓冲区
2. 操作系统进入内核态，执行系统调用，内核向磁盘控制器发起指令，要求其将制定数据拷贝到一个内核缓冲区
3. 磁盘控制器将此磁盘拷贝数据到内核缓冲区，这一步骤不需要CPU协助
4. 一旦内核缓冲区被填满，内核会把内核缓冲区的数据拷贝到用户缓冲区
5. 系统调用返回，进入用户态，线程从用户缓冲区获取到数据 

# IO模型
## 阻塞模型
+ 描述:最简单的IO模型，所有的IO操作都是阻塞的，即在等待IO过程中线程会被挂起，进入等待队列，此时线程不占用CPU也无法完成其他工作。
+ 原理:线程在发起IO请求是调用recvfrom，如果用户缓冲区没有数据，就一直等待
+ 实现:BIO
+ 优缺点:优点是实现简单，稳定，一般的网络编程中一个线程处理一个请求，线程之间互不干扰。缺点是高并发情况下大量线程会占用很多资源，可能压垮服务器，而且可能出现线程之间频繁切换，造成系统假死
## 非阻塞模型
+ 描述:线程在等待IO过程中不会进入阻塞态，可以继续去做其他工作，在IO期间，线程会不断去询问操作系统IO是否完成
+ 原理:线程在发起IO请求是调用recvfrom，如果内核缓冲区没有数据就一直轮询询问操作系统内核缓冲区数据是否准备好，如果没有准备好就一直返回一个错误
+ 实现:NIO
+ 优缺点:优点是用户线程不会傻等数据准备好，可以再此期间去完成其他任务，缺点是线程需要主动的不断询问操作系统数据是否准备好
## IO复用模型
+ 描述:linux内核提供一种能力，程序传递需要读取的文件描述符列表给内核，内核帮忙监控这些文件数据是否已经拷贝到内核缓冲区，如果已经拷贝完成主动通知程序
+ 实现:linux 的 select/poll/epoll
## 信号驱动模型
+ 描述:首先开启Socket信号驱动I/O功能，并通过系统调用sigaction执行一个信号处理函数（此系统调用立即返回，进程继续工作，它是非阻塞的）。当数据准备就绪时，就为进程生成一个SIGIO信号，通过信号会掉通知应用程序调用recvfrom来读取数据，并通知主循环函数来处理数据。信号驱动模型与非阻塞模型的区别是程序不用一直询问内核数据是否就绪，而是由内核主动通知。与IO复用模型的区别是线程是完全无阻塞的，IO复用模型的select操作是阻塞的
## 异步IO模型
+ 描述:线程通过系统调用告知内核将磁盘数据拷贝到某个用户缓冲区，此系统调用立即返回。内核会完成整个工作，将数据拷贝到用户缓冲区后通知线程。异步IO模型与信号驱动模型的区别是信号驱动模型的内核只是将数据拷贝到内核空间，最后一步由程序自己完成，而异步IO模型将所有的工作都完成了

# NIO
+ NIO的核的核心是使用一个线程完成多个请求的读写操作，其非阻塞也体现在这一个线程在等待IO时不会挂起阻塞，而是去完成其他任务
+ NIO的最重要的作用是解放了线程，可以我们用但线程发起或者处理大量的请求，对于服务器端来说，提供了承受海量连接的可能。对于客户端来说，可以实现单个线程发起大量请求，比如爬虫类应用
+ NIO的底层是借助操作系统的多路复用技术，NIO的select方法就是调用linux操作系统的select/poll/epoll 系统调用，它并不是单纯的非阻塞模型模型，而是非阻塞模型 + IO复用模型
    

# 多路复用技术
linux内核提供一种能力，程序传递需要读取的文件描述符列表给内核，内核帮忙监控这些文件数据是否已经拷贝到内核缓冲区，如果已经拷贝完成主动通知程序。有三个系统调用都可以达到这个效果 select/poll/epoll。调用这些函数线程会被阻塞，直到有相关文件数据已经准备好，线程才会继续往下走，并且返回已经就绪的文件列表
+ select:初代版本，调用时我们需要将需要监控的文件描述符集合传递给select,select会将这些文件描述符拷贝到内核空间，为了避免性能损耗，内核限制集合大小为1024个，所以select函数可以监控的文件数量有限。其次，文件数据就绪后，select函数只是返回有文件可以读写了，但是并不返回具体哪个文件，所以线程需要遍历集合，这种方式会导致惊群效应。性能会随着监控文件的增多下降，因为会有大量的空轮询
+ poll:select的升级版本，解决了文件描述符集合最大数量限制，但是依旧会出现惊群效应
+ epoll:解决了少量文件就绪导致文件遍历的问题，epoll不再是仅仅通知程序有文件可读写，而是返回一个就绪的文件列表，这样就避免大量无用的遍历

# 零拷贝技术
+ 传统的文件拷贝要经历四个步骤，比如一个ftp请求，文件从本地磁盘拷贝到网卡要经历四步：
    1. 磁盘 -> 内核缓冲区A(DMA拷贝)
    2. 内核缓冲区A -> 用户缓冲区(CPU拷贝)
    3. 用户缓冲区 -> 内核缓冲区B(CPU拷贝)
    4. 内核缓冲区B -> 网卡缓冲区(DMA拷贝)
+ NIO 使用 FileChannel.transferTo() 方法实现零拷贝，可以将上述拷贝步骤简化到3步，用户态和内核态由四次变为两次，且只有一次CPU拷贝
    1. 磁盘 -> 内核缓冲区A(DMA拷贝)
    2. 内核缓冲区A -> 内核缓冲区B(CPU拷贝)
    3. 内核缓冲区B -> 网卡缓冲区(DMA拷贝)
+ 如果底层NIC（网络接口卡）支持gather操作，可以进一步简化，拷贝步骤变为两次，且完全不需要CPU参与
    1. 磁盘 -> 内核缓冲区A(DMA拷贝)
    2. 文件描述符 -> 网卡缓冲区(没有数据拷贝)
    3. 内核缓冲区A -> 网卡缓冲区(DMA拷贝)

# JAVA NIO的基本使用

    public class MyServer {

        public static void main(String[] args) throws IOException {

            ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
            serverSocketChannel.configureBlocking(false);

            ServerSocket serverSocket = serverSocketChannel.socket();
            serverSocket.bind((new InetSocketAddress(9999)));

            //将ServerSocketChannel注册到选择器上去并监听accept事件
            Selector selector = Selector.open();
            serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);

            while (true) {
                //这里是阻塞的，所以严格意义上来说，NIO并不是非阻塞的
                int select = selector.select();
                if (0 == select) {
                    continue;
                }
                Iterator<SelectionKey> iterator = selector.selectedKeys().iterator();
                while (iterator.hasNext()) {
                    SelectionKey selectionKey = iterator.next();

                    if (selectionKey.isAcceptable()) {
                        handleAcceptEvent(selector,selectionKey.channel());
                    }

                    if (selectionKey.isReadable()) {
                        handleReadEvent( selectionKey.channel());
                    }

                    //删除已经处理过就绪 key ，否则下一次select还会返回
                    iterator.remove();
                }
            }
        }

        //客户端请求到来会触发 OP_ACCEPT，我们并不是新创建一个线程从 SocketChannel 读取数据，
        //而是注册将此 SocketChannel 注册到  OP_READ 上，等待下一次 select 被触发，因为请求到来了数据不一定就绪了
        public static void handleAcceptEvent(Selector selector,SelectableChannel channel){
            try {
                ServerSocketChannel acceptChannel = (ServerSocketChannel) channel;
                SocketChannel socketChannel = acceptChannel.accept();
                socketChannel.configureBlocking(false);
                socketChannel.register(selector, SelectionKey.OP_READ);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        //所有的请求都是一个线程处理的，感觉如果存在数据读写速度会很慢，实际上并不会很慢，因为IO的时间主要消耗在数据的等待，数据读写的速度非常快，带宽可以达到1Gbps,时间可以忽略不计
        //单个线程处理所有请求也减少了创建销毁线程的资源消耗，和线程上下文切换的资源消耗
        public static void handleReadEvent(SelectableChannel channel) throws IOException {
            SocketChannel readableChannel = (SocketChannel) channel;
            try {
                ByteBuffer buffer = ByteBuffer.allocate(1024);
                while (readableChannel.read(buffer) > 0){
                    buffer.flip();
                    while (buffer.hasRemaining()){
                        System.out.print((char) buffer.get());
                    }
                    buffer.clear();
                }

                Thread.sleep(1000);
            }catch (IOException e){
                e.printStackTrace();
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                readableChannel.close();
            }

        }
    }