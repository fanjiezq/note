# 七种事务传播机制
1. PROPAGATION_REQUIRED —— 支持当前事务，如果当前没有事务，则新建一个事务，这是最常见的选择，也是 Spring 默认的一个事务传播属性。
2. PROPAGATION_SUPPORTS —— 支持当前事务，如果当前没有事务，则以非事务方式执行。
3. PROPAGATION_MANDATORY —— 支持当前事务，如果当前没有事务，则抛出异常。
4. PROPAGATION_REQUIRES_NEW —— 新建事务，如果当前存在事务，把当前事务挂起。
5. PROPAGATION_NOT_SUPPORTED —— 以非事务方式执行操作，如果当前存在事务，就把当前事务挂起。
6. PROPAGATION_NEVER —— 以非事务方式执行，如果当前存在事务，则抛出异常。
7. PROPAGATION_NESTED —— Nested的事务和它的父事务是相依的，它的提交是要等和它的父事务一块提交的
