# ApplicationContext 构建
Spring的 ApplicationContext 是Spring的核心类,它 BeanFactory 的升级版,继承了 BeanFactory 接口,拥有生产bean的能力,它同时扩展了其他的功能,在项目运行过程中 ApplicationContext 对象保存着诸多与容器全局相关的数据

Spring有多种类型的 ApplicationContext 适用与不同的场景.但是基本的结构流程并没有不同,其中最直观的就属 ClassPathXmlApplicationContext ,早期的Spring 通过 xml 文件配置bean.ClassPathXmlApplicationContext就是用来加载xml文件并初始化项目的.代码如下:
    
    public static void main(String[] args) {
        ClassPathXmlApplicationContext classPathXmlApplicationContext = new ClassPathXmlApplicationContext("classpath:bean.xml");
        FundInfo bean1 = classPathXmlApplicationContext.getBean(FundInfo.class);
        System.out.println(bean1.getFundCode());
    }

ClassPathXmlApplicationContext 的构造方法中调用了其父类 AbstractApplicationContext.refresh() 方法,此方法是ApplicationContext加载的核心,代码如下:

    @Override
	public void refresh() throws BeansException, IllegalStateException {
		synchronized (this.startupShutdownMonitor) {
			// Prepare this context for refreshing.
			prepareRefresh();

			// Tell the subclass to refresh the internal bean factory.
			ConfigurableListableBeanFactory beanFactory = obtainFreshBeanFactory();

			// Prepare the bean factory for use in this context.
			prepareBeanFactory(beanFactory);

			try {
				// Allows post-processing of the bean factory in context subclasses.
				postProcessBeanFactory(beanFactory);

				// Invoke factory processors registered as beans in the context.
				invokeBeanFactoryPostProcessors(beanFactory);

				// Register bean processors that intercept bean creation.
				registerBeanPostProcessors(beanFactory);

				// Initialize message source for this context.
				initMessageSource();

				// Initialize event multicaster for this context.
				initApplicationEventMulticaster();

				// Initialize other special beans in specific context subclasses.
				onRefresh();

				// Check for listener beans and register them.
				registerListeners();

				// Instantiate all remaining (non-lazy-init) singletons.
				finishBeanFactoryInitialization(beanFactory);

				// Last step: publish corresponding event.
				finishRefresh();
			}
	}

以上代码中的每个子方法都是加载过程中的一个阶段,挑选几个核心方法记录
1. obtainFreshBeanFactory():获取BeanFactory

    此方法调用了refreshBeanFactory() 和 getBeanFactory() 实现在AbstractRefreshableApplicationContext类中,AbstractRefreshableApplicationContext.createBeanFactory() 是真正创建bean工厂的地方,根据代码可以看到返回的是DefaultListableBeanFactory ,这也是 Spring 默认的bean工厂

        @Override
        protected final void refreshBeanFactory() throws BeansException {
            if (hasBeanFactory()) {
                destroyBeans();
                closeBeanFactory();
            }
            try {
                DefaultListableBeanFactory beanFactory = createBeanFactory();
                beanFactory.setSerializationId(getId());
                customizeBeanFactory(beanFactory);
                loadBeanDefinitions(beanFactory);
                synchronized (this.beanFactoryMonitor) {
                    this.beanFactory = beanFactory;
                }
            }
        }

        protected DefaultListableBeanFactory createBeanFactory() {
            return new DefaultListableBeanFactory(getInternalParentBeanFactory());
        }

2. postProcessBeanFactory():bean初始化前自定义处理

    所有 Bean 的定义已经加载完成，但是没有实例化，这一步可以修改 bean 定义或者增加自定义的 bean.具体实现是依赖 BeanFactoryPostProcessor接口,在容器启动过程中,凡是实现此接口的类,都会自动执行其 postProcessBeanFactory().可以完成一些的自定义的对bean的操作. postProcessBeanFactory() 作用就是用来那个容器中的Bean完成这一功能.
    使用 BeanFactoryPostProcessor代码如下:
        
        public class MyBeanFactoryPostProcessor implements BeanFactoryPostProcessor {
            @Override
            public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
                System.out.println("这里可以修改 BeanFactory 的配置");
            }
        }

3. registerBeanPostProcessors():bean实例化前后自定义处理

    如果需要在bean实例化前后添加一些自定义操作,可以实现 BeanPostProcessor 接口,在容器启动过程中,凡是实现此接口的类,都会自动执行其 postProcessBeforeInitialization() 和 postProcessAfterInitialization(). registerBeanPostProcessors()方法的作用就是用来那个容器中的Bean完成这一功能.
    使用BeanPostProcessor代码如下:

        public class MyBeanPostProcessor implements BeanPostProcessor {

            @Override
            public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
                System.out.println("bean初始化之前的修改:" + beanName);
                return bean;
            }

            @Override
            public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
                System.out.println("bean初始化之后的修改:"+ beanName);
                if (bean instanceof FundInfo){
                    bean = (FundInfo) bean;
                    ((FundInfo) bean).setFundCode("000000");
                }
                return bean;
            }
        }

4. registerListeners():注册监听器

    注册监听器，找出系统中的 ApplicationListener 对象，注册到时间广播器中。如果有需要提前进行广播的事件，则执行广播。

参考:https://juejin.cn/post/6844904039348436999#heading-6


# BeanFactory
+ BeanFactory 是Srping的核心接口之一,Spring 提供了多个BeanFactory接口,BeanFactory,AutowireCapableBeanFactory,ListableBeanFactory等等,这些接口都是为了创建bean服务,BeanFactory是顶层接口,其他接口都继承自它,且都做了一定的功能扩展.Spring默认使用的实现类是 DefaultListableBeanFactory 它几乎实现了所有接口功能,功能复杂而强大.
+ SingletonBeanRegistry 是 DefaultListableBeanFactory 实现的另一个基础接口,此接口是bean实例的注册中心,核心实现类是DefaultSingletonBeanRegistry,如果bean配置为单例模式,则所有的bean都保存在这个类中:

        public class DefaultSingletonBeanRegistry extends SimpleAliasRegistry implements SingletonBeanRegistry {

            /** Cache of singleton objects: bean name to bean instance. */
            private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);

            /** Cache of singleton factories: bean name to ObjectFactory. */
            private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);
        }

# BeanDefinition
+ BeanDefinition接口用于描述bean的元数据信息,在 Spring 中此接口有三种实现：RootBeanDefinition、ChildBeanDefinition 以及 GenericBeanDefinition。而这三种实现都继承了 AbstractBeanDefinition，其中 BeanDefinition 是配置文件元素标签在容器中的内部表示形式。元素标签拥有 class、scope、lazy-init 等属性，BeanDefinition 则提供了相应的 beanClass、scope、lazyInit 属性一一对应
+ Spring 通过 BeanDefinition 将配置文件中的配置信息转换为容器的内部表示，并将这些 BeanDefinition 注册到 BeanDefinitionRegistry 中。Spring 容器的 BeanDefinitionRegistry 就像是 Spring 配置信息的内存数据库，主要以 map 的形式保存，后续操作直接从 BeanDefinitionRegistry 中读取配置信息
+ 加载benn定义的实现在AbstractXmlApplicationContext.loadBeanDefinitions()

        protected void loadBeanDefinitions(XmlBeanDefinitionReader reader) throws BeansException, IOException {
            Resource[] configResources = getConfigResources();
            if (configResources != null) {
                reader.loadBeanDefinitions(configResources);
            }
            String[] configLocations = getConfigLocations();
            if (configLocations != null) {
                reader.loadBeanDefinitions(configLocations);
            }
        }

    关于bean定义的加载可以根据代码一路跟踪到
    AbstractXmlApplicationContext.loadBeanDefinitions() ->
    AbstractBeanDefinitionReader.loadBeanDefinitions() -> 
    BeanDefinitionReader.loadBeanDefinitions() -> 
    XmlBeanDefinitionReader.loadBeanDefinitions()
    至此通过加载 XML 文件， 将xml文件解析为对应的 BeanDefinition ，完成了 Bean 定义的加载和注册

# BeanFactory和FactoryBean区别
+ BeanFactory 是Spring的核心接口之一，负责Bean的查询，定位等方面的管理功能，Spring为其提供了多种实现，比如DefaultListableBeanFactory，ClassPathXmlApplicationContext
+ FactoryBean 是Spring为用户提供的一种可以自定义Bean生产方式的手段，实现了FactoryBean接口的bean本身就成了一个工厂,bean的生成不再经过默认的bean工厂生产，而是直接由FactoryBean生成，可以定制非常个性化的Bean,比如AOP工厂类的实现，ProxyFactoryBean，或者MyBatis的SqlSessionFactoryBean都是以这种方式实现


# Bean实例化流程
1. 实例化BeanFactory,在实例化过程中会扫描所有的bean名称，根据beanname获取到BeanDefinition实例化那些不需要懒加载的bean
2. 实例化时需要为bean注入属性，可以采用构造函数注入也可以使用Setter方法注入
3. 实例化完成后开始注入Aware，所有实现了Aware接口的bean都会调用对应的接口方法
4. 调用BeanPostProcessor的postProcessBeforeInitialization方法
5. 调用Bean的初始化方法
6. 调用BeanPostProcessor的postProcessAfterInitialization方法
7. 注册Bean的销毁方法