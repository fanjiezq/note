# sql语句关键字执行顺序
sql语句

    SELECT DISTINCT
    < select_list >
    FROM
        < left_table > < join_type >
    JOIN < right_table > ON < join_condition >
    WHERE
        < where_condition >
    GROUP BY
        < group_by_list >
    HAVING
        < having_condition >
    ORDER BY
        < order_by_condition >
    LIMIT < limit_number >

执行顺序

    FROM <left_table>
    ON <join_condition>
    <join_type> JOIN <right_table>
    WHERE <where_condition>
    GROUP BY <group_by_list>
    HAVING <having_condition>
    SELECT 
    DISTINCT <select_list>
    ORDER BY <order_by_condition>
    LIMIT <limit_number>