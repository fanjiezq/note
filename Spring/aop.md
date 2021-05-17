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

