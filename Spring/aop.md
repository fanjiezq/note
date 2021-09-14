# 基本介绍
+ AOP一般用于处理系统中多个模块共有的逻辑抽离封装,比如日志打印,事物处理,权限控制等,便于减少系统的重复代码，降低模块间的耦合度
+ AOP是基于动态代理模式实现的,如果要代理的对象实现了某个接口，那么 Spring AOP 会使用 JDK Proxy，去创建代理对象，而对于没有实现接口的对象无法使用Proxy,会使用 Cglib 生成一个被代理对象的子类来作为代理,当然也可以指定用哪种方式. 如何基于动态代理呢,比如web项目的Controller层每个路由方法都需要打印入参和出参,那就使用动态代理技术在每个路由方法的前后加上打印日志的功能

# 代理类的创建
1. aop解析
    
    无论是早期xml方式配置aop,还是后来基于注解的解析,本质都是基于aop的几个概念(切面,织入等)进行一个策略配置,让容器能够知道我们需要在哪些地方加入什么逻辑.spring存在一系列的接口和类进行这些解析工作.具体实现是AspectJAwareAdvisorAutoProxyCreator 和 AbstractAdvisorAutoProxyCreator
    
2. 生成 Proxy
    解析配置的的最终目的是为了生成合适的代理类,AbstractAutoProxyCreator.createProxy() 方法完成了这个工作,代码如下:

        protected Object createProxy(Class<?> beanClass, @Nullable String beanName,
			@Nullable Object[] specificInterceptors, TargetSource targetSource) {

            if (this.beanFactory instanceof ConfigurableListableBeanFactory) {
                AutoProxyUtils.exposeTargetClass((ConfigurableListableBeanFactory) this.beanFactory, beanName, beanClass);
            }

            ProxyFactory proxyFactory = new ProxyFactory();
            proxyFactory.copyFrom(this);

            if (!proxyFactory.isProxyTargetClass()) {
                if (shouldProxyTargetClass(beanClass, beanName)) {
                    proxyFactory.setProxyTargetClass(true);
                }
                else {
                    evaluateProxyInterfaces(beanClass, proxyFactory);
                }
            }

            Advisor[] advisors = buildAdvisors(beanName, specificInterceptors);
            proxyFactory.addAdvisors(advisors);
            proxyFactory.setTargetSource(targetSource);
            customizeProxyFactory(proxyFactory);

            proxyFactory.setFrozen(this.freezeProxy);
            if (advisorsPreFiltered()) {
                proxyFactory.setPreFiltered(true);
            }

            return proxyFactory.getProxy(getProxyClassLoader());
	    }
    
    最后一行的 proxyFactory.getProxy(getProxyClassLoader()) 是最终创建Proxy的地方,可能会调用两个类CglibAopProxy.getProxy() 和 JdkDynamicAopProxy.getProxy()

# AOP 失效场景
(1) 在一个类内部调用时，被调用方法的 AOP 声明将不起作用。
(2) 对于基于接口动态代理的 AOP 事务增强来说，由于接口的方法都必然是 public ，这就要求实现类的实现方法也必须是 public 的（不能是 protected、private 等），同时不能使用 static 的修饰符。所以，可以实施接口动态代理的方法只能是使用 public 或 public final 修饰符的方法，其他方法不可能被动态代理，相应的也就不能实施 AOP 增强，换句话说，即不能进行 Spring 事务增强了。
(3) 基于 CGLib 字节码动态代理的方案是通过扩展被增强类，动态创建其子类的方式进行 AOP 增强植入的。由于使用 final、static、private 修饰符的方法都不能被子类覆盖，这些方法将无法实施 AOP 增强。所以方法签名必须特别注意这些修饰符的使用，以免使方法不小心成为事务管理的漏网之鱼。

# AOP 实现
+ AOP在实现的方式就是新建一个代理类来替换原始Bean,这个代理类Bean与普通的类Bean在本质上并无不同，它的改造过程也是Bean实例化步骤中的一环
+ Spring中的每个Bean最终都会被定义为一个BeanDefinition描述，普通Bean对应的是GenericBeanDefinition，而aop代理类对应的是 advisorBeanDefinition，在类加载过程中如果发现了某些类符合AOP的匹配规则就会建立advisorBeanDefinition，最终获取到的Bean就是代理类
+ Spring的代理Bean有两种生成方式，对接口方法的代理使用java的动态代理类实现，没有接口方法的代理使用cglib实现