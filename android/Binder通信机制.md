# 概念
+ 对应用层app来说，Binder是一个实现了Ibinder接口，具有跨进程通信能力的类
+ 对FrameWork层来说，Binder是ServiceManager连接各种系统Service，用户Server的桥梁
+ 对Native层，Binder是操作系统的一种跨进程通信方式，利用系统调用实现跨进程数据传递，并在此基础上建立了一套跨进程通信体系
+ 对内核来说，Binder是一种驱动，是一种虚拟设备

# 为什么选择binder
+ 高效: 比起socket，管道等linux原生的IPC方式，Binder利用mmp()实现一次通信只需要一次数据拷贝，效率更高
+ 稳定: 比起linux原生的内存映射方式的IPC，Binder更稳定
+ 改造方便: Binder属于Andoid特有的IPC通信方式，改造优化更方便，有利于建立一套适合android的通信体系

# 基础架构
+ Binder 是Android特有的IPC通信方式，是android最常用的进程间通信方式(也有一些其他方式，比如Zygote通信便是采用socket)。Binder 使用方式很简单，编写好服务端和客户端程序就可以立即进行通信，者得益于Android建立的完整的binder通信模型
+ Binder通信模型是C/S架构，具体涉及四个角色：服务端、客户端、服务管理者、底层驱动
    ![alt “Binder通信架构”](images/IPC-Binder.jpg)
ServiceManager启动以后等待服务端注册服务，这里的ServiceManager是native层的。Server启动后在ServiceManager上注册服务，Client在ServiceManager查询服务，最终调用。图中虚线部分只是逻辑上的通信，实际上客户端于服务端的每次通信都要通过ioctl调用底层驱动达到通信目的
+ ServiceManager是由init进程通过解析init.rc文件而创建的，主要功能就是注册服务和查询服务,对应文件是 service_manager.c,此文件中包含了do_add_service() 和 do_find_service() 分别用来注册服务和查询服务
+ 以上所说的Binder体系都是在native层，但是app都是使用java编写的，所以app要使用binder通信，必须让java层也可以调用到native层的通信机制，android在framework层封装了几个通信工具，于native层binder体系中的角色一一对应，然后使用jni技术打通上下， 就可以让app使用用java语言使用binder通信
    ![alt “Binder通信架构”](images/java_binder.jpg)

# 基本使用流程
+ binder使用时分为客户端和服务端，在使用binder时我们需要定义一个接口，此接口在服务端程序和客户端程序需要保证完全一样(如果担心两端不匹配，可以以sdk的方式由一端提供给另一端)
+ 对于服务端来说，主要就是实现接口的逻辑，逻辑实现之后需要继承 Binder 类，让其具有binder通信能力。此外还需要将服务注册到ServiceManager暴露给客户端

        public class IAccountServiceServer extends Binder implements IAccountService{
            private static final String TAG = "AccountServiceServer";
            public IAccountServiceServer() {
                //注册服务
                this.attachInterface(this, DESCRIPTOR);
            }

            // 实现逻辑，用于本进程调用
            @Override
            public boolean login(String userName, String password) throws RemoteException {
                Log.i(TAG, "username: " + userName + " password: " + password);
                return true;
            }

            // 实现逻辑，用于跨进程调用
            @Override
            protected boolean onTransact(int code, @NonNull Parcel data, @Nullable Parcel reply, int flags) throws RemoteException {
                switch (code) {
                    case TRANSACT_LOGIN:
                        String userName = data.readString();
                        String password = data.readString();
                        return login(userName, password);
                }
                return false;
            }

            @Override
            public IBinder asBinder() {
                return this;
            }
        }


+ 对于客户端需要完成几件事，1) 查询到服务端 2) 获取到服务端binder 3) 于服务端通信

        public class IAccountServiceClient {
            public static abstract class Stub extends Binder implements IAccountService {
                public static IAccountService asInterface(IBinder obj) {
                    if (obj == null) {
                        return null;
                    }
                    // 查询服务
                    IInterface iInterface = obj.queryLocalInterface(DESCRIPTOR);
                    if (iInterface != null && iInterface instanceof IAccountService) {
                        return (IAccountService) iInterface;
                    }
                    // 如果发现不是本进程服务，使用代理类
                    return new AccountServiceProxy(obj);
                }
            }

            // 调用代理类，用于与服务端进行RPC通信
            public static class AccountServiceProxy implements IAccountService {
                private IBinder binder;

                public AccountServiceProxy(IBinder binder) {
                    this.binder = binder;
                }

                @Override
                public boolean login(String userName, String password) throws RemoteException {
                    Parcel data = Parcel.obtain();
                    Parcel reply = Parcel.obtain();
                    data.writeString(userName);
                    data.writeString(password);
                    binder.transact(TRANSACT_LOGIN, data, reply, 0);
                    return reply.readBoolean();
                }

                @Override
                public IBinder asBinder() {
                    return binder;
                }
            }
        }

+ 在使用过程中，服务端一般在Service的onBind() 暴露出服务；客户端使用bindService()绑定服务并通过ServiceConnection回调拿到binder代理，代理的作用是RPC跨进程调用服务。在实际跨进程调用服务时，客户端必须通过 binder.transact() 方法调用服务，服务端则会在 onTransact() 方法中得到客户端的数据

# in、out、inout、oneway
+ in、out、inout 用于修饰AIDL接口的入参，表示AIDL接口的数据流通方向限制
    - 被in修饰的参数，会从客户端传递到服务端，但是服务端对参数的任何修改都不会反馈到客户端
    - 被out修饰的参数，客户端的参数数据不会传递到服务端，但是服务端的修改会反馈到客户端
    - 被inout修饰的参数，服务端会接收到客户端的参数数据，如果存在修改，也会反馈到客户端
+ oneway 是用来修饰AIDL接口的，可以加在接口上也可以加在方法上，被 oneway 修饰的方法不可以有返回值，也不可以存在in，out参数。oneway有异步调用和串行化处理两个特点
    - 异步调用: 调用 oneway 修饰的接口，客户端不必等待binder引擎完成处理，会直接返回
    - 串行化处理: 每个AIDL服务中的多个oneway请求会被串行化，不会并发处理。多个AIDL 服务的Oneway方法会并行执行



# tips
+ 在使用 binderService() 的时候需要注意，ServiceConnection 的回调是异步的，就是说 binderService() 存在返回值，但是仅仅表明被调用的Service服务存在，并不代表链接已经建立完成，连接建立完成的标志是  onServiceConnected() 回调执行，但是由于是异步的，我们不能在 binderService() 后立即进程跨进程访问，因为连接可能还没建立