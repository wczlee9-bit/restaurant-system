-- 初始化会员等级数据
INSERT INTO member_level_rules (id, name, min_points, discount, description, created_at)
VALUES
    (1, '普通会员', 0, 1.00, '新注册会员，享受全价优惠', NOW()),
    (2, '银卡会员', 1000, 0.95, '积分达到1000，享受95折优惠', NOW()),
    (3, '金卡会员', 5000, 0.90, '积分达到5000，享受90折优惠', NOW()),
    (4, '白金会员', 10000, 0.85, '积分达到10000，享受85折优惠', NOW()),
    (5, '钻石会员', 20000, 0.80, '积分达到20000，享受80折优惠', NOW())
ON CONFLICT (id) DO NOTHING;
