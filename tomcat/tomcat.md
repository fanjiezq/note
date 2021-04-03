# 综述
+ tomcat是一个服务器容器,它基于java Servlet,组件和容器三个概念构建起整个体系
+ java Servlet程序是一个按照Servlet规范编写一个Java类,他用于对某个场景的请求进行处理
+ Servet类本身并不能独立运行,它需要被一个平台进行管理,这就是容器,容器是一个可以独立运行的服务器,但是它没有处理请求的能力,只能根据请求的类型调用不同的Servet类处理请求
+ 除了处理请求本身,服务器还需要完成一些额外的任务,比如日志记录,session管理,权限管理等功能,为了系统的可扩展性,容器本身并不提供这些功能,而是利用外部类来实现,这些外部类就是tomcat的各个组建
+ 在tomcat中,container相当于一个管家,它的手下有一帮办事的人员,他名义上提供各种功能,暴露出功能入口但是本身并不实现这些功能,具体的功能是由各个组件完成.这种架构使系统非常灵活,各个组件可以随意插拔,也可以随意替换.

# connector
+ 创建ServerSocket对象,不断监听并接受http请求,关联一个container,将请求封装为request,resopnse对象,调用container方法处理请求
+ connector的核心功能是解析和封装请求,利用HttpProcessor解析请求头,请求体,请求参数等等,这一过程非常耗费性能,所以一个 connector 含有多个 HttpProcessor 对象,在connector初始化的时候就已经创建了一个HttpProcessor pool
+ HttpProcessor实现了Runnable 接口,实际运行时每个请求对应一个HttpProcessor对象,以并行的方式处理请求,所以当HttpProcessor pool的资源没有耗尽时,connector对请求的处理是非阻塞的

# container
+ container负责调度管理Servlet处理,它依靠一系列组建完成调度,包含Loader,Logger,Pipeline,Valve等
  - Loader: 负责加载Servlet
  - Valve:代表container需要完成的一个任务
  - Pipeline: 封装了container需要处理的所有任务集合,其中元素就是Valve.每个continaer都有一个Pipeline,并且在其中添加一个基础Valve
+ tomcat体系中有多种 container ,每一种 container 可以处理的业务的范围不同,范围从大到小依次是 Engine > Host > Context > Wrapper ,每个大范围的continer 可以包含多个小范围的 container,这种结构可以让处理逻辑分层
  - Engine:顶级host,代表一个servlet引擎,当需要一个tomcat实例支持多个虚拟ip地址可以使用.它不可以有父容器,它的子容器必须是Host
  - Host: 代表一个虚拟ip,一般使用这个作为最上层的容器,因为一般一个tomcat实例只需要支持一个ip,它的子容器必须是Context
  - Context: 代表一个application应用,它可以拥有多个Wrapper作为子container,根据请求的业务类型选择合适的Wrapper处理请求
  - Wrapper: 最小范围的 container,每个Wrapper对应的一类请求处理逻辑.它不可以有子container

# Server and Servie
- 一个connector只能监听一个端口,服务器有时需要多个端口.比如需要同时监听80和443,此外服务器也需要一种简单方式开启和关闭整个tomcat(很多组件之间并没有从属关系,开始或关闭时需要单独处理)
- Server 也是一个组件,它i代表整个tomcat服务器,换句话说代表所有组件集合, 使用Server可以总整体上管理tomcat的组件
- Server 利用 Servie 管理组件,Servie包含一个container和多个connector,还提供start(),stop()等生命周期方法,通过这些生命周期方法,可以统一管理所有组件的生命周期,支持多个connector可以让服务器监听多个端口

# Loader
+ tomcat的servlet类加载使用类加载器进行加载,servlet类会存放在一个固定的位置,称为仓库,一般在/webroot目录下,tomcat的类加载器会在这个目录及其子目录下寻找servlet类,并载入到内存
+ 需要注意的是.tomcat的类加载并没有使用java双亲委派机制,她提供自定义的类加载器,并限制只能在特定的目录下加载类,这么做主要为了安全,不允许类加载器拥有太大的权限
+ 所有类加载器实现Loader接口,作为组件的形式与容器进行绑定,当容器需要某个特定servlet,会先调用getClassLoader()获取到类加载器,然后调用loadClass()获取servlet
+ tomcat还存在一个Reloader接口,用于tomcat类的热更新,它启动一个线程实时监控仓库中的类是否发生变化,如果存在类发生变化就自动重载,实现热更新
+ tomcat提供的默认类加载器是 WebappLoader,当此类加载器启动后成如下工作:
  - Creating a class loader
  - Setting repositories
  - Setting the class path
  - Setting permissions
  - Starting a new thread for auto-reload

# Logger
+ tomcat利用日志打印组建记录日志,Logger作为组件与可以与container绑定,负责具体的日志输出工作,Container接口提供setLogger()方法用于这一绑定动作
+ tomcat中的日志输出类型分为三类,SystemOutLogger|SystemErrLogger|FileLogger,FileLogger是三者中最复杂也是功能最强大的,它可以把日志文件输出到文件,并且自动根据日期的变化每天都生成一个新日志文件,避免日志文件无线膨胀
+ tomcat的日志体系与其他日志体系一样也是分级的,系统的默认日志级别可以配置,低于系统配置级别的日志不予输出

# Lifecycle
+ tomcat的各个组件一般都具有生命周期,为了管理方便,组建都实现了Lifecycle接口,实现Lifecycle接口的组建可以被container以统一的方式管理生命周期
+ 接口提供了start(),stop(),addLifecycleListener()等方法,以及生命周期状态转换时的事件类型和事件监听,如果我们需要在组建到达某个生命周期时进行一些业务处理(比如组建停止时回收数据),就可以为该组件的某个生命周期添加事件监听,这种方式可以非常见简单在组件的各个生命周期做个性化处理

# Session Management
+ 很多场景客户端需要服务端记录请求的状态(比如暂记住用户名密码),session可以实现会话级别的请求状态存储,所谓会话级别只是一个概念,本质上是服务端可以一段时间(比如30秒)记录一个客户的请求状态数据,从第一个请求开始,到服务器的记录时间结束都称作一个会话,一旦超时,会话结束则此客户被暂存的数据就被删除了,每个会话都有一个唯一id,它的身份标识,同时与客户端进行映射
+ tomcat的会话体系由三个组件构成:
  - Session:代表一个会话,它保存了会话的数据,和当前会话的最近一次访问时间
  - Manager:管理会话,每个Session对象必须对应一个manager,一个manage可以管理多个会话对象.manager与容器绑定,容器通过manager管理所有的会话,比如创建,获取,失效,删除
  - Stores:Tomcat的会话数据存储方式有多种,可以单纯存储在内存,也可以存储在文件和数据库,每种存储方式存储的位置虽然不同,但是基本操作一致.将这些操作抽象出来形成一个Stores接口,没种方式都是一个Stores实现,这种方式使得tomcat可以很轻松的切换会话的存储方式.
+ 默认情况下会话的数据存储在内存中,但是总有一些情况需要数据的持久化(比如活动状态的会话过多,缓存不够),此时manager会选择部分会话数据移动到文件中存储,需要时再进行加载
+ manager会开启一个后台线程,定时监听每个会话的最近一次访问时间,如果客户端长时间不发出请求(默认60秒),会话会自动失效.同时如果失效的会话信息存储在文件中,文件中的会话数据也会删除

# Security
+ 开启认证授权功能后,客户端只有认证授权通过才可以进行资源访问,tomcat的认证授权体系由以下几个类完成
  - SecurityConstraint:资源访问限制,此类可以让我们配置哪些类型的请求需要认证授权 ,比如post类型方法,或者url = /,在启动时与容器绑定
  - LoginConfig:此类主要用于保存配置认证授权流程的基本信息i,认证授权类型,数据源名称,认证失败页面等等,在启动时与容器绑定
  - Authenticator:进行认证授权动作的类,它是被动态加载的,在tomcat启动后根据配置的认证类型加载对应的Authenticator赋予给容器
  - Realm:身份域,是一个权限仓库,内部保存了当前系统支持的所有的身份信息和每个用户对应的角色,Authenticator根据客户端传递的身份标识从Realm中查询用户是否存在,权限是否符合要求
  - Principal:权限实体,每个Principal中包含了一个用户身份标识和它对应的角色
  
# tomcat处理http请求流程
1. connector监听到请求到来,封装请求,调用关联的container的invoke()方法,一般与connector绑定的容器是Host,所以调用Host的invoke()
2. Host 作为容器,默认含有一个Pipeline,它的invoke()方法中并没有实际业务逻辑,而是调用自己的Pipeline.invoke()
3. Pipeline封装了此容器需要处理的任务Valve,它invoke()方法中以类似责任链的方式调用所有Valve的invoke()方法
4. Host的Pipeline中所有Valve执行完成后 ,会获取到自己的子容器Context,并调用Context.invoke()
5. Context.invoke()内部处理逻辑与Host类似,最后调用子容器Wrapper的invoke()方法,其内部也是调用自己Pipeline
6. Wrapper是最底层的容器,负责真正的业务处理, 负责执行执行请求含有的过滤器,加载Servlet完成请求的处理.