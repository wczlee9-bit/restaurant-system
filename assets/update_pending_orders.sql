-- 更新已存在的 pending 状态订单和订单项
-- 1. 将所有 pending 状态的订单项更新为 preparing
-- 2. 将所有 pending 状态的订单更新为 preparing

-- 更新订单项状态
UPDATE order_items
SET status = 'preparing'
WHERE status = 'pending';

-- 更新订单状态
UPDATE orders
SET order_status = 'preparing'
WHERE order_status = 'pending';

-- 检查更新结果
SELECT
    '订单状态分布' as 类型,
    order_status as 状态,
    COUNT(*) as 数量
FROM orders
GROUP BY order_status
UNION ALL
SELECT
    '订单项状态分布' as 类型,
    status as 状态,
    COUNT(*) as 数量
FROM order_items
GROUP BY status;
