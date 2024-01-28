# 进程的重要性(http://gityuan.com/2015/10/01/process-lifecycle/)
Android系统将尽量长时间地保持应用进程，但为了新建进程或运行更重要的进程，最终需要清除旧进程来回收内存。 为了确定保留或终止哪些进程，系统会根据进程中正在运行的组件以及这些组件的状态，将每个进程放入“重要性层次结构”中。 必要时，系统会首先消除重要性最低的进程，然后是清除重要性稍低一级的进程，依此类推，以回收系统资源。进程的重要性，划分5级：

1. 前台进程(Foreground process)
2. 可见进程(Visible process)
3. 服务进程(Service process)
4. 后台进程(Background process)
5. 空进程(Empty process)