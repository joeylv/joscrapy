  * 1 SQL解析结果初探
  * 2 SQL解析分析
    * 2.1 1\. 得到LexerEngine
    * 2.2 2\. 获取第一个token
      *         * 2.2.0.1 nextToken()分析
    * 2.3 3\. 得到SQL解析器
    * 2.4 4\. SQL解析

> 原文作者：[阿飞Javaer](https://www.jianshu.com/u/6779ec81d3b7)  
>  原文链接：<https://www.jianshu.com/p/3c6138b0426d>

* * *

sharding-
jdbc对SQL解析的源码主要在下图所示parsing模块中，由下图可知SQL解析主要分为两部分：lexer和parser。lexer就是本文需要分析的词法分析：

![201805271001](http://cmsblogs.qiniudn.com/201805271001.png)

sharding-jdbc sql解析  
  
<table>  
<tr>  
<th>

SQL

</th>  
<th>

com.dangdang.ddframe.rdb.sharding.parsing.lexer.token.Token

</th> </tr>  
<tr>  
<td>

/*! hello, afei */

</td>  
<td>

跳过

</td> </tr>  
<tr>  
<td>

delete

</td>  
<td>

(type=DELETE, literals=delete, endPosition=24)

</td> </tr>  
<tr>  
<td>

ignore

</td>  
<td>

(type=IGNORE, literals=ignore, endPosition=31)

</td> </tr>  
<tr>  
<td>

from

</td>  
<td>

(type=FROM, literals=from, endPosition=36)

</td> </tr>  
<tr>  
<td>

`t_user`

</td>  
<td>

(type=IDENTIFIER, literals=`t_user`, endPosition=45)

</td> </tr>  
<tr>  
<td>

where

</td>  
<td>

(type=WHERE, literals=where, endPosition=51)

</td> </tr>  
<tr>  
<td>

user_id

</td>  
<td>

(type=IDENTIFIER, literals=user_id, endPosition=59)

</td> </tr>  
<tr>  
<td>

=

</td>  
<td>

(type=EQ, literals==, endPosition=60)

</td> </tr>  
<tr>  
<td>

?

</td>  
<td>

(type=QUESTION, literals=?, endPosition=61)

</td> </tr>  
<tr>  
<td>

</td>  
<td>

(type=END, literals=, endPosition=62)

</td> </tr> </table>

分析sharding-jdbc源码的词法分析之前，先大概说一下词法分析是干嘛的，后面理解起来就会更容易，例如对于SQL： _“/! hello, afei
/delete ignore from`t_user` where user_id=? “_ 而言，词法分析结果如下：  
  
<table>  
<tr>  
<th>

SQL

</th>  
<th>

com.dangdang.ddframe.rdb.sharding.parsing.lexer.token.Token

</th> </tr>  
<tr>  
<td>

/*! hello, afei */

</td>  
<td>

跳过

</td> </tr>  
<tr>  
<td>

delete

</td>  
<td>

(type=DELETE, literals=delete, endPosition=24)

</td> </tr>  
<tr>  
<td>

ignore

</td>  
<td>

(type=IGNORE, literals=ignore, endPosition=31)

</td> </tr>  
<tr>  
<td>

from

</td>  
<td>

(type=FROM, literals=from, endPosition=36)

</td> </tr>  
<tr>  
<td>

`t_user`

</td>  
<td>

(type=IDENTIFIER, literals=`t_user`, endPosition=45)

</td> </tr>  
<tr>  
<td>

where

</td>  
<td>

(type=WHERE, literals=where, endPosition=51)

</td> </tr>  
<tr>  
<td>

user_id

</td>  
<td>

(type=IDENTIFIER, literals=user_id, endPosition=59)

</td> </tr>  
<tr>  
<td>

=

</td>  
<td>

(type=EQ, literals==, endPosition=60)

</td> </tr>  
<tr>  
<td>

?

</td>  
<td>

(type=QUESTION, literals=?, endPosition=61)

</td> </tr>  
<tr>  
<td>

</td>  
<td>

(type=END, literals=, endPosition=62)

</td> </tr> </table>

## SQL解析结果初探

前面分析SQL重写的时，其测试用例代码在 **SQLRewriteEngineTest.java**
中，列举其中一个用例源码如下，assertRewriteForLimit()方法中的selectStatement就是SQL解析的结果：

    
    
    @Before
    public void setUp() {
        // 定义sharding规则
        shardingRule = new ShardingRuleMockBuilder()
                // table_x表的主键列是id
                .addGenerateKeyColumn("table_x", "id")
                // table_x和table_y是绑定表关系
                .addBindingTable("table_y").build();
        selectStatement = new SelectStatement();
        tableTokens = new HashMap<>(1, 1);
        // 逻辑表table_x对应的实际表是table_1
        tableTokens.put("table_x", "table_1");
    }
    
    @Test
    public void assertRewriteForLimit() {
        selectStatement.setLimit(new Limit(true));
        selectStatement.getLimit().setOffset(new LimitValue(2, -1));
        selectStatement.getLimit().setRowCount(new LimitValue(2, -1));
        selectStatement.getSqlTokens().add(new TableToken(17, "table_x"));
        selectStatement.getSqlTokens().add(new OffsetToken(33, 2));
        selectStatement.getSqlTokens().add(new RowCountToken(36, 2));
        // SelectStatement就是SQL解析的结果
        SQLRewriteEngine rewriteEngine = new SQLRewriteEngine(shardingRule, "SELECT x.id FROM table_x x LIMIT 2, 2", selectStatement);
        assertThat(rewriteEngine.rewrite(true).toSQL(tableTokens), is("SELECT x.id FROM table_1 x LIMIT 0, 4"));
    }
    

## SQL解析分析

核心类为`com.dangdang.ddframe.rdb.sharding.parsing.SQLParsingEngine.java`，核心源码如下：

    
    
    @RequiredArgsConstructor
    public final class SQLParsingEngine {
    
        // 数据库类型，例如MySQL，Oracle等
        private final DatabaseType dbType;
    
        // 原SQL（解析前的SQL）
        private final String sql;
    
        // sharding分库分表规则
        private final ShardingRule shardingRule;
    
        public SQLStatement parse() {
        LexerEngine lexerEngine = LexerEngineFactory.newInstance(dbType, sql);
        lexerEngine.nextToken();
        SQLParser sqlParser = SQLParserFactory.newInstance(
                dbType,
                lexerEngine.getCurrentToken().getType(), shardingRule, lexerEngine);
        SQLStatement result = sqlParser.parse();
        return result;
    }
    

>
从parse()方法的结果可知，SQL解析的结果就是SQLStatement，上面的测试用例是SelectStatement，是SQLStatement的子类，关系如下图所示：

### 1\. 得到LexerEngine

对应源码为`LexerEngine lexerEngine = LexerEngineFactory.newInstance(dbType,
sql);`，核心实现源码如下：

    
    
    @NoArgsConstructor(access = AccessLevel.PRIVATE)
    public final class LexerEngineFactory {
    
        public static LexerEngine newInstance(final DatabaseType dbType, final String sql) {
            // 不同的数据库类型获取LexerEngine不一样（主要是关键词不一样），从这里可知H2和MySQL的解析完全一致
            switch (dbType) {
                case H2:
                case MySQL:
                    return new LexerEngine(new MySQLLexer(sql));
                case Oracle:
                    return new LexerEngine(new OracleLexer(sql));
                case SQLServer:
                    return new LexerEngine(new SQLServerLexer(sql));
                case PostgreSQL:
                    return new LexerEngine(new PostgreSQLLexer(sql));
                default:
                    throw new UnsupportedOperationException(String.format("Cannot support database [%s].", dbType));
            }
        }
    }
    

> 从这里可知，sharding-
jdbc只支持这些数据库：H2，MySQL，Oracle，SQLServer，PostgreSQL；其他数据库如DB2是不支持的；

以Mysql数据库为例，获取MySQLLexer源码如下，可知Lexer两个主要属性为SQL和关键词字典：

    
    
    // 词法分析器的这几个属性比较重要，贯穿整个SQL解析过程
    @RequiredArgsConstructor
    public class Lexer {
    
        // 待解析的SQL语句
        @Getter
        private final String input;
    
        // 字典属性下面有解析，主要包括数据库对应的所有关键词
        private final Dictionary dictionary;
    
        // 解析SQL的位置偏移量
        private int offset;
    
        // 当前解析的token
        @Getter
        private Token currentToken;
        ... ...
    }
    
    public final class MySQLLexer extends Lexer {
    
        // MySQL词法分析器核心Dictionary的构造方法入参为MySQL所有关键词合集（可以预见各数据库的词法分析器都包含其所有SQL关键词信息），MySQL所有关键词集合包括MySQLKeyword和DefaultKeyword；其他数据库类似，例如Oracle所有关键词集合包括OracleKeyword和DefaultKeyword
        private static Dictionary dictionary = new Dictionary(MySQLKeyword.values());
    
        public MySQLLexer(final String input) {
            super(input, dictionary);
        }
        ... ...
    

### 2\. 获取第一个token

对应的源码是`lexerEngine.nextToken();`，核心实现源码如下：

    
    
    public final void nextToken() {
        skipIgnoredToken();
        if (isVariableBegin()) {
            currentToken = new Tokenizer(input, dictionary, offset).scanVariable();
        } else if (isNCharBegin()) {
            currentToken = new Tokenizer(input, dictionary, ++offset).scanChars();
        } else if (isIdentifierBegin()) {
            currentToken = new Tokenizer(input, dictionary, offset).scanIdentifier();
        } else if (isHexDecimalBegin()) {
            currentToken = new Tokenizer(input, dictionary, offset).scanHexDecimal();
        } else if (isNumberBegin()) {
            currentToken = new Tokenizer(input, dictionary, offset).scanNumber();
        } else if (isSymbolBegin()) {
            currentToken = new Tokenizer(input, dictionary, offset).scanSymbol();
        } else if (isCharsBegin()) {
            currentToken = new Tokenizer(input, dictionary, offset).scanChars();
        } else if (isEnd()) {
            currentToken = new Token(Assist.END, "", offset);
        } else {
            currentToken = new Token(Assist.ERROR, "", offset);
        }
        offset = currentToken.getEndPosition();
    }
    
    // 跳过忽略的token
    private void skipIgnoredToken() {
        offset = new Tokenizer(input, dictionary, offset).skipWhitespace();
        while (isHintBegin()) {
            offset = new Tokenizer(input, dictionary, offset).skipHint();
            offset = new Tokenizer(input, dictionary, offset).skipWhitespace();
        }
        while (isCommentBegin()) {
            offset = new Tokenizer(input, dictionary, offset).skipComment();
            offset = new Tokenizer(input, dictionary, offset).skipWhitespace();
        }
    }
    

由这段代码可知，忽略的token主要包括：

  1. 空格，如下图所示：

![201805271002](http://cmsblogs.qiniudn.com/201805271002.png)

  1. hint与后面的空格，例如MySQL的hint语法为`/*! hint info */`，`"SELECT /*!40001 SQL_CACHE */ o.* FROM t_order o"`这条SQL有hint`/*!40001 SQL_CACHE */`；（Oracle的hint语法有所不同，通过OracleLexer.java中的isHintBegin()可知，Oracle的hint语法为`/*+ hint info */`）；
  2. 注释与后面的空格，，参考sharding-jdbc源码可知注释语法有3种：`//`，`--`，`/*`，这三种注释的处理有所不同，`//`和`--`被认为是单行注释（isSingleLineCommentBegin()），sharding-jdbc会直接通过当前一整行；而`/*`被认为是多行注释（isMultipleLineCommentBegin()），sharding-jdbc会直接掉到`*/`后面，例如MySQL的注释语法为`" /*parse explain*/SELECT o.* FROM t_order o"`这条SQL有注释`/*parse explain*/`；

判断是否为注释的源码如下：

    
    
    protected boolean isCommentBegin() {
        char current = getCurrentChar(0);
        char next = getCurrentChar(1);
        return "/" == current && "/" == next || "-" == current && "-" == next || "/" == current && "*" == next;
    }
    

##### nextToken()分析

由于接下来的SQL解析都会调用这个nextToken()方法，所以为了更好的分析SQL解析过程，接下来详细剖析它的逻辑，由其源码可知，其逻辑主要分为两个部分：

  1. 调用skipIgnoredToken()跳过忽略的token（上面已经分析了哪些属于忽略的token）
  2. 调用`is***Begin()`方法判断类型然后构造Token；`is***Begin()`主要有下面提到的这些： 
    * **isVariableBegin()** –是否变量开头，即@，例如这种SQL： **select @a from dual** （连续两个@符号即@@也是可以的），其中a是一个定义的变量； **select @a from dual** 这条SQL解析到@的时候，得到的token为 **{[type:Literals.VARIABLE](https://link.jianshu.com?t=type%3ALiterals.VARIABLE), literals:@a, endPostion:9}** （这个token的endPostion就是@a后面的位置）
    * **isNCharBegin()** –SQLServer的特殊语法，其他数据库都不支持。例如INSERT INTO employees  
VALUES(N’29730′, N’Philippe’, N’Horsford’, 20, 1)，申明字符串为nvarchar类型；

    * **isIdentifierBegin()** — 是否标识符开头，即a z，AZ，`，_，$；例如这种SQL：**select user_id from t_user limit 1**，解析select的时候，得到的token为**{type:DefaultKeyword.SELECT, literals:SELECT, endPostion:6}**；或者这种SQL：**select`user_id`from t_user limit 1**，解析`user_id`的时候，得到的token为**{type:Literals.IDENTIFIER, literals:`user_id`, endPostion:16}**；
    * **isHexDecimalBegin()** — 是否16进程符号开头，即0x。例如这种SQL： **select 0x21 from dual** ，解析0x21的时候，得到的token为 **{type:Literals.HEX, literals:0x21, endPostion:11}**
    * **isNumberBegin()** — 是否数字开头，即0~9，例如这种SQL： **select ‘afei’ from t_user limit 1** ，limit 1这个1就是数字，解析到limit后面的1的时候，得到的token为 **{type:Literals.INT, literals:1, endPostion:33}**
    * **isSymbolBegin()** — 是否特殊符号开头，例如这种SQL： **select`user_id` from t_user limit ?** ，，解析？的时候，得到的token为 **{type:Symbol.QUESTION, literals:?, endPostion:36}**
    * **isCharsBegin()** — 是否字符开头，即单引号或者双引号，例如这种SQL： **select ‘afei’ from t_user limit 1** ，解析 `afei`的时候，得到的token为 **{type:Literals.CHARS, literals:afei, endPostion:13}**
    * **isEnd()** — 是否SQL尾部，判断条件是 **offset >= input.length()**，即遍历位置offset是否到了sql（input就是sql）尾部。得到的token为 **{type:Assist.END, literals:””, endPostion:31}**

> nextToken()的解析非常重要，其调用贯穿在整个sharding-jdbc的SQL解析过程中；根据这段分析逻辑就能得出文章前面词法分析结果表格了。

###  3\. 得到SQL解析器

对应的源码是`SQLParserFactory.newInstance(dbType,
lexerEngine.getCurrentToken().getType(), shardingRule, lexerEngine)`，
**lexerEngine.getCurrentToken().getType()** 就是上面解析得到的第一个token的类型，核心实现源码如下：

    
    
    @NoArgsConstructor(access = AccessLevel.PRIVATE)
    public final class SQLParserFactory {
    
        public static SQLParser newInstance(final DatabaseType dbType, final TokenType tokenType, final ShardingRule shardingRule, final LexerEngine lexerEngine) {
            // 第一个token类型一定是默认关键词，否则抛出异常。构造这种异常很简单，只需要定义的SQL以MySQLKeyword中的关键词开头即可，例如"show create table t_order o"
            if (!(tokenType instanceof DefaultKeyword)) {
                throw new SQLParsingUnsupportedException(tokenType);
            }
            // 根据第一个token类型得到具体解析器，且第一个token一定是：select，insert，update，delete，create，alter，drop，truncate中的一个，否则会抛出SQLParsingUnsupportedException异常。构造这种异常很简单，只需要定义的sql以DefaultKeyword中的关键词开头，且不是下面枚举的关键词即可，例如"DATABASE SELECT o.* FROM t_order o"
            switch ((DefaultKeyword) tokenType)  {
                // 从这里可知，为什么前面要调用lexerEngine.nextToken()获取第一个token，SQLParserFactory根据这个token才能确实哪种类型的SQL解析器
                case SELECT:
                    return SelectParserFactory.newInstance(dbType, shardingRule, lexerEngine);
                case INSERT:
                    return InsertParserFactory.newInstance(dbType, shardingRule, lexerEngine);
                case UPDATE:
                    return UpdateParserFactory.newInstance(dbType, shardingRule, lexerEngine);
                case DELETE:
                    return DeleteParserFactory.newInstance(dbType, shardingRule, lexerEngine);
                case CREATE:
                    return CreateParserFactory.newInstance(dbType, shardingRule, lexerEngine);
                case ALTER:
                    return AlterParserFactory.newInstance(dbType, shardingRule, lexerEngine);
                case DROP:
                    return DropParserFactory.newInstance(dbType, shardingRule, lexerEngine);
                case TRUNCATE:
                    return TruncateParserFactory.newInstance(dbType, shardingRule, lexerEngine);
                default:
                    throw new SQLParsingUnsupportedException(lexerEngine.getCurrentToken().getType());
            }
        }
    }
    

从上面的代码可知，得到的SQL解析器的一些主要属性有：

  1. 数据库类型dbType；
  2. 分库分表规则shardingRule；
  3. 词法分析器引擎lexerEngine；

> lexerEngine的属性为Lexer
lexer，它的一些核心属性在上面有分析过：SQL语句input，包含SQL关键词的字典dictionary，SQL解析位置偏移量offset，当前解析得到的词令currentToken；

### 4\. SQL解析

这篇文章分析了sharding-
jdbc中SQL解析的准备工作，下一篇文章将详细分析insert（增），delete（删），update（改），select（查），等SQL语句的解析过程；

