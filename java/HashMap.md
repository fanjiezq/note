# 实现原理
+ HashMap 简单来说就是一个链表数组，基础是一个数组，每个数组元素是一个链表(Entry)
+ 元素存储时会先对key进行hash计算，然后对数组length取模，确认元素应该保存在数组的哪个位置，如果该位置已经被占用，则比较key值，不相同就保存在当前元素后面，形成链表
+ 当某个链表的数量大于8时，链表会转为红黑树，提升查找效率

# 扩容机制
+ HashMap有两个核心参数，数组大小(capacity)和负载因子(loadFactor)。数组大小不必说默认16，负载因子是为了控制数据的密集程度，默认0.75
+ 当HashMap存储的 元素总数 > capacity * loadFactor,数组容量会扩展到原来的两倍，扩容的目的是为了减少hash碰撞，碰撞越多，链表就越长，查询插入和查询效率越低
+ 还有一种情况会触发扩容，就是元素不多，但是也形成了比较长的链表，但是此时数组太小(小于64)会进行扩容，虽然元素数量没有达到标准，但是数据分布不均匀，进行一次扩容成本很低，但是能很好的解决问题

# 线程安全问题
+ HashMap的resize过程在多线程并发调用时，可能出现死循环
+ HashMap的put方法并没有锁机制，如果A，B两个线程同时put数据，A在hash计算完成后恰好时间片用完，B此时正常插入数据，等到A再次运行时不会在重新Hash而是直接插入数据，就会导致A覆盖了B的数据
+ 迭代器的快速失败问题，当HashMap使用迭代器遍历时，另一个线程添加或者删除了元素，迭代器会立即抛出异常

# ConcurrentHashMap
## jdk7实现
+ 底层依旧是链表数组的形式，但是在最外层加了Segment概念，每个 Segment 管理一个链表数组，在数据插入和查询要经过两次hash,先找到所在的segment,然后定位存储在数组的位置。
+ Segment 的数量是可以配置的，但是一定是2的指数倍，Segment 在对象创建的时候确定，一旦确定无法再修改，避免修改引起整体rehash,所以很自然的ConcurrentHashMap在扩容时也是单个segment进行扩容的
+ 针对put操作，使用局部加锁的方式保证数据安全和高性能。Segment 继承了ReentrantLock，所以它本身就是一个锁，所以在进行数据存储时，会对Segment加锁，只要数据分布在不同的Segment，数据存储完全的隔离，不会出现竞争的情况。线程获取锁时首先尝试使用自旋锁，自旋一定次数后转为阻塞锁
+ 针对get操作，使用 volatile 变量保证变量可见性，保证get操作时之前所有对变量的修改都可见
+ 针对遍历操作，ConcurrentHashMap 支持在遍历过程中修改容器数据，且修改对后续遍历可见、

## JDK8 实现
+ jdk7的分段锁实现使 ConcurrentHashMap 理论上最大并发度为 Segment 个数，但是其寻址多了一次hash操作，JDK8 抛弃了 Segment 概念，其底层数据结构又变回 HashMap 一样，只有一个链表数组，不同的是在进行数据存储时，如果链表已经存在元素，就对链表的第一个元素使用 synchronized 加锁，也可以保证线程安全，且实现更简单
+ 此外当链表长度超过8时，链表会变为红黑树形式 