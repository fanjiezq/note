# 七种事务传播机制
spring的事务由容器统一管理，每个方法都可以加上事务，那么方法调用时涉及多个事务，事务如何处理就会成为问题，处理的方式就是事务传播机制；spring提供了7种事务传播机制。
下面的例子都是以如下代码进行讲解：

  public void B(){}
  
  public void A(){
    B();
  }
 
1. PROPAGATION_REQUIRED:需要事务；如果当前上下文没有事务，新建事务；如果上下文存在事务,加入当前事务;是 Spring 默认的一个事务传播属性。
3. PROPAGATION_SUPPORTS:支持事务；如果当前上下文没有事务直接执行；如果上下文存在事务,加入当前事务
4. PROPAGATION_MANDATORY:必须事务；如果当前上下文没有事务，抛出异常；如果上下文存在事务,加入当前事务
5. PROPAGATION_REQUIRES_NEW:新建事务；如果当前上下文没有事务，新建事务；如果上下文存在事务,挂起当前事务，新建自己的事务，本事务执行完成后再释放上下文事务，两个事务时间并无关系
6. PROPAGATION_NOT_SUPPORTED:不需要事务；如果当前上下文有事务，挂起当前事务，执行完成后再释放当前事务
7. PROPAGATION_NEVER:不能存在事务；如果当前存在事务，则抛出异常。
8. PROPAGATION_NESTED:与REQUIRED级别类似，与上下文事务一起提交，但是失败时会滚到savepoint点
