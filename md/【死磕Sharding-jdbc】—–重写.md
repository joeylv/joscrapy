  * 1 表名重写分析
  * 2 offset重写分析
  * 3 rowCount重写分析
  * 4 appendRest分析
  * 5 SQLBuilder.toString()分析

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/c7854327634f>

* * *

核心源码就在`sharding-jdbc-
core`模块的`com.dangdang.ddframe.rdb.sharding.rewrite`目录下，包含两个文件 **SQLBuilder** 和
**SQLRewriteEngine** ；测试用例入口为 **SQLRewriteEngineTest**
，下面从SQLRewriteEngineTest中debug源码分析sharding-jdbc的重写是如何实现的：

SQLRewriteEngineTest中某个测试用例如下–主要包括都表名，offset，limit（rowCount）的重写：

    
    
    @Test
    public void assertRewriteForLimit() {
        selectStatement.setLimit(new Limit(true));
        // offset的值就是limit offset,rowCount中offset的值
        selectStatement.getLimit().setOffset(new LimitValue(2, -1));
        // rowCount的值就是limit offset,rowCount中rowCount的值
        selectStatement.getLimit().setRowCount(new LimitValue(2, -1));
        // TableToken的值表示表名table_x在原始SQL语句的偏移量是17的位置
        selectStatement.getSqlTokens().add(new TableToken(17, "table_x"));
        // OffsetToken的值表示offset在原始SQL语句的偏移量是33的位置（2就是offset的值）
        selectStatement.getSqlTokens().add(new OffsetToken(33, 2));
        // RowCountToken的值表示rowCount在原始SQL语句的偏移量是36的位置（2就是rowCount的值）
        selectStatement.getSqlTokens().add(new RowCountToken(36, 2));
        // selectStatement值模拟过程，实际上是SQL解释过程（SQL解释会单独分析）
        SQLRewriteEngine rewriteEngine = new SQLRewriteEngine(shardingRule, "SELECT x.id FROM table_x x LIMIT 2, 2", selectStatement);
        // 重写的核心就是这里了：rewriteEngine.rewrite(true)
        assertThat(rewriteEngine.rewrite(true).toSQL(tableTokens), is("SELECT x.id FROM table_1 x LIMIT 0, 4"));
    }
    

重写方法核心源码：  
从这段源码可知，sql重写主要包括对表名，limit offset, rowNum以及order by的重写（ItemsToken值对select
col1, col2 from… 即查询结果列的重写–需要由于ordre by或者group by需要增加一些结果列）；

    
    
    public SQLBuilder rewrite(final boolean isRewriteLimit) {
        SQLBuilder result = new SQLBuilder();
        if (sqlTokens.isEmpty()) {
            result.appendLiterals(originalSQL);
            return result;
        }
        int count = 0;
        // 根据Token的beginPosition即出现的位置排序
        sortByBeginPosition();
        for (SQLToken each : sqlTokens) {
            if (0 == count) {
                // 第一次处理：截取从原生SQL的开始位置到第一个token起始位置之间的内容，例如"SELECT x.id FROM table_x x LIMIT 2, 2"这条SQL的第一个token是TableToken，即table_x所在位置，所以截取内容为"SELECT x.id FROM "
                result.appendLiterals(originalSQL.substring(0, each.getBeginPosition()));
            }
            if (each instanceof TableToken) {
                // 看后面的"表名重写分析"
                appendTableToken(result, (TableToken) each, count, sqlTokens);
            } else if (each instanceof ItemsToken) {
                // ItemsToken是指当逻辑SQL有order by，group by这样的特殊条件时，需要在select的结果列中增加一些结果列，例如执行逻辑SQL:"SELECT o.* FROM t_order o where o.user_id=? order by o.order_id desc limit 2,3"，那么还需要增加结果列o.order_id AS ORDER_BY_DERIVED_0 
                appendItemsToken(result, (ItemsToken) each, count, sqlTokens);
            } else if (each instanceof RowCountToken) {
                // 看后面的"rowCount重写分析"
                appendLimitRowCount(result, (RowCountToken) each, count, sqlTokens, isRewriteLimit);
            } else if (each instanceof OffsetToken) {
                // 看后面的"offset重写分析"
                appendLimitOffsetToken(result, (OffsetToken) each, count, sqlTokens, isRewriteLimit);
            } else if (each instanceof OrderByToken) {
                appendOrderByToken(result, count, sqlTokens);
            }
            count++;
        }
        return result;
    }
    
    private void sortByBeginPosition() {
        Collections.sort(sqlTokens, new Comparator<SQLToken>() {
            // 生序排列
            @Override
            public int compare(final SQLToken o1, final SQLToken o2) {
                return o1.getBeginPosition() - o2.getBeginPosition();
            }
        });
    }
    

## 表名重写分析

    
    
    private void appendTableToken(final SQLBuilder sqlBuilder, final TableToken tableToken, final int count, final List<SQLToken> sqlTokens) {
        String tableName = sqlStatement.getTables().getTableNames().contains(tableToken.getTableName()) ? tableToken.getTableName() : tableToken.getOriginalLiterals();
        // append表名特殊处理
        sqlBuilder.appendTable(tableName);
        int beginPosition = tableToken.getBeginPosition() + tableToken.getOriginalLiterals().length();
        appendRest(sqlBuilder, count, sqlTokens, beginPosition);
    }
    
    // append表名特殊处理，把TableToken也要添加到SQLBuilder中（List<Object> segments）
    public void appendTable(final String tableName) {
        segments.add(new TableToken(tableName));
        currentSegment = new StringBuilder();
        segments.add(currentSegment);
    }
    

## offset重写分析

    
    
    private void appendLimitOffsetToken(final SQLBuilder sqlBuilder, final OffsetToken offsetToken, final int count, final List<SQLToken> sqlTokens, final boolean isRewrite) {
        // offset的重写比较简单：如果要重写，则offset置为0，否则保留offset的值；
        sqlBuilder.appendLiterals(isRewrite ? "0" : String.valueOf(offsetToken.getOffset()));
        int beginPosition = offsetToken.getBeginPosition() + String.valueOf(offsetToken.getOffset()).length();
        appendRest(sqlBuilder, count, sqlTokens, beginPosition);
    }
    

## rowCount重写分析

    
    
    private void appendLimitRowCount(final SQLBuilder sqlBuilder, final RowCountToken rowCountToken, final int count, final List<SQLToken> sqlTokens, final boolean isRewrite) {
        SelectStatement selectStatement = (SelectStatement) sqlStatement;
        Limit limit = selectStatement.getLimit();
        if (!isRewrite) {
            // 如果不需要重写sql中的limit的话（例如select * from t limit 10），那么，直接append rowCount的值即可；
            sqlBuilder.appendLiterals(String.valueOf(rowCountToken.getRowCount()));
        } else if ((!selectStatement.getGroupByItems().isEmpty() || !selectStatement.getAggregationSelectItems().isEmpty()) && !selectStatement.isSameGroupByAndOrderByItems()) {
            // 如果要重写sql中的limit的话，且sql中有group by或者有group by & order by，例如""SELECT o.* FROM t_order o where o.user_id=? group by o.order_id order by o.order_id desc limit 2,3"需要"，那么重写为Integer.MAX_VALUE，原因在下文分析，请点击连接：
            sqlBuilder.appendLiterals(String.valueOf(Integer.MAX_VALUE));
        } else {
            // 否则只需要将limit offset,rowCount重写为limit 0, offset+rowCount即可；
            sqlBuilder.appendLiterals(String.valueOf(limit.isRowCountRewriteFlag() ? rowCountToken.getRowCount() + limit.getOffsetValue() : rowCountToken.getRowCount()));
        }
        int beginPosition = rowCountToken.getBeginPosition() + String.valueOf(rowCountToken.getRowCount()).length();
        appendRest(sqlBuilder, count, sqlTokens, beginPosition);
    }
    

## appendRest分析

    
    
    private void appendRest(final SQLBuilder sqlBuilder, final int count, final List<SQLToken> sqlTokens, final int beginPosition) {
        // 如果SQL解析后只有一个token，那么结束位置（endPosition）就是sql末尾；否则结束位置就是到下一个token的起始位置
        int endPosition = sqlTokens.size() - 1 == count ? originalSQL.length() : sqlTokens.get(count + 1).getBeginPosition();
        sqlBuilder.appendLiterals(originalSQL.substring(beginPosition, endPosition));
    }
    

>
所有重写最后都会调用appendRest()，即附加上余下部分内容，这个余下部分内容是指从当前处理的token到下一个token之间的内容，例如SQL为`SELECT
x.id FROM table_x x LIMIT 5,
10`，当遍历到`table_x`，即处理完TableToken后，由于下一个token为OffsetToken，即5，所以appendRest就是append这一段内容：”
x LIMIT “–从table_x到5之间的内容；

## SQLBuilder.toString()分析

重写完后，调用SQLBuilder的toString()方法生成重写后最终的SQL语句；

    
    
    public String toSQL(final Map<String, String> tableTokens) {
        StringBuilder result = new StringBuilder();
        for (Object each : segments) {
            // 如果是TableToken，并且是分库分表相关表，那么append最终的实际表名，例如t_order的实际表名可能是t_order_1
            if (each instanceof TableToken && tableTokens.containsKey(((TableToken) each).tableName)) {
                result.append(tableTokens.get(((TableToken) each).tableName));
            } else {
                result.append(each);
            }
        }
        return result.toString();
    }
    

