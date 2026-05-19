# Real Replay Mining v1 Review Pack

## 使用说明

本审核包不是让你为单个样本补关键词，而是做 cluster-level / category-level 决策。

重点判断每条样本属于哪类：

- `low_info_context_needed`：当前轮信息不足，需要上下文，不应直接扩 SOP
- `taxonomy_gap`：标签体系不对齐，expected_scene 比当前系统更细
- `merchant_fact_gap`：需要店铺/商品/活动/库存/快递配置事实
- `platform_sop_gap`：确实缺平台 SOP
- `retrieval_gap`：SOP 有但检索没召回
- `label_noise`：expected_scene 或样本本身不可靠
- `dpo_keep`：可以进入 DPO
- `dpo_drop`：不能进入 DPO


# no_hit_or_weak

- source: `data/eval/real_replay_mining_v1/no_hit_or_weak_query_sample.jsonl`
- shown_rows: 80

## expected_scene distribution in shown rows

| scene | count |
|---|---:|
| product_qa_policy | 20 |
| promotion_policy | 16 |
| unknown | 7 |
| quality_issue | 7 |
| price_protection | 5 |
| description_mismatch | 4 |
| stock_policy | 4 |
| express_policy | 4 |
| shipping_policy | 3 |
| coupon_policy | 3 |
| refund_policy | 2 |
| gift_policy | 2 |
| invoice_policy | 1 |
| logistics_policy | 1 |
| order_modify_policy | 1 |

## hit_status distribution in shown rows

| hit_status | count |
|---|---:|
| weak_query | 41 |
| no_hit | 39 |

## review table

| idx | retrieval_query | expected_scene | hit_status | top1_scene | top1_score | top_cards | suggested_bucket | note |
|---:|---|---|---|---|---:|---|---|---|
| 1 | 54476844278044265219693有啥区别 | unknown | weak_query | logistics_policy | 7.0 | tmall_logistics_timeliness_rule_0009/logistics_policy/7.0<br>tmall_7day_return_rule_0005/return_exchange/5.0 |  |  |
| 2 | 是纯棉的吗百分百棉麻；会不会添加了荧光增白剂 | product_qa_policy | no_hit |  | 0 |  |  |  |
| 3 | 是纯棉的吗百分百棉麻；会不会添加了荧光增白剂 | product_qa_policy | no_hit |  | 0 |  |  |  |
| 4 | 实在是俩娃家里消耗大；那亲亲静候佳音哦谢谢 | unknown | no_hit |  | 0 |  |  |  |
| 5 | 我经营藏茶茶刀必不可少；你店里有茶勺吗 | description_mismatch | no_hit |  | 0 |  |  |  |
| 6 | 不好吃吃了六颗三颗苦；关键一半就是苦的 | quality_issue | no_hit |  | 0 |  |  |  |
| 7 | 不好吃吃了六颗三颗苦；关键一半就是苦的 | quality_issue | no_hit |  | 0 |  |  |  |
| 8 | 26号之前哦；差不多吧寄过来路上三天 | stock_policy | no_hit |  | 0 |  |  |  |
| 9 | 26号之前哦；差不多吧寄过来路上三天 | stock_policy | no_hit |  | 0 |  |  |  |
| 10 | 距离并不远；哦哦改好啦我都被气糊涂了 | refund_policy | no_hit |  | 0 |  |  |  |
| 11 | 浙江衢州；涨价了之前刚到你那买了5箱 | price_protection | no_hit |  | 0 |  |  |  |
| 12 | 浙江衢州；涨价了之前刚到你那买了5箱 | price_protection | no_hit |  | 0 |  |  |  |
| 13 | 我看图片上有；我先买吧好用我再来多买 | promotion_policy | no_hit |  | 0 |  |  |  |
| 14 | 180块钱行不行十盒；哈哈哈都差不多 | promotion_policy | no_hit |  | 0 |  |  |  |
| 15 | 有开收据吗；福建艺术职业学院白茶馆 | invoice_policy | no_hit |  | 0 |  |  |  |
| 16 | 撬普洱哪个合适；中意那个大马士茶刀 | quality_issue | no_hit |  | 0 |  |  |  |
| 17 | 撬普洱哪个合适；中意那个大马士茶刀 | quality_issue | no_hit |  | 0 |  |  |  |
| 18 | 这两种有区别吗；图片这种是干的对吧 | product_qa_policy | no_hit |  | 0 |  |  |  |
| 19 | 547665361968；好的谢谢 | unknown | no_hit |  | 0 |  |  |  |
| 20 | 528105689823；好的谢谢 | product_qa_policy | no_hit |  | 0 |  |  |  |
| 21 | 536023110028；好的谢谢 | product_qa_policy | no_hit |  | 0 |  |  |  |
| 22 | 550995848415；好的谢谢 | promotion_policy | no_hit |  | 0 |  |  |  |
| 23 | 550995848415；好的谢谢 | promotion_policy | no_hit |  | 0 |  |  |  |
| 24 | 不好我可要退的哦；杭州桐庐几天到 | promotion_policy | no_hit |  | 0 |  |  |  |
| 25 | 不好我可要退的哦；杭州桐庐几天到 | shipping_policy | no_hit |  | 0 |  |  |  |
| 26 | 你这儿有葡萄干没；我讨厌有啥别的 | shipping_policy | no_hit |  | 0 |  |  |  |
| 27 | 还行吧；亲皮也不薄呀开壳也挺费劲 | quality_issue | no_hit |  | 0 |  |  |  |
| 28 | 还行吧；亲皮也不薄呀开壳也挺费劲 | express_policy | no_hit |  | 0 |  |  |  |
| 29 | 你这儿有葡萄干没；我讨厌有啥别的 | description_mismatch | no_hit |  | 0 |  |  |  |
| 30 | 我特么差点炸了；恩退了再买没钱了 | logistics_policy | no_hit |  | 0 |  |  |  |
| 31 | 能拍吗；552710489362 | coupon_policy | weak_query | logistics_policy | 9.0 | tmall_after_sale_service_rule_0005/logistics_policy/9.0<br>tmall_not_fresh_return_rule_0010/quality_issue/9.0<br>tmall_not_fresh_return_rule_0011/quality_issue/9.0 |  |  |
| 32 | 能拍吗；552710489362 | coupon_policy | weak_query | logistics_policy | 9.0 | tmall_after_sale_service_rule_0005/logistics_policy/9.0<br>tmall_not_fresh_return_rule_0010/quality_issue/9.0<br>tmall_not_fresh_return_rule_0011/quality_issue/9.0 |  |  |
| 33 | 528690173109；嗯对的 | product_qa_policy | weak_query | shipping_policy | 5.0 | tmall_logistics_timeliness_rule_0005/shipping_policy/5.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/5.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/5.0 |  |  |
| 34 | 好谢谢；528941799061 | order_modify_policy | weak_query | return_exchange | 7.0 | tmall_return_shipping_protection_rule_0006/return_exchange/7.0 |  |  |
| 35 | 528105689823；荧光剂 | product_qa_policy | weak_query | return_exchange | 5.0 | tmall_7day_return_rule_0005/return_exchange/5.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/5.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/5.0 |  |  |
| 36 | 538405926243；便宜些 | promotion_policy | weak_query | quality_issue | 5.0 | tmall_after_sale_service_rule_0007/quality_issue/5.0<br>tmall_after_sale_service_rule_0009/return_exchange/5.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/5.0 |  |  |
| 37 | 涨价了；528105689823 | price_protection | weak_query | return_exchange | 5.0 | tmall_7day_return_rule_0005/return_exchange/5.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/5.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/5.0 |  |  |
| 38 | 527658979000；这款呢 | product_qa_policy | weak_query | logistics_policy | 8.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/8.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/5.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/5.0 |  |  |
| 39 | 527658979000；这款呢 | product_qa_policy | weak_query | logistics_policy | 8.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/8.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/5.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/5.0 |  |  |
| 40 | 521754572637；你看下 | product_qa_policy | weak_query | logistics_policy | 5.0 | tmall_after_sale_service_rule_0003/logistics_policy/5.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/5.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/5.0 |  |  |
| 41 | 521754572637；你看下 | product_qa_policy | weak_query | logistics_policy | 5.0 | tmall_after_sale_service_rule_0003/logistics_policy/5.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/5.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/5.0 |  |  |
| 42 | 543526374545；四组呀 | refund_policy | weak_query | quality_issue | 5.0 | tmall_not_fresh_return_rule_0007/quality_issue/5.0 |  |  |
| 43 | 555185256661；就这款 | promotion_policy | weak_query | logistics_policy | 5.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/5.0<br>tmall_not_fresh_return_rule_0007/quality_issue/5.0 |  |  |
| 44 | 538832022583；嗯嗯好 | promotion_policy | weak_query | return_exchange | 10.0 | tmall_return_shipping_protection_rule_0004/return_exchange/10.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/7.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/5.0 |  |  |
| 45 | 孩子特别喜欢吃你家里的榴莲干呢 | express_policy | no_hit |  | 0 |  |  |  |
| 46 | 你这儿有葡萄干没；好吧奇异果呢 | description_mismatch | no_hit |  | 0 |  |  |  |
| 47 | 你这儿有葡萄干没；好吧奇异果呢 | description_mismatch | no_hit |  | 0 |  |  |  |
| 48 | 买二送一那买四送二嘛；送几份呢 | promotion_policy | no_hit |  | 0 |  |  |  |
| 49 | 547369195439这种呢 | express_policy | weak_query | logistics_policy | 5.0 | tmall_after_sale_service_rule_0003/logistics_policy/5.0 |  |  |
| 50 | 您好；552710489362 | coupon_policy | weak_query |  | 0 |  |  |  |
| 51 | 528690173109；在不 | unknown | weak_query |  | 0 |  |  |  |
| 52 | 528941799061；好的 | promotion_policy | weak_query |  | 0 |  |  |  |
| 53 | 528941799061；好的 | promotion_policy | weak_query |  | 0 |  |  |  |
| 54 | 528941799061；中国 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 55 | 528941799061；中国 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 56 | 你好；528690173109 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 57 | 你好；528690173109 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 58 | 528105689823；好的 | gift_policy | weak_query |  | 0 |  |  |  |
| 59 | 528105689823；好的 | unknown | weak_query |  | 0 |  |  |  |
| 60 | 528105689823；好的 | shipping_policy | weak_query |  | 0 |  |  |  |
| 61 | 546838661718；好的 | promotion_policy | weak_query |  | 0 |  |  |  |
| 62 | 543826442006；好吧 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 63 | 538872953711；上海 | promotion_policy | weak_query |  | 0 |  |  |  |
| 64 | 547279128207；哦哦 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 65 | 549182321874；哦哦 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 66 | 521521942026；好的 | stock_policy | weak_query |  | 0 |  |  |  |
| 67 | 521521942026；好的 | stock_policy | weak_query |  | 0 |  |  |  |
| 68 | 543526374545；没事 | promotion_policy | weak_query |  | 0 |  |  |  |
| 69 | 545468795743；哦哦 | promotion_policy | weak_query |  | 0 |  |  |  |
| 70 | 538872953711；谢谢 | unknown | weak_query |  | 0 |  |  |  |
| 71 | 538872953711；谢谢 | price_protection | weak_query |  | 0 |  |  |  |
| 72 | 538872953711；谢谢 | price_protection | weak_query |  | 0 |  |  |  |
| 73 | 536534099634；哦哦 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 74 | 538832022583；好的 | product_qa_policy | weak_query |  | 0 |  |  |  |
| 75 | 請問這茶刀和養壺筆是小號的嗎 | express_policy | no_hit |  | 0 |  |  |  |
| 76 | 看评论说比较差；这批有带盖吗 | quality_issue | no_hit |  | 0 |  |  |  |
| 77 | 看评论说比较差；这批有带盖吗 | quality_issue | no_hit |  | 0 |  |  |  |
| 78 | 来晚了；那个公众号是微信号吗 | promotion_policy | no_hit |  | 0 |  |  |  |
| 79 | 送脐带贴；能换别的吗同价位的 | unknown | no_hit |  | 0 |  |  |  |
| 80 | 送脐带贴；能换别的吗同价位的 | gift_policy | no_hit |  | 0 |  |  |  |

# scene_mismatch

- source: `data/eval/real_replay_mining_v1/scene_mismatch_sample.jsonl`
- shown_rows: 80

## expected_scene distribution in shown rows

| scene | count |
|---|---:|
| express_policy | 11 |
| complaint_policy | 9 |
| promotion_policy | 8 |
| refund_policy | 6 |
| stock_policy | 6 |
| logistics_policy | 5 |
| coupon_policy | 5 |
| shipping_fee_policy | 5 |
| description_mismatch | 4 |
| quality_issue | 4 |
| order_modify_policy | 3 |
| shipping_policy | 3 |
| return_exchange | 3 |
| gift_policy | 3 |
| missing_package_policy | 2 |
| bulk_purchase_policy | 2 |
| price_protection | 1 |

## hit_status distribution in shown rows

| hit_status | count |
|---|---:|
| scene_mismatch | 80 |

## review table

| idx | retrieval_query | expected_scene | hit_status | top1_scene | top1_score | top_cards | suggested_bucket | note |
|---:|---|---|---|---|---:|---|---|---|
| 1 | 我今夜一点多刚看到查看物流里面说18袋榴莲干都签收了我根本一袋都没收到没见到一个快递员给过我快递邮件谁给我了就说快件已签收谁签收了我9月9号买了6袋9月11号买了6袋9月12号买了6袋一共18袋到现在 | logistics_policy | scene_mismatch | return_exchange | 73.0 | tmall_return_shipping_protection_rule_0004/return_exchange/73.0<br>tmall_after_sale_service_rule_0005/logistics_policy/64.0<br>tmall_trade_timeliness_rule_0011/logistics_policy/57.0 |  |  |
| 2 | 我今夜一点多刚看到查看物流里面说18袋榴莲干都签收了我根本一袋都没收到没见到一个快递员给过我快递邮件谁给我了就说快件已签收谁签收了我9月9号买了6袋9月11号买了6袋9月12号买了6袋一共18袋到现在 | logistics_policy | scene_mismatch | return_exchange | 73.0 | tmall_return_shipping_protection_rule_0004/return_exchange/73.0<br>tmall_after_sale_service_rule_0005/logistics_policy/64.0<br>tmall_trade_timeliness_rule_0011/logistics_policy/57.0 |  |  |
| 3 | 你要是昨天发货就能到你为什么昨天不发货呢那你到不了你就不要说呀你们上面还写着今天16点付款8号星期日货到能到了吗我是昨天上午9点多付的款应该七号货到我就能收到货呀那你说货到不了怎么办给我退钱呗；你说几 | refund_policy | scene_mismatch | logistics_policy | 101.0 | tmall_trade_timeliness_rule_0011/logistics_policy/101.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/80.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/76.0 |  |  |
| 4 | 521521942026你好发什么快递；“让我们一起清凉一夏”为回馈广大亲们的支持屹茗堂特精选1000罐花茶凡在全场购物满39元即赠花茶一罐赠完为止领取方式亲们挑选自己喜爱的花茶并与所购商品一同拍下联 | promotion_policy | scene_mismatch | express_policy | 79.0 | phase12_express_choice_availability_0001/express_policy/79.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/65.0<br>taobao_breach_promise_carrier_method_0001/express_policy/46.0 |  |  |
| 5 | 我不是找你的你们为什么这么不讲信用我付了款今天都七天了还不送货难道你骗人吗你们的人斤有人吗赶紧回复在不回复我要点退款了；那我在等今天一下午吧我可以收回退款今天我在收不到货明天说什么我都要退款你把我发的 | complaint_policy | scene_mismatch | refund_policy | 69.0 | tmall_trade_timeliness_rule_0022/refund_policy/69.0<br>tmall_trade_timeliness_rule_0011/logistics_policy/42.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/38.0 |  |  |
| 6 | 我不是找你的你们为什么这么不讲信用我付了款今天都七天了还不送货难道你骗人吗你们的人斤有人吗赶紧回复在不回复我要点退款了；那我在等今天一下午吧我可以收回退款今天我在收不到货明天说什么我都要退款你把我发的 | complaint_policy | scene_mismatch | refund_policy | 69.0 | tmall_trade_timeliness_rule_0022/refund_policy/69.0<br>tmall_trade_timeliness_rule_0011/logistics_policy/42.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/38.0 |  |  |
| 7 | 您好遇到问题请详细描述由于用户很多可能会稍后给您解答请亲们见谅；亲您的这个一口价是6元您可以设置满2件减3元不要勾选上不封顶即可那么买家买下2件的价格就是66-3=9元购买3件就是666-3=15元 | promotion_policy | scene_mismatch | quality_issue | 27.0 | tmall_mismatch_compensation_rule_0003/quality_issue/27.0<br>tmall_after_sale_service_rule_0007/quality_issue/23.0<br>tmall_7day_return_rule_0006/return_exchange/21.0 |  |  |
| 8 | 那我退回来吧换一包熟的运费你们负担啊现在我在外地明天回来后就退回给你们到时候运费得返回；半生半熟是质量问题吗没货了退回后把款全额退款真不行只能让淘宝客服解决了我买的炒熟的不是买半生半熟的把地址发过来 | refund_policy | scene_mismatch | shipping_fee_policy | 70.0 | taobao_dispute_shipping_fee_liability_0001/shipping_fee_policy/70.0<br>tmall_after_sale_service_rule_0007/quality_issue/63.0<br>tmall_mismatch_compensation_rule_0003/quality_issue/55.0 |  |  |
| 9 | 那我退回来吧换一包熟的运费你们负担啊现在我在外地明天回来后就退回给你们到时候运费得返回；半生半熟是质量问题吗没货了退回后把款全额退款真不行只能让淘宝客服解决了我买的炒熟的不是买半生半熟的把地址发过来 | refund_policy | scene_mismatch | shipping_fee_policy | 70.0 | taobao_dispute_shipping_fee_liability_0001/shipping_fee_policy/70.0<br>tmall_after_sale_service_rule_0007/quality_issue/63.0<br>tmall_mismatch_compensation_rule_0003/quality_issue/55.0 |  |  |
| 10 | 那是什么意思算了没多少钱的事我就是不喜欢你们这种解决方式的态度；现在是包装破损怎么解决一下快递也认可包装是有破损的嘛当然了照片你没看吗都压成这个样子了鸭蛋也碎了粽子一袋也给压扁了东西是没少 | missing_package_policy | scene_mismatch | quality_issue | 105.0 | tmall_mismatch_compensation_rule_0003/quality_issue/105.0<br>tmall_return_shipping_protection_rule_0004/return_exchange/86.0<br>tmall_not_fresh_return_rule_0007/quality_issue/36.0 |  |  |
| 11 | 是啊我知道一份三袋啊我又没说什么问的是3包就是每包236元是不是可加入购物车要五包才是236元每包啊你们图片不是说三包就是236元每包吗怎么加入购物车就不是呢既然不是图片上的又是什么意思 | description_mismatch | scene_mismatch | quality_issue | 84.0 | tmall_mismatch_compensation_rule_0003/quality_issue/84.0<br>tmall_return_shipping_protection_rule_0004/return_exchange/84.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/30.0 |  |  |
| 12 | 我买你家防溢乳垫怎么会漏吸水珠刚才小宝宝喝奶的时候我才发现乳房旁一圈都是我才垫两小时太恐怖了我都不知道孩子有没有吃到肚子里去溢乳垫都只湿一点；就算是两小时换一回但你这个乳垫会漏吸水珠啊 | quality_issue | scene_mismatch | description_mismatch | 36.0 | tmall_mismatch_compensation_rule_0006/description_mismatch/36.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/34.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/32.0 |  |  |
| 13 | 稍等；亲海报全屏效果宽度是1920高度是无限制的1920宽度是在各个显示器都显示全屏效果的所以您海报内容是要集中做在中间950990部分因为不同的显示器是会显示不一样的效果的 | order_modify_policy | scene_mismatch | logistics_policy | 34.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/34.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/26.0<br>tmall_trade_timeliness_rule_0022/refund_policy/26.0 |  |  |
| 14 | 稍等；亲海报全屏效果宽度是1920高度是无限制的1920宽度是在各个显示器都显示全屏效果的所以您海报内容是要集中做在中间950990部分因为不同的显示器是会显示不一样的效果的 | order_modify_policy | scene_mismatch | logistics_policy | 34.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/34.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/26.0<br>tmall_trade_timeliness_rule_0022/refund_policy/26.0 |  |  |
| 15 | 核桃什么时候到我同时拍的一个发了一个还没发好奇怪发的那个快递信息也中断了问了也没答复我等着送人的还不到我就不要了；嗯希望这次不是石沉大海前几次也都说帮我查最终连回音都没有 | express_policy | scene_mismatch | return_exchange | 57.0 | tmall_return_shipping_protection_rule_0004/return_exchange/57.0<br>taobao_invoice_apply_timing_0001/invoice_policy/53.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/34.0 |  |  |
| 16 | 核桃什么时候到我同时拍的一个发了一个还没发好奇怪发的那个快递信息也中断了问了也没答复我等着送人的还不到我就不要了；嗯希望这次不是石沉大海前几次也都说帮我查最终连回音都没有 | express_policy | scene_mismatch | return_exchange | 57.0 | tmall_return_shipping_protection_rule_0004/return_exchange/57.0<br>taobao_invoice_apply_timing_0001/invoice_policy/53.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/34.0 |  |  |
| 17 | 货在你们自己手上发货是你们自己发；你上面讲的话完全是忽悠我的我都没有跟你讲多少因为是第4天晚上了你还这么忽悠我太气人了一般的在网上我不喜欢说人的你自己也好好想想这事 | express_policy | scene_mismatch | logistics_policy | 21.0 | tmall_logistics_timeliness_rule_0009/logistics_policy/21.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/20.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/18.0 |  |  |
| 18 | 我发你的图看到了吗这是你们的图我的明显是红木其他的都对颜色也一样；我刚好一套黑檀的叫你们补发我又退的话你们太亏要不我买多一支茶针你们在补发我一个大号黑檀茶笔可以不 | bulk_purchase_policy | scene_mismatch | refund_policy | 23.0 | tmall_trade_timeliness_rule_0022/refund_policy/23.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/19.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/15.0 |  |  |
| 19 | 我发你的图看到了吗这是你们的图我的明显是红木其他的都对颜色也一样；我刚好一套黑檀的叫你们补发我又退的话你们太亏要不我买多一支茶针你们在补发我一个大号黑檀茶笔可以不 | bulk_purchase_policy | scene_mismatch | refund_policy | 23.0 | tmall_trade_timeliness_rule_0022/refund_policy/23.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/19.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/15.0 |  |  |
| 20 | 3元你打发要饭的吧算了我就直接给你们个差评了就这种服务态度我花了20就买这个你就退我3元；10吧我也不多说什么了可以就可以不可以就算了至少让我不要损失那么多嘛 | complaint_policy | scene_mismatch | refund_policy | 29.0 | tmall_trade_timeliness_rule_0022/refund_policy/29.0<br>phase12_order_modify_address_0001/order_modify_policy/27.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/24.0 |  |  |
| 21 | 就算再怎么生意忙我付款到今天第六天了你们自己写着3-5天；算了退货好了你们每天都说明天发走没有一天发的你们的话已经不能相信了我这边么等得急死天天催你们都没用 | shipping_policy | scene_mismatch | return_exchange | 36.0 | tmall_return_shipping_protection_rule_0004/return_exchange/36.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/27.0<br>tmall_after_sale_service_rule_0007/quality_issue/25.0 |  |  |
| 22 | 就算再怎么生意忙我付款到今天第六天了你们自己写着3-5天；算了退货好了你们每天都说明天发走没有一天发的你们的话已经不能相信了我这边么等得急死天天催你们都没用 | shipping_policy | scene_mismatch | return_exchange | 36.0 | tmall_return_shipping_protection_rule_0004/return_exchange/36.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/27.0<br>tmall_after_sale_service_rule_0007/quality_issue/25.0 |  |  |
| 23 | 发过霉一样；牌子是怎么做起来卖这些烂核桃能长久吗早扔了我拉了3次我两个明友吃了多也拉了吃几个没事吃了10几个等半时就拉我也不会为这点钱黑你希望你们检查质量 | coupon_policy | scene_mismatch | logistics_policy | 17.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/17.0<br>tmall_not_fresh_return_rule_0007/quality_issue/17.0<br>tmall_after_sale_service_rule_0007/quality_issue/15.0 |  |  |
| 24 | 发过霉一样；牌子是怎么做起来卖这些烂核桃能长久吗早扔了我拉了3次我两个明友吃了多也拉了吃几个没事吃了10几个等半时就拉我也不会为这点钱黑你希望你们检查质量 | coupon_policy | scene_mismatch | logistics_policy | 17.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/17.0<br>tmall_not_fresh_return_rule_0007/quality_issue/17.0<br>tmall_after_sale_service_rule_0007/quality_issue/15.0 |  |  |
| 25 | 不是硬就是粉粉的榴莲味很淡根本不像榴莲干真的生气没碰到过；你怎么这么说话我一直喜欢吃榴莲干你们这难吃实在没法下咽仍了这能浪费钱了但你们不虚心我还是要差评的 | complaint_policy | scene_mismatch | service_recovery | 30.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/30.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/27.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/21.0 |  |  |
| 26 | 您好亲在的哦卖多多科技为您服务请具体说明您的问题；不是亲限购是在宝贝页面显示限购数量无论是电脑端还是手机端提交订单之后在下单页面都是可以任意添加件数的哦 | complaint_policy | scene_mismatch | refund_policy | 42.0 | tmall_trade_timeliness_rule_0022/refund_policy/42.0<br>tmall_mismatch_compensation_rule_0008/quality_issue/35.0<br>tmall_mismatch_compensation_rule_0006/description_mismatch/34.0 |  |  |
| 27 | 您好亲在的哦卖多多科技为您服务请具体说明您的问题；不是亲限购是在宝贝页面显示限购数量无论是电脑端还是手机端提交订单之后在下单页面都是可以任意添加件数的哦 | complaint_policy | scene_mismatch | refund_policy | 42.0 | tmall_trade_timeliness_rule_0022/refund_policy/42.0<br>tmall_mismatch_compensation_rule_0008/quality_issue/35.0<br>tmall_mismatch_compensation_rule_0006/description_mismatch/34.0 |  |  |
| 28 | 剛查到是假簽收淘寶海外倉查不到說他們未收到；說麻煩連續賣家問快遞公司提供簽收面單的圖片進行核實處理說麻煩聯繫賣家問快遞公司提供簽收面單的圖片進行核實處理 | order_modify_policy | scene_mismatch | logistics_policy | 43.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/43.0<br>tmall_after_sale_service_rule_0003/logistics_policy/24.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/22.0 |  |  |
| 29 | 13422170743768063我这一单东西给我运到哪去了昨天应该到的今天还没到这会儿看见预估说要7号才能到前次买不是很正常吗第二天就到了什么情况 | express_policy | scene_mismatch | return_exchange | 38.0 | tmall_return_shipping_protection_rule_0004/return_exchange/38.0<br>phase12_refund_not_received_0001/refund_policy/27.0<br>tmall_after_sale_service_rule_0010/logistics_policy/26.0 |  |  |
| 30 | 反正证据我是留下来了我会找客服投诉你们向你们这样还想我下次再来被坑一次就够了还想二次要不你地址给我我把蜜枣粽退你是不是你们自己搞错了你们自己拿回去拆 | return_exchange | scene_mismatch | logistics_policy | 32.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/32.0<br>taobao_delivery_false_shipment_0001/logistics_policy/30.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/28.0 |  |  |
| 31 | 反正证据我是留下来了我会找客服投诉你们向你们这样还想我下次再来被坑一次就够了还想二次要不你地址给我我把蜜枣粽退你是不是你们自己搞错了你们自己拿回去拆 | return_exchange | scene_mismatch | logistics_policy | 32.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/32.0<br>taobao_delivery_false_shipment_0001/logistics_policy/30.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/28.0 |  |  |
| 32 | 疑不对呀怎么是299547665361968不是229亲前两份买的是229后面8份买就299什么情况呀不是10份内都是229的吗；好的那我退款从新买 | refund_policy | scene_mismatch | logistics_policy | 27.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/27.0<br>tmall_not_fresh_return_rule_0003/quality_issue/25.0<br>tmall_not_fresh_return_rule_0007/quality_issue/25.0 |  |  |
| 33 | 疑不对呀怎么是299547665361968不是229亲前两份买的是229后面8份买就299什么情况呀不是10份内都是229的吗；好的那我退款从新买 | refund_policy | scene_mismatch | logistics_policy | 27.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/27.0<br>tmall_not_fresh_return_rule_0003/quality_issue/25.0<br>tmall_not_fresh_return_rule_0007/quality_issue/25.0 |  |  |
| 34 | 10元这一折腾你们得倒霉20元运费哎发货的质量太重要了那我选择换货还是退货；这样你们也省点我也别那么麻烦不知道这个裂纹会不会变大如果裂开就废了 | return_exchange | scene_mismatch | quality_issue | 26.0 | tmall_not_fresh_return_rule_0003/quality_issue/26.0<br>taobao_dispute_shipping_fee_liability_0001/shipping_fee_policy/25.0<br>taobao_dispute_return_address_issue_0001/return_exchange/24.0 |  |  |
| 35 | 电话多少邮政电话我这里看不到我在等送人去的晕回话急回话你说昨天电话打通的电话给我什么意思在等货大姐7号今天11号；晚点用会忘了现在的事马上安排 | express_policy | scene_mismatch | quality_issue | 57.0 | tmall_mismatch_compensation_rule_0003/quality_issue/57.0<br>tmall_return_shipping_protection_rule_0004/return_exchange/51.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/17.0 |  |  |
| 36 | 吃完哭还有就是像库存很久一样全是涩味就像油炸东西放很久一样；我婆婆昨天吃了好几个今天我自己吃了4个给朋友吃了10多个小孩吃了几个具体多少不知道 | refund_policy | scene_mismatch | quality_issue | 19.0 | tmall_not_fresh_return_rule_0007/quality_issue/19.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/17.0<br>taobao_dispute_shortage_combined_package_0001/logistics_policy/15.0 |  |  |
| 37 | 这次买的怎么都是这样的坏的还有虫子怎么跟上次不一样；是都是这样对啊我买来送人的别人打开都是这样的无语了我是看上次买的不错又在买了没想到是这样 | quality_issue | scene_mismatch | logistics_policy | 57.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/57.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/30.0<br>tmall_trade_timeliness_rule_0022/refund_policy/30.0 |  |  |
| 38 | 这次买的怎么都是这样的坏的还有虫子怎么跟上次不一样；是都是这样对啊我买来送人的别人打开都是这样的无语了我是看上次买的不错又在买了没想到是这样 | quality_issue | scene_mismatch | logistics_policy | 57.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/57.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/30.0<br>tmall_trade_timeliness_rule_0022/refund_policy/30.0 |  |  |
| 39 | 借口；我又不是吃一次我不知道奶油味是什么样孑吗我从不吃原味的别人家都油亮黄色的一句对不起都不说还强词夺理你一个客服吃了多少核桃说的很懂样孑 | coupon_policy | scene_mismatch | quality_issue | 34.0 | tmall_mismatch_compensation_rule_0003/quality_issue/34.0<br>tmall_trade_timeliness_rule_0022/refund_policy/29.0<br>tmall_return_shipping_protection_rule_0004/return_exchange/26.0 |  |  |
| 40 | 就是我之前确认收货后申请退款的刚刚截图也给你们看了退款中这三个字看到了么；快递你看下11号就已经签收了今天几号了那你那边看不到怎么处理呢 | coupon_policy | scene_mismatch | logistics_policy | 140.0 | tmall_after_sale_service_rule_0005/logistics_policy/140.0<br>tmall_after_sale_service_rule_0007/quality_issue/71.0<br>tmall_trade_timeliness_rule_0011/logistics_policy/67.0 |  |  |
| 41 | 你好在吗；之前有一家的发的韵达也是龙武这里没有韵达到哨冲就打电话给我了叫我去哨冲拿我说我地址是龙武然后他说到龙武要加5元我怕这个也会这样 | express_policy | scene_mismatch | gift_policy | 21.0 | phase12_gift_missing_or_promise_unfulfilled_0001/gift_policy/21.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/19.0<br>phase12_order_modify_address_0001/order_modify_policy/17.0 |  |  |
| 42 | 怎么回事啊是不是他们把货搞丢了我后买的三只松鼠都到货了本来一直都买的三只松鼠的榴莲干那天看见你家的了就想换个牌子尝尝结果还尝出来麻烦了 | express_policy | scene_mismatch | logistics_policy | 46.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/46.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/44.0<br>tmall_trade_timeliness_rule_0022/refund_policy/30.0 |  |  |
| 43 | 你们什么态度吗可是人家跟我打电话说丟了没有拉我不是把号码给你了；我只要把钱赶紧退我好了什么态度吗人家已经说丢了的你们自己跟快递去联系把 | express_policy | scene_mismatch | refund_policy | 29.0 | tmall_trade_timeliness_rule_0022/refund_policy/29.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/23.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/23.0 |  |  |
| 44 | 你们什么态度吗可是人家跟我打电话说丟了没有拉我不是把号码给你了；我只要把钱赶紧退我好了什么态度吗人家已经说丢了的你们自己跟快递去联系把 | express_policy | scene_mismatch | refund_policy | 29.0 | tmall_trade_timeliness_rule_0022/refund_policy/29.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/23.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/23.0 |  |  |
| 45 | 你也是够够的前两天就说到货了会发的一直说补发补发现在又没到货；你已经不是第一次和我说这句话了真的是够够的我估计你过几天又要和我说丢件了 | stock_policy | scene_mismatch | logistics_policy | 32.0 | tmall_logistics_timeliness_rule_0009/logistics_policy/32.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/29.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/23.0 |  |  |
| 46 | 你也是够够的前两天就说到货了会发的一直说补发补发现在又没到货；你已经不是第一次和我说这句话了真的是够够的我估计你过几天又要和我说丢件了 | stock_policy | scene_mismatch | logistics_policy | 32.0 | tmall_logistics_timeliness_rule_0009/logistics_policy/32.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/29.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/23.0 |  |  |
| 47 | 这不是江西么我是买到江西啊而且我换地址给别人浙江的也要运费我之前买就不用啊可以改运费吗；对不起我地址错了可以再拍一次么我要寄给浙江的 | promotion_policy | scene_mismatch | order_modify_policy | 69.0 | phase12_order_modify_address_0001/order_modify_policy/69.0<br>tmall_trade_timeliness_rule_0022/refund_policy/27.0<br>tmall_return_shipping_protection_rule_0004/return_exchange/24.0 |  |  |
| 48 | 我是说前面的标题我在你店买的80抽那些标题就有口手标明就这个款没有标明；因为口手湿巾和不是口手湿巾都会标清楚我都是看标题多好小看后面 | gift_policy | scene_mismatch | logistics_policy | 21.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/21.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/15.0<br>tmall_mismatch_compensation_rule_0006/description_mismatch/15.0 |  |  |
| 49 | 你们客服说让我留一包试用这样不委屈了宝宝现在你们又说只给我补发5包钱其实只有那么大回事但是我想知道是个什么情况；不清楚你们可以问的 | description_mismatch | scene_mismatch | refund_policy | 30.0 | phase12_refund_not_received_0001/refund_policy/30.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/19.0<br>tmall_not_fresh_return_rule_0003/quality_issue/19.0 |  |  |
| 50 | 你们客服说让我留一包试用这样不委屈了宝宝现在你们又说只给我补发5包钱其实只有那么大回事但是我想知道是个什么情况；不清楚你们可以问的 | description_mismatch | scene_mismatch | refund_policy | 30.0 | phase12_refund_not_received_0001/refund_policy/30.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/19.0<br>tmall_not_fresh_return_rule_0003/quality_issue/19.0 |  |  |
| 51 | 这是我的问题吗我只关心结果结果是您骗人对吗明天如果还是没有发我会找淘宝投诉和ems投诉的看着着办吧年前你们到底有没有货呀我表示怀疑 | complaint_policy | scene_mismatch | shipping_policy | 36.0 | tmall_logistics_timeliness_rule_0005/shipping_policy/36.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/36.0<br>tmall_after_sale_service_rule_0010/logistics_policy/30.0 |  |  |
| 52 | 这是我的问题吗我只关心结果结果是您骗人对吗明天如果还是没有发我会找淘宝投诉和ems投诉的看着着办吧年前你们到底有没有货呀我表示怀疑 | complaint_policy | scene_mismatch | shipping_policy | 36.0 | tmall_logistics_timeliness_rule_0005/shipping_policy/36.0<br>tmall_return_shipping_protection_rule_0005/return_exchange/36.0<br>tmall_after_sale_service_rule_0010/logistics_policy/30.0 |  |  |
| 53 | 我也看你家写的是婴儿的但是买回来根本就没有写婴儿的字样；我我不是想让你们退干嘛的只是跟你们说希望你们以后注意吧不过我也会如实评价的 | description_mismatch | scene_mismatch | logistics_policy | 21.0 | tmall_logistics_timeliness_rule_0007/logistics_policy/21.0<br>tmall_trade_timeliness_rule_0022/refund_policy/17.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/15.0 |  |  |
| 54 | 我昨天已经申请退款的了今天怎么发货了你们看一下在嘛我在别处买了；可以截拦嘛等等我问下我昨天买的店是否给我发货如果没就你们家买可以嘛 | logistics_policy | scene_mismatch | quality_issue | 63.0 | tmall_not_fresh_return_rule_0011/quality_issue/63.0<br>taobao_after_sale_undelivered_refund_0001/refund_policy/61.0<br>taobao_after_sale_shipped_refund_0001/refund_policy/52.0 |  |  |
| 55 | 那我花这么多钱不是不想要一个有瑕疵的吗那瑕疵品我花10块钱就能买一个；要不你给我换一个要不我就把这退了谁也不想花钱买个瑕疵品不是吗 | logistics_policy | scene_mismatch | service_recovery | 27.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/27.0<br>tmall_trade_timeliness_rule_0022/refund_policy/24.0<br>taobao_after_sale_shipped_refund_0001/refund_policy/24.0 |  |  |
| 56 | 以前没有我们学校有邮政代售点而且以前的话都是有快递员电话我总是会看到谁在派件专门有派件员为我服务；我的订单号快递现在是不是下班了 | express_policy | scene_mismatch | logistics_policy | 45.0 | tmall_logistics_timeliness_rule_0007/logistics_policy/45.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/43.0<br>tmall_trade_timeliness_rule_0022/refund_policy/41.0 |  |  |
| 57 | 复制这条信息打开手机淘宝即可看到SHOPNAME婴儿纯棉柔巾宝宝棉柔巾纸巾干湿巾干湿两用巾100抽12包au71n6kMba | gift_policy | scene_mismatch | quality_issue | 14.0 | tmall_not_fresh_return_rule_0007/quality_issue/14.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/12.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/11.0 |  |  |
| 58 | 是都是这样对啊我买来送人的别人打开都是这样的无语了我是看上次买的不错又在买了没想到是这样；我是送人的别人说打开很多坏的怎么办 | missing_package_policy | scene_mismatch | logistics_policy | 51.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/51.0<br>tmall_not_fresh_return_rule_0003/quality_issue/28.0<br>tmall_after_sale_service_rule_0003/logistics_policy/26.0 |  |  |
| 59 | 也就是粽子他拿到手34天也不发货是这个意思；好你问吧如果明天还没有更新的物流收到东西以后不仅给你们差评我还要投诉你们的店铺 | complaint_policy | scene_mismatch | service_recovery | 81.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/81.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/78.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/59.0 |  |  |
| 60 | 我的货发错地址了可以帮我调解吗；我定了两次单送给两个客户结果发到一个地方了21号那个单发错了21号的要发河南运费我们这边出 | shipping_fee_policy | scene_mismatch | order_modify_policy | 68.0 | phase12_order_modify_address_0001/order_modify_policy/68.0<br>taobao_dispute_return_address_issue_0001/return_exchange/32.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/19.0 |  |  |
| 61 | 我的货发错地址了可以帮我调解吗；我定了两次单送给两个客户结果发到一个地方了21号那个单发错了21号的要发河南运费我们这边出 | logistics_policy | scene_mismatch | order_modify_policy | 68.0 | phase12_order_modify_address_0001/order_modify_policy/68.0<br>taobao_dispute_return_address_issue_0001/return_exchange/32.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/19.0 |  |  |
| 62 | 我根本没有打开就在外面拍的是看你们做生意也不容易才会跟你说这些难道你们的东西就是这样吗不要烦我呢购物是开心的我不是找气的 | promotion_policy | scene_mismatch | logistics_policy | 36.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/36.0<br>phase12_gift_missing_or_promise_unfulfilled_0001/gift_policy/27.0<br>tmall_not_fresh_return_rule_0007/quality_issue/26.0 |  |  |
| 63 | xuxili2008126com许熙丽xuxili2008126com许熙丽xuxili2008126com许熙丽；谢谢 | price_protection | scene_mismatch | logistics_policy | 10.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/10.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/7.0<br>tmall_not_fresh_return_rule_0007/quality_issue/7.0 |  |  |
| 64 | 我两次拍为什么不能改价呢我两袋是寄到宁波6袋寄到湖北寄在一起我还得寄一次；宁波这边两袋我出5元可以吗不行就拍6袋寄湖北 | promotion_policy | scene_mismatch | refund_policy | 84.0 | tmall_trade_timeliness_rule_0022/refund_policy/84.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/40.0<br>tmall_mismatch_compensation_rule_0007/quality_issue/38.0 |  |  |
| 65 | 咨询一下怎么安上去的；我就想要个能卸下来的老虎钳子都用上了针下来了但是铜箍还在上面不敢再弄了怕刚到手就弄坏了挺喜欢的 | quality_issue | scene_mismatch | logistics_policy | 32.0 | tmall_logistics_timeliness_rule_0007/logistics_policy/32.0<br>tmall_after_sale_service_rule_0007/quality_issue/15.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/15.0 |  |  |
| 66 | 卖家怎么一直没有快递信息的我8号买的今天已经12号；我没有问下午还是上午到我只需要你们明天发货还叫我退货怎么做客服的 | stock_policy | scene_mismatch | logistics_policy | 66.0 | tmall_logistics_timeliness_rule_0009/logistics_policy/66.0<br>tmall_7day_return_rule_0010/return_exchange/57.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/54.0 |  |  |
| 67 | 卖家怎么一直没有快递信息的我8号买的今天已经12号；我没有问下午还是上午到我只需要你们明天发货还叫我退货怎么做客服的 | stock_policy | scene_mismatch | logistics_policy | 66.0 | tmall_logistics_timeliness_rule_0009/logistics_policy/66.0<br>tmall_7day_return_rule_0010/return_exchange/57.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/54.0 |  |  |
| 68 | 两个快递同时到的家人没帮我拒签你这边给我补下邮费多的一份我给你寄回去；我在外面怎么联系而且接快递的电话是我家人不是我 | shipping_fee_policy | scene_mismatch | return_exchange | 55.0 | tmall_return_shipping_protection_rule_0005/return_exchange/55.0<br>phase12_refund_not_received_0001/refund_policy/27.0<br>tmall_7day_return_rule_0014/return_exchange/26.0 |  |  |
| 69 | 两个快递同时到的家人没帮我拒签你这边给我补下邮费多的一份我给你寄回去；我在外面怎么联系而且接快递的电话是我家人不是我 | shipping_fee_policy | scene_mismatch | return_exchange | 55.0 | tmall_return_shipping_protection_rule_0005/return_exchange/55.0<br>phase12_refund_not_received_0001/refund_policy/27.0<br>tmall_7day_return_rule_0014/return_exchange/26.0 |  |  |
| 70 | 卖家怎么一直没有快递信息的我8号买的今天已经12号；你们太不负责任了乱填快递单送人去的一直等着没货不跟我说一声的啊 | stock_policy | scene_mismatch | logistics_policy | 52.0 | tmall_logistics_timeliness_rule_0009/logistics_policy/52.0<br>taobao_delivery_false_shipment_0001/logistics_policy/44.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/40.0 |  |  |
| 71 | 我就是看到无添加任何香精才买的买回来一股味道不是骗人吗；那能给我一个解释香味什么情况拿了湿巾的手一个小时还能一股味 | coupon_policy | scene_mismatch | quality_issue | 59.0 | tmall_not_fresh_return_rule_0010/quality_issue/59.0<br>taobao_delivery_delay_0001/shipping_policy/32.0<br>tmall_trade_timeliness_rule_0002/shipping_policy/30.0 |  |  |
| 72 | 买的你的宝贝已经收到唯一的缺陷是木裂太明显了你看咋处理吧；不影响影响外观啊这么漂亮的玩意一条明显的木裂太煞风景了吧 | shipping_policy | scene_mismatch | gift_policy | 24.0 | phase12_gift_missing_or_promise_unfulfilled_0001/gift_policy/24.0<br>tmall_after_sale_service_rule_0005/logistics_policy/21.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/19.0 |  |  |
| 73 | 我就想知道我的快递天天快递拿走了吗还是你们还没发还在你们库里；我是提前那么多天买的意思就是在路上了直接就显示到了吗 | express_policy | scene_mismatch | service_recovery | 39.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/39.0<br>taobao_breach_promise_carrier_method_0001/express_policy/26.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/24.0 |  |  |
| 74 | 20065110070079683帮忙看下订单怎么付不了款呢；21622588981079683帮忙改下价格呗谢谢 | promotion_policy | scene_mismatch | logistics_policy | 25.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/25.0<br>tmall_not_fresh_return_rule_0007/quality_issue/20.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/19.0 |  |  |
| 75 | 20065110070079683帮忙看下订单怎么付不了款呢；21622588981079683帮忙改下价格呗谢谢 | promotion_policy | scene_mismatch | logistics_policy | 25.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/25.0<br>tmall_not_fresh_return_rule_0007/quality_issue/20.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/19.0 |  |  |
| 76 | 复制这条信息打开手机淘宝即可看到九都纸皮核桃薄皮奶油味休闲坚果零食炒货年货干果2500g新货v87tmu1QZn | stock_policy | scene_mismatch | logistics_policy | 12.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/12.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/12.0<br>taobao_dispute_address_change_failed_0001/order_modify_policy/11.0 |  |  |
| 77 | 我之前买的都是绵柔巾因为用着还不错才买这么多你家的湿巾囤货给还没出生的宝宝试用了一下居然浮那么多油让我怎么放心用 | gift_policy | scene_mismatch | service_recovery | 27.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/27.0<br>tmall_after_sale_service_rule_0005/logistics_policy/15.0<br>tmall_after_sale_service_rule_0010/logistics_policy/15.0 |  |  |
| 78 | 那我能买一罐柠檬和一罐枸杞再加5元买一罐菊花茶吗；你看一下吧那是不是能都装在一起啊分开有点麻烦的就是送过来的时候 | promotion_policy | scene_mismatch | logistics_policy | 26.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/26.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/26.0<br>tmall_trade_timeliness_rule_0022/refund_policy/24.0 |  |  |
| 79 | 528690173109；你虽然价钱弄底了但是你运费算了5块还不是一样啊上次买没有减价但是包邮算清楚还比这次便宜 | shipping_fee_policy | scene_mismatch | logistics_policy | 38.0 | tmall_logistics_timeliness_rule_0007/logistics_policy/38.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/30.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/23.0 |  |  |
| 80 | 528690173109；你虽然价钱弄底了但是你运费算了5块还不是一样啊上次买没有减价但是包邮算清楚还比这次便宜 | shipping_fee_policy | scene_mismatch | logistics_policy | 38.0 | tmall_logistics_timeliness_rule_0007/logistics_policy/38.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/30.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/23.0 |  |  |

# low_score

- source: `data/eval/real_replay_mining_v1/low_score_sample.jsonl`
- shown_rows: 80

## expected_scene distribution in shown rows

| scene | count |
|---|---:|
| promotion_policy | 10 |
| gift_policy | 9 |
| product_qa_policy | 8 |
| complaint_policy | 8 |
| express_policy | 7 |
| bulk_purchase_policy | 7 |
| unknown | 5 |
| stock_policy | 5 |
| refund_policy | 4 |
| return_exchange | 4 |
| price_protection | 3 |
| quality_issue | 3 |
| shipping_policy | 2 |
| coupon_policy | 1 |
| order_modify_policy | 1 |
| shipping_fee_policy | 1 |
| description_mismatch | 1 |
| missing_package_policy | 1 |

## hit_status distribution in shown rows

| hit_status | count |
|---|---:|
| scene_mismatch | 59 |
| hit | 11 |
| low_score | 10 |

## review table

| idx | retrieval_query | expected_scene | hit_status | top1_scene | top1_score | top_cards | suggested_bucket | note |
|---:|---|---|---|---|---:|---|---|---|
| 1 | 复制这条信息打开手机淘宝即可看到SHOPNAME婴儿纯棉柔巾宝宝棉柔巾纸巾干湿巾干湿两用巾100抽12包au71n6kMba | gift_policy | scene_mismatch | quality_issue | 14.0 | tmall_not_fresh_return_rule_0007/quality_issue/14.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/12.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/11.0 |  |  |
| 2 | xuxili2008126com许熙丽xuxili2008126com许熙丽xuxili2008126com许熙丽；谢谢 | unknown | hit | logistics_policy | 10.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/10.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/7.0<br>tmall_not_fresh_return_rule_0007/quality_issue/7.0 |  |  |
| 3 | xuxili2008126com许熙丽xuxili2008126com许熙丽xuxili2008126com许熙丽；谢谢 | price_protection | scene_mismatch | logistics_policy | 10.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/10.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/7.0<br>tmall_not_fresh_return_rule_0007/quality_issue/7.0 |  |  |
| 4 | 复制这条信息打开手机淘宝即可看到九都纸皮核桃薄皮奶油味休闲坚果零食炒货年货干果2500g新货v87tmu1QZn | stock_policy | scene_mismatch | logistics_policy | 12.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/12.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/12.0<br>taobao_dispute_address_change_failed_0001/order_modify_policy/11.0 |  |  |
| 5 | 今天不是199了在吗520401029636不在啊520401029636520401029636；那算了 | promotion_policy | scene_mismatch | logistics_policy | 11.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/11.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/11.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/9.0 |  |  |
| 6 | 最近我拆了一包湿巾感觉有点洗涤剂的味道放在热水里蘸一下再拧干的话热水里会有油花有遇到过这种情况的么 | product_qa_policy | scene_mismatch | return_exchange | 13.0 | tmall_7day_return_rule_0018/return_exchange/13.0<br>tmall_7day_return_rule_0016/return_exchange/11.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/9.0 |  |  |
| 7 | 加上赶工包装袋省封口贴了刀尖也都没磨好我自己急用没办法但我会给差评的；你们这样子做生意肯定不行的 | complaint_policy | scene_mismatch | service_recovery | 12.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/12.0<br>tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0 |  |  |
| 8 | 加上赶工包装袋省封口贴了刀尖也都没磨好我自己急用没办法但我会给差评的；你们这样子做生意肯定不行的 | complaint_policy | scene_mismatch | service_recovery | 12.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/12.0<br>tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0 |  |  |
| 9 | 加上赶工包装袋省封口贴了刀尖也都没磨好我自己急用没办法但我会给差评的；随便你拉反正我也失去信心 | complaint_policy | scene_mismatch | service_recovery | 13.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/13.0<br>tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0 |  |  |
| 10 | 加上赶工包装袋省封口贴了刀尖也都没磨好我自己急用没办法但我会给差评的；随便你拉反正我也失去信心 | complaint_policy | scene_mismatch | service_recovery | 13.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/13.0<br>tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0 |  |  |
| 11 | 加上赶工包装袋省封口贴了刀尖也都没磨好我自己急用没办法但我会给差评的；随便你拉反正我也失去信心 | complaint_policy | scene_mismatch | service_recovery | 13.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/13.0<br>tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0 |  |  |
| 12 | SHOPNAME婴儿湿纸巾宝宝手口湿巾棉柔湿巾纸无香随身25抽12小包点击链接再选择浏览器打开 | gift_policy | scene_mismatch | quality_issue | 10.0 | tmall_not_fresh_return_rule_0011/quality_issue/10.0<br>tmall_7day_return_rule_0016/return_exchange/9.0<br>tmall_after_sale_service_rule_0003/logistics_policy/7.0 |  |  |
| 13 | SHOPNAME婴儿湿纸巾宝宝手口湿巾棉柔湿巾纸无香随身25抽12小包点击链接再选择浏览器打开 | gift_policy | scene_mismatch | quality_issue | 10.0 | tmall_not_fresh_return_rule_0011/quality_issue/10.0<br>tmall_7day_return_rule_0016/return_exchange/9.0<br>tmall_after_sale_service_rule_0003/logistics_policy/7.0 |  |  |
| 14 | 没回复你也没给我说啊而且又是我再次找你们你们这也不负责啊我昨天才做的剖腹产还要忍着巨疼天天追件 | express_policy | low_score | refund_policy | 6.0 | phase12_refund_not_received_0001/refund_policy/6.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/6.0<br>tmall_7day_return_rule_0005/return_exchange/5.0 |  |  |
| 15 | 不公平呀我买啊2袋可以优惠15元一袋我买3袋反而只能优惠13元一袋了买多了反而单价还高于买少的 | promotion_policy | scene_mismatch | logistics_policy | 13.0 | tmall_after_sale_service_rule_0010/logistics_policy/13.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/13.0<br>tmall_after_sale_service_rule_0003/logistics_policy/11.0 |  |  |
| 16 | 我用3袋拍一次共拍2次还是6袋一起拍都送2份礼品呢545468795743；嗯嗯了解了哦 | refund_policy | scene_mismatch | logistics_policy | 9.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/9.0<br>tmall_not_fresh_return_rule_0003/quality_issue/9.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/9.0 |  |  |
| 17 | 我用3袋拍一次共拍2次还是6袋一起拍都送2份礼品呢545468795743；嗯嗯了解了哦 | refund_policy | scene_mismatch | logistics_policy | 9.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/9.0<br>tmall_not_fresh_return_rule_0003/quality_issue/9.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/9.0 |  |  |
| 18 | 您好我刚才拍了一个茶刀因为我这边现在没有圆通提醒您一下别发圆通的谢谢啦；那到啥时候 | express_policy | scene_mismatch | return_exchange | 14.0 | tmall_7day_return_rule_0018/return_exchange/14.0<br>tmall_7day_return_rule_0006/return_exchange/12.0<br>tmall_7day_return_rule_0007/shipping_fee_policy/12.0 |  |  |
| 19 | 亲这次双十二便宜点嘛下回涨了就涨了吧之前你们跟我说过都可以299的就这次把通融一下 | promotion_policy | scene_mismatch | return_exchange | 9.0 | tmall_7day_return_rule_0010/return_exchange/9.0<br>tmall_after_sale_service_rule_0003/logistics_policy/9.0<br>tmall_after_sale_service_rule_0010/logistics_policy/9.0 |  |  |
| 20 | 店家我想再买五包大核桃能原来价82元一包买给我吗我可是买了你们很多了也算老客户了吧 | promotion_policy | low_score | order_modify_policy | 6.0 | phase12_order_wrong_cancel_reorder_0001/order_modify_policy/6.0<br>phase12_refund_not_received_0001/refund_policy/6.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/6.0 |  |  |
| 21 | 是纸皮核桃ba；我看评价说有大大小小的嗯我先买一袋子看看好的话在过来买保证质量谢谢 | quality_issue | hit | quality_issue | 9.0 | tmall_after_sale_service_rule_0007/quality_issue/9.0<br>tmall_mismatch_compensation_rule_0003/quality_issue/9.0<br>phase12_gift_missing_or_promise_unfulfilled_0001/gift_policy/6.0 |  |  |
| 22 | 以前最早几次在你们这里买都是发的汇通后来我再买备注的汇通你们都发成邮政了邮政太慢了 | express_policy | hit | express_policy | 11.0 | phase12_express_choice_availability_0001/express_policy/11.0<br>taobao_breach_promise_carrier_method_0001/express_policy/11.0<br>taobao_dispute_address_change_failed_0001/order_modify_policy/11.0 |  |  |
| 23 | 538832022583；之前我买纯棉那款包邮三亚了买无纺布这款12包的能包三亚吗 | product_qa_policy | scene_mismatch | return_exchange | 12.0 | tmall_return_shipping_protection_rule_0004/return_exchange/12.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/11.0<br>tmall_7day_return_rule_0007/shipping_fee_policy/9.0 |  |  |
| 24 | 538405926243有货吗椒盐味的送夹子吗538405926243在吗人呢；哦 | coupon_policy | scene_mismatch | return_exchange | 9.0 | tmall_7day_return_rule_0006/return_exchange/9.0<br>tmall_7day_return_rule_0010/return_exchange/9.0<br>tmall_7day_return_rule_0015/return_exchange/9.0 |  |  |
| 25 | 我去把评论删了吧那天总共买了3份蛋黄；没事没事在外边读书能吃到嘉兴的青团也是不易 | complaint_policy | scene_mismatch | logistics_policy | 9.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/9.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/9.0<br>tmall_trade_timeliness_rule_0022/refund_policy/9.0 |  |  |
| 26 | 小号红檀木茶针你看看我们买过好多好多次了哦每次都是你们家购买；好了帮忙早点发货哦 | promotion_policy | scene_mismatch | shipping_policy | 14.0 | phase12_shipping_urge_before_overdue_0001/shipping_policy/14.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/12.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/11.0 |  |  |
| 27 | 包装写的紫外线消毒漏气了消毒不就没用了就是普通卫生纸了；等你补发到了也已经生了 | return_exchange | scene_mismatch | order_modify_policy | 12.0 | phase12_order_modify_address_0001/order_modify_policy/12.0<br>tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0 |  |  |
| 28 | 包装写的紫外线消毒漏气了消毒不就没用了就是普通卫生纸了；等你补发到了也已经生了 | return_exchange | scene_mismatch | order_modify_policy | 12.0 | phase12_order_modify_address_0001/order_modify_policy/12.0<br>tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0 |  |  |
| 29 | 你家这种纸也太恐怖了吧一收到全部都是开封了的试问这种样子谁敢给孩子用；在不在 | unknown | hit | quality_issue | 11.0 | tmall_not_fresh_return_rule_0003/quality_issue/11.0<br>tmall_after_sale_service_rule_0003/logistics_policy/9.0<br>tmall_after_sale_service_rule_0005/logistics_policy/9.0 |  |  |
| 30 | 就是想买核桃一直在你家买我想买4袋发两个地方；560540315373是送这 | stock_policy | scene_mismatch | logistics_policy | 11.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/11.0<br>tmall_7day_return_rule_0011/return_exchange/9.0<br>tmall_after_sale_service_rule_0003/logistics_policy/9.0 |  |  |
| 31 | 长期要用的买谁家的都是买多送包长期买你家的；试一下吧好用下次再买就多送一包哦 | bulk_purchase_policy | low_score | shipping_policy | 7.0 | tmall_logistics_timeliness_rule_0005/shipping_policy/7.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/7.0<br>phase12_shipping_urge_before_overdue_0001/shipping_policy/6.0 |  |  |
| 32 | 长期要用的买谁家的都是买多送包长期买你家的；试一下吧好用下次再买就多送一包哦 | bulk_purchase_policy | low_score | shipping_policy | 7.0 | tmall_logistics_timeliness_rule_0005/shipping_policy/7.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/7.0<br>phase12_shipping_urge_before_overdue_0001/shipping_policy/6.0 |  |  |
| 33 | 竖着刻下来；哦⊙o⊙哦那我们先订200行吗过段时间再订因为这也是给公司订的 | bulk_purchase_policy | scene_mismatch | shipping_policy | 11.0 | tmall_logistics_timeliness_rule_0005/shipping_policy/11.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/10.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/9.0 |  |  |
| 34 | 能把零头去了嘛；我忘了备注了你记得一定要给我两张盖好章的收据啊我要报销用的 | order_modify_policy | scene_mismatch | return_exchange | 9.0 | tmall_7day_return_rule_0011/return_exchange/9.0<br>phase12_express_choice_availability_0001/express_policy/8.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/8.0 |  |  |
| 35 | 茶巾不要了你都给我换成大号的我就去拍两套然后我再拍点别的凑100块钱的行不 | price_protection | scene_mismatch | logistics_policy | 10.0 | tmall_logistics_timeliness_rule_0007/logistics_policy/10.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/10.0<br>tmall_not_fresh_return_rule_0007/quality_issue/10.0 |  |  |
| 36 | 包装质量都一样的吧；好的那今天给我发出来好客户们都要放假了我要给他们送过去 | quality_issue | scene_mismatch | return_exchange | 11.0 | tmall_7day_return_rule_0017/return_exchange/11.0<br>tmall_7day_return_rule_0011/return_exchange/9.0<br>tmall_7day_return_rule_0015/return_exchange/9.0 |  |  |
| 37 | 包装质量都一样的吧；好的那今天给我发出来好客户们都要放假了我要给他们送过去 | quality_issue | scene_mismatch | return_exchange | 11.0 | tmall_7day_return_rule_0017/return_exchange/11.0<br>tmall_7day_return_rule_0011/return_exchange/9.0<br>tmall_7day_return_rule_0015/return_exchange/9.0 |  |  |
| 38 | 怎么湿巾泡到水里老是油油的；我妯娌也拿了去用说也是浮一层油都不敢给孩子用 | gift_policy | scene_mismatch | shipping_policy | 11.0 | tmall_logistics_timeliness_rule_0005/shipping_policy/11.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/11.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/11.0 |  |  |
| 39 | 因为我们不可能为了一个湿巾纸就去专门检测机构做检测；也只能自己用荧光照了 | gift_policy | scene_mismatch | return_exchange | 11.0 | tmall_return_shipping_protection_rule_0006/return_exchange/11.0<br>phase12_order_modify_address_0001/order_modify_policy/8.0<br>tmall_7day_return_rule_0016/return_exchange/7.0 |  |  |
| 40 | 因为我们不可能为了一个湿巾纸就去专门检测机构做检测；也只能自己用荧光照了 | gift_policy | scene_mismatch | return_exchange | 11.0 | tmall_return_shipping_protection_rule_0006/return_exchange/11.0<br>phase12_order_modify_address_0001/order_modify_policy/8.0<br>tmall_7day_return_rule_0016/return_exchange/7.0 |  |  |
| 41 | 如果要自取的话我着还在月子里自取不太方便；我记得上次从你家买的就是自取呀 | unknown | hit | logistics_policy | 11.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/11.0<br>tmall_not_fresh_return_rule_0003/quality_issue/7.0<br>phase12_shipping_urge_before_overdue_0001/shipping_policy/6.0 |  |  |
| 42 | 你好先拍个一袋方便的话送个小袋椒盐味的尝一下味道好还要买；明后天的没关系 | stock_policy | low_score | shipping_policy | 6.0 | phase12_shipping_urge_before_overdue_0001/shipping_policy/6.0<br>tmall_7day_return_rule_0006/return_exchange/5.0<br>tmall_7day_return_rule_0007/shipping_fee_policy/5.0 |  |  |
| 43 | 我刚拍了一包5斤装核桃有一斤装一斤装的包装袋吗有的话需要配5个包装袋谢谢 | shipping_fee_policy | scene_mismatch | return_exchange | 14.0 | tmall_7day_return_rule_0017/return_exchange/14.0<br>tmall_7day_return_rule_0018/return_exchange/13.0<br>tmall_7day_return_rule_0015/return_exchange/11.0 |  |  |
| 44 | 那每样都发一点吧；我是酒店用的最好能今天发货好的待会我们酒店会有人拍的 | shipping_policy | hit | shipping_policy | 14.0 | phase12_shipping_urge_before_overdue_0001/shipping_policy/14.0<br>taobao_breach_promise_gift_0001/gift_policy/11.0<br>tmall_after_sale_service_rule_0003/logistics_policy/9.0 |  |  |
| 45 | 那每样都发一点吧；我是酒店用的最好能今天发货好的待会我们酒店会有人拍的 | shipping_policy | hit | shipping_policy | 14.0 | phase12_shipping_urge_before_overdue_0001/shipping_policy/14.0<br>taobao_breach_promise_gift_0001/gift_policy/11.0<br>tmall_after_sale_service_rule_0003/logistics_policy/9.0 |  |  |
| 46 | 44265219693；536534099634这两款湿巾有什么区别吗 | gift_policy | scene_mismatch | return_exchange | 11.0 | tmall_return_shipping_protection_rule_0006/return_exchange/11.0<br>tmall_after_sale_service_rule_0005/logistics_policy/9.0<br>tmall_after_sale_service_rule_0007/quality_issue/9.0 |  |  |
| 47 | 纸皮核桃我要绿色袋子包装的一箱几袋在吗；保证质量合作愉快注意生产日期 | product_qa_policy | scene_mismatch | return_exchange | 14.0 | tmall_7day_return_rule_0018/return_exchange/14.0<br>tmall_7day_return_rule_0017/return_exchange/11.0<br>tmall_mismatch_compensation_rule_0003/quality_issue/11.0 |  |  |
| 48 | 纸皮核桃我要绿色袋子包装的一箱几袋在吗；保证质量合作愉快注意生产日期 | product_qa_policy | scene_mismatch | return_exchange | 14.0 | tmall_7day_return_rule_0018/return_exchange/14.0<br>tmall_7day_return_rule_0017/return_exchange/11.0<br>tmall_mismatch_compensation_rule_0003/quality_issue/11.0 |  |  |
| 49 | 你好这款是拍两件148元吗；亲爱哒客官小店默认韵达百世汇通天天快递哦 | express_policy | scene_mismatch | logistics_policy | 11.0 | tmall_after_sale_service_rule_0003/logistics_policy/11.0<br>tmall_not_fresh_return_rule_0011/quality_issue/11.0<br>tmall_after_sale_service_rule_0005/logistics_policy/9.0 |  |  |
| 50 | 你好这款是拍两件148元吗；亲爱哒客官小店默认韵达百世汇通天天快递哦 | express_policy | scene_mismatch | logistics_policy | 11.0 | tmall_after_sale_service_rule_0003/logistics_policy/11.0<br>tmall_not_fresh_return_rule_0011/quality_issue/11.0<br>tmall_after_sale_service_rule_0005/logistics_policy/9.0 |  |  |
| 51 | 加上赶工包装袋省封口贴了刀尖也都没磨好我自己急用没办法但我会给差评的 | complaint_policy | scene_mismatch | return_exchange | 9.0 | tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0<br>tmall_7day_return_rule_0017/return_exchange/9.0 |  |  |
| 52 | 加上赶工包装袋省封口贴了刀尖也都没磨好我自己急用没办法但我会给差评的 | complaint_policy | scene_mismatch | return_exchange | 9.0 | tmall_7day_return_rule_0015/return_exchange/9.0<br>tmall_7day_return_rule_0016/return_exchange/9.0<br>tmall_7day_return_rule_0017/return_exchange/9.0 |  |  |
| 53 | 我先退款再拍吧不小心弄上花呗了；我看那个花呗还挺麻烦呢到时候还得还款 | refund_policy | scene_mismatch | invoice_policy | 11.0 | taobao_invoice_apply_timing_0001/invoice_policy/11.0<br>tmall_after_sale_service_rule_0003/logistics_policy/9.0<br>tmall_after_sale_service_rule_0005/logistics_policy/9.0 |  |  |
| 54 | 我先退款再拍吧不小心弄上花呗了；我看那个花呗还挺麻烦呢到时候还得还款 | refund_policy | scene_mismatch | invoice_policy | 11.0 | taobao_invoice_apply_timing_0001/invoice_policy/11.0<br>tmall_after_sale_service_rule_0003/logistics_policy/9.0<br>tmall_after_sale_service_rule_0005/logistics_policy/9.0 |  |  |
| 55 | 和还有一款79912包的啥区别；538832022583这件是无纺布 | product_qa_policy | scene_mismatch | return_exchange | 12.0 | tmall_return_shipping_protection_rule_0004/return_exchange/12.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/9.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/9.0 |  |  |
| 56 | 这个是四个一共259对吧；每个里面都是200个还是四个一共200个呀 | bulk_purchase_policy | scene_mismatch | logistics_policy | 12.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/12.0<br>tmall_mismatch_compensation_rule_0006/description_mismatch/9.0<br>tmall_not_fresh_return_rule_0003/quality_issue/9.0 |  |  |
| 57 | 这个是四个一共259对吧；每个里面都是200个还是四个一共200个呀 | bulk_purchase_policy | scene_mismatch | logistics_policy | 12.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/12.0<br>tmall_mismatch_compensation_rule_0006/description_mismatch/9.0<br>tmall_not_fresh_return_rule_0003/quality_issue/9.0 |  |  |
| 58 | 538832022583；528690173109这个是纯棉加大尺寸 | product_qa_policy | scene_mismatch | return_exchange | 10.0 | tmall_return_shipping_protection_rule_0004/return_exchange/10.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/9.0<br>tmall_mismatch_compensation_rule_0006/description_mismatch/9.0 |  |  |
| 59 | 我自己洗脸哪种最好；546487395690543826442006 | unknown | hit | logistics_policy | 10.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/10.0<br>tmall_after_sale_service_rule_0005/logistics_policy/9.0<br>tmall_not_fresh_return_rule_0010/quality_issue/9.0 |  |  |
| 60 | 我自己洗脸哪种最好；546487395690543826442006 | unknown | hit | logistics_policy | 10.0 | tmall_logistics_timeliness_rule_0024/logistics_policy/10.0<br>tmall_after_sale_service_rule_0005/logistics_policy/9.0<br>tmall_not_fresh_return_rule_0010/quality_issue/9.0 |  |  |
| 61 | 44265219693这款是湿巾是吗；538832022583这款呢 | gift_policy | scene_mismatch | return_exchange | 10.0 | tmall_return_shipping_protection_rule_0004/return_exchange/10.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/7.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/7.0 |  |  |
| 62 | 44265219693这款是湿巾是吗；538832022583这款呢 | gift_policy | scene_mismatch | return_exchange | 10.0 | tmall_return_shipping_protection_rule_0004/return_exchange/10.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/7.0<br>tmall_logistics_timeliness_rule_0024/logistics_policy/7.0 |  |  |
| 63 | 拖太久我投诉了；那边现在库存有几支好的先发过来给我少的第二次再补上 | stock_policy | scene_mismatch | service_recovery | 12.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/12.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/11.0<br>taobao_breach_promise_gift_0001/gift_policy/11.0 |  |  |
| 64 | 拖太久我投诉了；那边现在库存有几支好的先发过来给我少的第二次再补上 | stock_policy | scene_mismatch | service_recovery | 12.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/12.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/11.0<br>taobao_breach_promise_gift_0001/gift_policy/11.0 |  |  |
| 65 | 前几天我在贵店买了10盒青团本来说送点小礼品的亲好像给忘记了亲在吗 | promotion_policy | scene_mismatch | shipping_policy | 11.0 | tmall_trade_timeliness_rule_0002/shipping_policy/11.0<br>tmall_logistics_timeliness_rule_0005/shipping_policy/7.0<br>phase12_gift_missing_or_promise_unfulfilled_0001/gift_policy/6.0 |  |  |
| 66 | 我的确是用了以后就有点过敏啊；但是里面有残留物之前用的是婴儿专用纸 | product_qa_policy | scene_mismatch | return_exchange | 11.0 | tmall_7day_return_rule_0018/return_exchange/11.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/9.0<br>tmall_logistics_timeliness_rule_0009/logistics_policy/9.0 |  |  |
| 67 | 那还是40几吗我实在听不懂你说的活动写20几现在价格又不变我看不懂 | promotion_policy | scene_mismatch | refund_policy | 14.0 | tmall_trade_timeliness_rule_0022/refund_policy/14.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/11.0<br>taobao_delivery_stockout_refuse_ship_0001/shipping_policy/11.0 |  |  |
| 68 | 你不是说一斤一包吗；你家85元5斤是整包5斤还是一斤一包如果是我拍 | description_mismatch | scene_mismatch | logistics_policy | 13.0 | tmall_logistics_timeliness_rule_0006/logistics_policy/13.0<br>tmall_logistics_timeliness_rule_0007/logistics_policy/13.0<br>tmall_not_fresh_return_rule_0003/quality_issue/11.0 |  |  |
| 69 | 一看就知道是红木的应为我自己有还有2支在家；我现在下对吧要落实哦 | bulk_purchase_policy | low_score | express_policy | 3.0 | sample_shipping_policy_0002/express_policy/3.0<br>phase12_refund_not_received_0001/refund_policy/2.0 |  |  |
| 70 | 一看就知道是红木的应为我自己有还有2支在家；我现在下对吧要落实哦 | bulk_purchase_policy | low_score | express_policy | 3.0 | sample_shipping_policy_0002/express_policy/3.0<br>phase12_refund_not_received_0001/refund_policy/2.0 |  |  |
| 71 | 您要把粽子换了收件人是谁呢我看看可不可以；不超重吗那是多大个包裹 | product_qa_policy | scene_mismatch | logistics_policy | 14.0 | taobao_dispute_shortage_combined_package_0001/logistics_policy/14.0<br>phase12_gift_missing_or_promise_unfulfilled_0001/gift_policy/13.0<br>tmall_logistics_timeliness_rule_0006/logistics_policy/11.0 |  |  |
| 72 | 好的那我这边准备下单收货以后就麻烦您开发票您开发票的话是寄过来吗 | promotion_policy | scene_mismatch | invoice_policy | 14.0 | taobao_invoice_apply_timing_0001/invoice_policy/14.0<br>taobao_breach_promise_discount_difference_0001/promotion_policy/13.0<br>taobao_breach_promise_gift_0001/gift_policy/13.0 |  |  |
| 73 | 我刚才尝了一个觉得太甜了我吃不了那个味道所以就想退掉那盒没动过的 | price_protection | scene_mismatch | order_modify_policy | 12.0 | phase12_order_wrong_cancel_reorder_0001/order_modify_policy/12.0<br>phase12_order_modify_address_0001/order_modify_policy/6.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/6.0 |  |  |
| 74 | 在吗棉签棒也太差了吧拆开来这样的无语你们这是给宝宝用的吗不理人了 | return_exchange | hit | return_exchange | 9.0 | tmall_7day_return_rule_0016/return_exchange/9.0<br>tmall_mismatch_compensation_rule_0006/description_mismatch/9.0<br>tmall_mismatch_compensation_rule_0007/quality_issue/9.0 |  |  |
| 75 | 在吗棉签棒也太差了吧拆开来这样的无语你们这是给宝宝用的吗不理人了 | return_exchange | hit | return_exchange | 9.0 | tmall_7day_return_rule_0016/return_exchange/9.0<br>tmall_mismatch_compensation_rule_0006/description_mismatch/9.0<br>tmall_mismatch_compensation_rule_0007/quality_issue/9.0 |  |  |
| 76 | 你好我拍的照看到了吗这次核桃整体都很小坏的也很多我都是第三次买了 | missing_package_policy | scene_mismatch | description_mismatch | 11.0 | tmall_mismatch_compensation_rule_0006/description_mismatch/11.0<br>phase12_express_choice_availability_0001/express_policy/6.0<br>tmall_7day_return_rule_0018/return_exchange/5.0 |  |  |
| 77 | 么么哒千万不能忘；542480334969亲爱的这是一包的价格吗 | promotion_policy | scene_mismatch | quality_issue | 11.0 | tmall_after_sale_service_rule_0007/quality_issue/11.0<br>tmall_return_shipping_protection_rule_0006/return_exchange/11.0<br>tmall_after_sale_service_rule_0003/logistics_policy/9.0 |  |  |
| 78 | 我这里邮政气人的很；我备注了没中通你应该提醒下我我就不备注自取了 | express_policy | low_score | express_policy | 7.0 | sample_shipping_policy_0002/express_policy/7.0<br>phase12_express_choice_availability_0001/express_policy/6.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/6.0 |  |  |
| 79 | 我这里邮政气人的很；我备注了没中通你应该提醒下我我就不备注自取了 | express_policy | low_score | express_policy | 7.0 | sample_shipping_policy_0002/express_policy/7.0<br>phase12_express_choice_availability_0001/express_policy/6.0<br>phase12_service_recovery_delay_complaint_0001/service_recovery/6.0 |  |  |
| 80 | 539833396424539833396424这也是你们家的啊 | promotion_policy | low_score | service_recovery | 6.0 | phase12_service_recovery_delay_complaint_0001/service_recovery/6.0<br>tmall_7day_return_rule_0010/return_exchange/5.0<br>tmall_7day_return_rule_0017/return_exchange/5.0 |  |  |

# dpo_audit

- source: `data/eval/real_replay_mining_v1/dpo_candidate_audit_sample.jsonl`
- shown_rows: 80

## issue distribution in shown rows

| issue | count |
|---|---:|
| rejected_too_short | 56 |
| chosen_too_short | 55 |

| idx | issues | prompt | chosen | rejected | suggested_decision |
|---:|---|---|---|---|---|
| 1 |  | 用户：538405926243买二份有没有少点呀 | 亲亲真的不好意思我们已经是优惠价了呢小本生意请亲谅解 | 恩恩客官现在有个活动参加就有礼哦 |  |
| 2 | chosen_too_short | 用户：我一不小心就拍了一组我在拍一组可以嘛 客服：要不亲退了一起拍吧 用户：那就等你们处理喽 | 好的亲退了 | 亲亲您的订单今天五箱都会发货的您看今天一起给您发出可以吗 |  |
| 3 | rejected_too_short | 用户：那好的就拍这款 客服：好的哦亲爱的 用户：颜色有这种 客服：二合一的颜色有2个哦亲 用户：这个不是叫红色吗 客服：黑的 用户：这个不要 客服：第二个红的好的哦亲亲您拍的宝贝可以使用优惠券哦达到可 | 颜色的话一般茶刀茶针和二合一的话都是红木檀和黑木檀哦 | 好的呢帮您备注了哦 |  |
| 4 |  | 用户：不是免运费 | 本店茶具订单满99包邮除宁夏青海内蒙古海南新疆西藏满39包邮 | 查清楚看是什么原因给亲补发过去吧 |  |
| 5 | chosen_too_short | 用户：我已经买了吗榴莲干555185256661 客服：好的 用户：买了吗 客服：买了 用户：都一个星期了 客服：亲实在抱歉之前到的一批货因为质量问题直接退回厂家了预计明后天会到呢到货后及时给您发货哦 | 好吃的 | 您辛苦打扫下肯定漏的到处都是了 |  |
| 6 | rejected_too_short | 用户：好 客服：恩恩 用户：改过了 客服：好的 用户：谢谢啦 客服：不客气哦 用户：为什么迟迟不给我发货 | 实在抱歉呢由于订单量大您的订单本来安排今天发货的呢 | 对的亲 |  |
| 7 | chosen_too_short,rejected_too_short | 用户：噢和视频一样应该沒有坏的 客服：完全没有坏果率是没法保证的哦作为农副产品是有一定坏果率的不过小店这边有仔细检查不用担心的 用户：我过去网上买这样价没有一粒坏的难得有一到二粒很少 客服：嗯嗯是的因 | 小店尽快给您发出哦 | 不能哦 |  |
| 8 | chosen_too_short | 用户：你好寄哪几家快递 客服：您好邮政EMS随机发 用户：3组送什么 | 拍2组送2包湿巾3组也是2包 | 纯棉的528690173109纯棉的大片的 |  |
| 9 | chosen_too_short,rejected_too_short | 用户：你是一包有3代还是一代就是一代 客服：一袋就是一袋哦266三袋 用户：我要买12代那是多少钱呢 客服：1064哦现在有满88-5的券呢 用户：是不是只要90多了应该是101了 客服：1014呢5 | 记得勾选优惠券哦 | 地址亲亲复制给我哦 |  |
| 10 |  | 用户：每一样都要点要二百个 | 单个的话价格都是最低了哦都是亏本促销的只是为了前期冲销量的548881602868547107612966547393486364547259785739这款单买可以再便宜鲜肉蜜枣豆沙最低53蛋黄肉粽 | 客官我把链接发您您可以点击进入查看一下547481727679548112521279547917318438 |  |
| 11 | chosen_too_short,rejected_too_short | 用户：在吗 客服：屹茗堂周三特价及520表白节在的哦 用户：有什么快递可以发 客服：亲爱哒客官小店默认邮政百世汇通天天快递哦 用户：百世 | 好的 | 那下次您买的话送您吧补给您 |  |
| 12 | rejected_too_short | 用户：等下收藏了送啥吃的 客服：试吃是随机赠送哦客官比如牛蹄筋牛肉干这种而且最好是晒一下收小店店铺截图哦我再帮您申请张优惠券哦下次来小店购买芒果干可以优惠哦 用户：这样给你看 客服：是收藏小店店铺呢不 | 优惠券有效期至8月31日谢谢客官支持小店哦 | 您好 |  |
| 13 | chosen_too_short,rejected_too_short | 用户：那明天提供开票信息这些给你吧行吗 客服：要全部的开增值税专用票的要求----提供开票信息营业执照复印件一般纳税人证明复印件开增值税普通票的要求----个人或者公司抬头发票开的是----用品 用户 | 亲只有这些齐全的才能开 | 这款就是层数的不一样 |  |
| 14 | rejected_too_short | 用户：亲 客服：您好 用户：我的东西少了很多啊 客服：应该是分包发的稍等我查下呢 用户：好 客服：972171389843297200789513322个包裹哦亲 用户：为什么发保定啊我就在天津 客服 | 应该这两天会到的这个会联系下快递 | 恩恩好的 |  |
| 15 | chosen_too_short,rejected_too_short | 用户：那怎么办 客服：您要多分呢 用户：先要四五份吧不知道质量怎么样 客服：好的 用户：单怎么下 | 您提交以后哪里可以修改数量的 | 今天给您发出去哦 |  |
| 16 | chosen_too_short,rejected_too_short | 用户：在不 客服：在的哦 用户：这是榴莲干是真的榴莲 客服：是的呢 用户：味道怎么样 客服：榴莲的味道很浓厚哦 用户：吃起来和新鲜的有很大差别嘛保鲜 | 吃起来也很松脆 | 是的呢 |  |
| 17 | chosen_too_short,rejected_too_short | 用户：不好我可要退的哦 客服：好的呢 用户：杭州桐庐几天到 | 一般1-2天 | 5号活动结束后哦 |  |
| 18 | chosen_too_short,rejected_too_short | 用户：改了可以了吗什么时候退款 客服：好的呢帮您联系一下掌柜哦掌柜看到后会尽快处理哦 用户：希望快点 客服：好的呢 用户：别给我像发货一样的慢 | 不会的呢 | 顺丰到付的不包邮 |  |
| 19 | rejected_too_short | 用户：我买的东西发货了没怎么看不见物流 | 亲亲实在抱歉仓库那边说配货的时候椒盐味纸皮核桃缺货了呢新的一批明天才到货哦到货后第一时间给您打包哦亲亲不要着急哦 | 那您看怎么处理 |  |
| 20 | chosen_too_short,rejected_too_short | 用户：还可以发货吧这个是地址我刚刚又拍了 客服：好的 用户：是带别人买的不要发错了可以发百世汇通嘛 客服：亲请核对一下收货地址哦 用户：对 客服：好的小店尽快给您发出哦 用户：三袋的好的 客服：嗯嗯  | 嗯嗯已经给您修改好了哦 | 有问题有快递协商解决和 |  |
| 21 | chosen_too_short,rejected_too_short | 用户：528105689823 客服：您好 用户：有优惠吗 客服：亲已经是优惠价格了呢没有其他优惠了 用户：有送什么没 客服：这款有送湿巾 用户：什么时候发货呢 客服：拍下后72小时内发货哦 用户：几 | 对的亲 | 这款是无纺布的1820的尺寸 |  |
| 22 | chosen_too_short,rejected_too_short | 用户：我要上次的茶刀在不 客服：在的哦有什么可以帮到您的 用户：上次在你们家定制过茶刀 客服：嗯呢 用户：这次再来100支 客服：亲亲还要来100支嘛 用户：是的200支库存太大你又不优惠 客服：好的 | 稍等一下噢给亲亲9元一支 | 嗯嗯亲亲请核对一下收货地址哦 |  |
| 23 | chosen_too_short,rejected_too_short | 用户：味道棒棒哒所以给了大大的好评 客服：您很有眼光好的呢 用户：下次在跟你家店买 | 好呢 | 屹茗堂周三特价及520表白节 |  |
| 24 | chosen_too_short,rejected_too_short | 用户：在吗 客服：您好 用户：现在拍几天能到辽宁 客服：这个不一定哦 用户：大概几天不知道么 | 一般情况下3到5天左右 | 亲不会的呢您放心 |  |
| 25 | chosen_too_short,rejected_too_short | 用户：干纸巾怎么涨价了 | 现在没有活动哦亲 | 好的 |  |
| 26 | chosen_too_short,rejected_too_short | 用户：亲我是绍兴的能发申通快递或中通圆通类的吗不要发邮政 客服：亲亲其他快递停了哦 用户：奶油味好吃还是椒盐味好吃 | 奶油味的偏多哦 | 好的呢 |  |
| 27 | chosen_too_short,rejected_too_short | 用户：好发什么快递 客服：亲爱哒小店默认邮政天天百世汇通中通快递浙江省内发邮政小包哦您看哪个快递发过去您比较方便接收呢您可以下单自行备注或者联系我帮您备注哦若要发顺丰快递请联系我们补差价哦 用户：发顺 | 15 | 不补差价 |  |
| 28 |  | 用户：原味的没有25公斤的吗 客服：原味的目前只有1斤装的客官 用户：我怀孕呢有点不敢吃其他味的 客服：建议您买原味的原味的现在是活动价格哦才18一斤很优惠的 用户：可以先买两袋来试试吗 客服：孕妇也 | 好的客官您下单我帮您核对一下地址 | 因为晚上财务那边都下班了所以得等明天了呢抱歉哦 |  |
| 29 | chosen_too_short,rejected_too_short | 用户：是纯棉的吗百分百棉麻 客服：对的亲这款是纯棉的哦 用户：会不会添加了荧光增白剂 | 没有的呢亲 | 536534099634 |  |
| 30 | rejected_too_short | 用户：82元如果优惠马上拍 客服：不好意思呢价格最低了呢 用户：今天发货吗发中通如果不发就算了 | 不好意思由于过年之前订单量巨大会在48小时内按照亲亲拍下订单的时间顺序发货的哦不要着急早拍早发货哦 | 其他不修改吗客官 |  |
| 31 | chosen_too_short,rejected_too_short | 用户：为什么还要快递费 客服：您好我看下呢 用户：另外以前不都还有会员价 客服：改好了亲现在没有哦亲 用户：现在都没有了吗 客服：对的额 用户：应该还有送的东西吧 客服：实付满159会送护脐贴一盒 用 | 好的亲 | 不确定哦亲 |  |
| 32 | chosen_too_short,rejected_too_short | 用户：538832022583 客服：您好 用户：这种有没有大尺寸啊 | 1820 | 恩恩不客气呢 |  |
| 33 | chosen_too_short,rejected_too_short | 用户：你这个可以在上面刻印logo不 客服：可以的呢 用户：一般需要多久如果100个 | 3-5天哦 | 12包 |  |
| 34 |  | 用户：538872953711 客服：在的呢 用户：什么时候有货 | 10月中下旬哦到新货立刻发出呢 | 亲这个具体是时间我们没办法保证呢具体看物流时效的哦 |  |
| 35 | chosen_too_short,rejected_too_short | 用户：这些今天要发出哈快四点了怕来不及 客服：好的 用户：先帮我安排发啊哈 客服：好的 用户：怎么还三单没发货 客服：在发 用户：发出了吗再一盒 客服：改好了哦 用户：车子要走了吧 客服：今天您还要下 | 好的 | 好的亲 |  |
| 36 | rejected_too_short | 用户：这个活动几天啊 客服：亲亲要买要趁早呢听我们掌柜的语气即将涨价了呢因为这个只是冲销量看看效果的呢 用户：都是新货吧看有别家还卖陈货了 客服：保证新鲜的呢生产日期都是16年12月份的哦亲亲这边只能 | 实在抱歉呢亲亲下次光顾我这边再给您赠送一些其他的呢 | 加购物车 |  |
| 37 | chosen_too_short | 用户：好 客服：亲亲这边快递说尽量帮您拦下来因为双11期间现在快递包裹太多了有时候快递都会忙不过来的不一定能注意到呢 用户：可以拦回来的然后重发一个不要放发货单的吧 | 亲尽量帮您拦回来的呢 | 不是的不是您买的少是因为单子太多了 |  |
| 38 | rejected_too_short | 用户：西瓜子买几袋包邮 | 满２５包邮哦或者您可以带个包邮产品芒果干之类的 | 嗯嗯 |  |
| 39 | chosen_too_short | 用户：上面不是说698吗 客服：宝贝限购一件哦下周一会价格稍微上调不限购哦 用户：哦现在是多少钱呢554676601124 | 现在第二件照旧原价199哦 | 好的您的宝贝我们会以最快的速度发货的请您耐心等待哦 |  |
| 40 | chosen_too_short,rejected_too_short | 用户：在吗 客服：您好在的亲亲 用户：问下六一有活动吗 | 亲暂时还没出来活动呢 | 就一点点 |  |
| 41 | rejected_too_short | 用户：亲优惠劵不能领取 客服：您好因为是限量亲手慢了哦 用户：满50减25的优惠劵我还没有到两点就在开始领根本就没有过不是上午10点跟下午2点开抢吗 | 对的但抢的人多亲也行跟网速有关呢 | 是一个线头吗亲照片看不清呢亲 |  |
| 42 | chosen_too_short | 用户：嗯嗯上次买的无纺布哪一款不吸水呀一直都木有再用 客服：亲可以试下这款植物纤维的 用户：嗯嗯 | 嗯嗯亲 | 亲亲已经是特价了呢真的不能再便宜啦 |  |
| 43 | rejected_too_short | 用户：530746013021 客服：聚划算拍下确认收货后找客服返8元359更薄一点 用户：这两个什么区别 客服：359更薄一点 用户：550995848415 | 聚划算拍下确认收货后找客服返8元 | 是豆沙馅里面吗 |  |
| 44 |  | 用户：送个夹子吧 客服：不好意思客官我们这边没有夹子的只有开口器的呢 用户：还有优惠吗 客服：客官买多的话可以使用优惠券的哦亲请核对一下收货地址哦 用户：是的 | 好的客官明天给您发出哦现在快递4点收件走了要明天给您发出了哦 | 9890634174304邮政补发的单号哦亲可以查下 |  |
| 45 |  | 用户：好的能优惠多少呢 客服：第二份开始原价299元一盒掌柜说可以给您29一盒哦我们都是100盒开始给优惠的呢 用户：不能多送几个吗 客服：已经是优惠价了哦 用户：好吧 客服：您拍下帮您改价哦 用户： | 帮您改一下价哦请您稍等第二盒开始都是299元了哦 | 不好意思由于过年之前订单量巨大会按照亲亲拍下订单的时间顺序发货的哦一般拍下后35天左右能发货哦不要着急早拍早发货哦本店不接受急件呢 |  |
| 46 | chosen_too_short,rejected_too_short | 用户：买两包少点呗 客服：亲要什么 用户：椒盐纸皮核桃85的我买两包你给我优惠些 客服：可以领取优惠券的哦 用户：我知道再优惠点呗 客服：最低了哦 用户：再优惠点吧一下子买了10斤呢 | 真的最低了呢运费比较贵哦 | 您这边已经退款了哦 |  |
| 47 | rejected_too_short | 用户：这个差价你应该补给我 客服：亲收到了吗 用户：刚收到 | 亲确定收货后这边返差价呢3个工作日内返款 | 亲要多少个 |  |
| 48 | chosen_too_short | 用户：那个纸皮核桃是熟的咸的么奶香的好吃还是椒盐的好吃 客服：奶香的吧 用户：那我拍的是椒盐的你帮我改奶香 客服：奶油椒盐都可以的 用户：朋友介绍的第一次买 客服：好的 用户：没有坏的吧 客服：个别还 | 可以的 | 亲添加vx哦tealove2015 |  |
| 49 | chosen_too_short,rejected_too_short | 用户：对的 客服：嗯嗯亲 用户：今天还能发货 客服：活动期间72小时内发货正常付款时间在15:00之前的订单当天发货15:00之后的订单次日发货最晚不超过72小时哦亲收到商品后请先验货再签收包裹破损可 | 没有赠品哦 | 确认收货后没送吗 |  |
| 50 | rejected_too_short | 用户：哇好吃不 客服：非常好吃的呢 用户：榴莲干呢亲发什么快递 | 亲爱哒客官小店默认韵达百世汇通哦 | 嗯 |  |
| 51 | chosen_too_short,rejected_too_short | 用户：已拍 客服：好的亲亲您的宝贝我们会以最快的速度发货的您耐心等待哦 用户：如果可以发中通离我这近 | 已备注 | 今天发货 |  |
| 52 |  | 用户：538872953711 客服：您好 用户：您好这个送不送核桃夹 | 亲亲没有夹核桃的大夹子哦我们都有送开果器呢我们家的核桃壳薄如纸手捏即破哦不用担心呢 | 这边给您105元一把的价格哦我们都是200把起给优惠的呢 |  |
| 53 | chosen_too_short | 用户：在吗 客服：在的哦 用户：我想问问你们家的青团里面吃起来是酸的这正常 客服：是酸的吗 用户：对 | 全部都是这样的吗 | 因为这里显示他们的订单是没有的之前没有买过所以我可以帮他改价你这个号的话显示有两笔订单一笔是买了三罐一笔买了两罐 |  |
| 54 | chosen_too_short,rejected_too_short | 用户：太好了我群里蛮多妈妈买了你家纸 客服：多多推荐哦么么哒 用户：红包呢 | 发货后联系微哦亲 | 差不多的 |  |
| 55 | chosen_too_short,rejected_too_short | 用户：五块179这么便宜么 客服：对的亲现在520活动哦 用户：怎么加不到购物车 | 可以的呢 | 亲请核对一下收货地址哦 |  |
| 56 | chosen_too_short,rejected_too_short | 用户：明天能发货吗 | 72小时内发出 | 您好 |  |
| 57 | rejected_too_short | 用户：什么快递啊 | 亲爱哒客官小店默认邮政百世汇通天天快递1kg以内可以发申通快递哦 | 一袋2个哦 |  |
| 58 | chosen_too_short,rejected_too_short | 用户：在 客服：在的呢有什么可以帮助您的呢 用户：邮政好慢啊没物流在我想退货在吗 | 您好 | 不客气的 |  |
| 59 | chosen_too_short,rejected_too_short | 用户：嗯 客服：嗯嗯亲 用户：如果补发的还是薄的我就直接差评了这个可以接受吧 | 可以的 | 好的亲亲 |  |
| 60 | chosen_too_short,rejected_too_short | 用户：已经拆开了 客服：亲亲我们都是新货哦 用户：不拆开尝怎么知道好坏呢 客服：这边给您返现5元作为补偿您看可以吗 用户：我家经常买核桃新货不只是这样的我退回来你们可以自己尝尝看这核桃的味道实在太差了 | 不客气哦 | 嗯呢 |  |
| 61 | rejected_too_short | 用户：拍这个 客服：是的客官 用户：拍这个399就是一整套茶盒还有包括茶针和茶巾茶笔等这些赠品 客服：有送三件套的都有赠品的 用户：好的马上拍 客服：好的客官申请退换货地址之后记得在您退货来的东西里面 | 那也可以的那您重新拍宝贝好了之前的申请退款一下不过售后要白天上班帮您处理了的 | 嗯嗯谢谢客官支持小店 |  |
| 62 | chosen_too_short,rejected_too_short | 用户：搞什么呀这么久浙江过来不就一两天的时间吗 | 亲亲明天关注下这个物流哈 | 好的呢 |  |
| 63 | chosen_too_short | 用户：536023110028 客服：您好 用户：这款买一送一跟另外一款一样吗 客服：一样的 用户：525839399303 客服：送的同款哦 用户：这个 客服：嗯嗯亲 用户：这两个是一样的那就是说一 | 不客气亲 | 这个是活动开始前半小时才有的现在结束了 |  |
| 64 | chosen_too_short,rejected_too_short | 用户：你好这款是拍两件148元吗 客服：7月5日10点准时开抢前10分钟第二件0元拍下减价每人限购2件 用户：是要直接拍2件对吗 客服：是的 用户：大小是多少呢 客服：长3-35cm哦直径2cm 用户 | 可以选天天快递吗 | 亲之前的活动已经结束了呢 |  |
| 65 | rejected_too_short | 用户：已付款请查看今天能发货吗 | 不好意思由于过年之前订单量巨大会在48小时内按照亲亲拍下订单的时间顺序发货的哦不要着急早拍早发货哦 | 亲请核对一下收货地址哦 |  |
| 66 | chosen_too_short | 用户：44265219693亲这款湿巾没盖子了 客服：您好有盖子的 用户：哦哦 客服：嗯嗯亲 用户：我看很多评论说没盖子了么 | 现在有的哦 | 是的哦运费是要这么贵的哦因为重我给你改了40 |  |
| 67 | chosen_too_short,rejected_too_short | 用户：528690173109 客服：您好 用户：这款纸巾多大 客服：1520的尺寸纯棉的材质呢 用户：是你们店里尺寸最大的吗有没有2020 客服：不是呢2020的纯棉的现在预售哦拍下后5月22号发货 | 稍等 | 您好亲亲淡淡的奶香味哦不咸的 |  |
| 68 | chosen_too_short,rejected_too_short | 用户：这个是大尺寸的是吧 客服：这款纯棉的1520的尺寸 用户：528941799061 | 恩恩 | 不客气亲 |  |
| 69 | chosen_too_short | 用户：那还不就是全棉的意思 客服：手感上没有纯棉的柔软比纯棉的更厚更大一点 用户：嗯 | 嗯嗯亲 | 好的呢小二也超级喜欢吃榴莲的好好吃的不过办公室里有人不喜欢吃的话要被隔离的 |  |
| 70 | rejected_too_short | 用户：不勾选上不封顶就不是 客服：好的试用版有这功能吗 用户：有 | 好的谢谢为什么第三件也是半价了 | 是的呢送的是湿巾哦 |  |
| 71 | chosen_too_short,rejected_too_short | 用户：我送客户的 客服：恩 用户：日期太不新鲜了 客服：真空包装的10月才过期的您可以放心食用 用户：这样会起返作用的 客服：那您申请退款哦 用户：不好意思了 客服：没事的呢 用户：能便宜点吗退货也很 | 嗯呢放心哦 | 亲自己备注下呢 |  |
| 72 |  | 用户：亲在吗 客服：您好 用户：咱家这款是干巾吗 客服：528105689823这款是干的哦 用户：哦哦我现在看的这款是湿巾啊 客服：亲说的哪款呢 用户：你发来的那款干巾是多少成多少的啊 | 这个是干的饿哦528105689823 | 客官今天16点前付款是当天发货的哦16点后付款是次日发货的呢早拍早发货哦 |  |
| 73 | chosen_too_short | 用户：那应该到我这一天就够了吧 客服：我帮您查下哦 用户：赶紧呀 客服：亲亲这边仓库回复椒盐缺货了哦能改成奶油吗 用户：怎么到现在才跟我说椒盐一包也没了 客服：是的呢 用户：什么时候有货 | 明天 | 不好意思亲目前有200g和260g装的还没有500g装的 |  |
| 74 | chosen_too_short | 用户：这样的话能在过年前到吧 客服：基本上可以的 用户：哦好的 | 嗯 | 亲如果是需要普通厚度的话建议亲这款是纯棉的亲具体不是很清楚哦 |  |
| 75 | chosen_too_short,rejected_too_short | 用户：6个 客服：是的 用户：4个是不是白的2个肉的 客服：是的 用户：白的什么味道 客服：蜜枣的 用户：甜吗 客服：还可以的不是非常甜 用户：我不能吃甜 客服：那您可以单买粽子54725946925 | 您单买就可以了 | 一盒360克哦 |  |
| 76 | chosen_too_short,rejected_too_short | 用户：536672552226 客服：您好 用户：有人没 客服：在的哦 用户：这个两瓶生产日期是什么时候 客服：16年呢亲 用户：保质期多长时间啊45321327349 客服：2年呢亲 用户：这个生产 | 金额满了吗亲 | 都是近期生产的哦 |  |
| 77 | chosen_too_short | 用户：有那种盖子的吗不要纸的哪种 客服：带盖的呢 用户：是带哪种硬硬的盖子那种吗 | 这款是塑料盖的 | 亲亲由于其他快递停发本店15日后默认邮政小包哦 |  |
| 78 | chosen_too_short | 用户：44265219693 | 您好 | 那您分两单下好了然后在买家留言备注那里说明一下就可以了 |  |
| 79 | chosen_too_short,rejected_too_short | 用户：这个会不会聚划算 客服：暂时没有哦 用户：后期会不会有 | 不一定哦亲多多关注我们哦 | 嗯嗯 |  |
| 80 | chosen_too_short,rejected_too_short | 用户：你家发什么快递呢 客服：江浙沪皖默认发韵达汇通邮政小包 用户：现在棉柔纸巾有啥活动吗 客服：暂时没有呢亲您可以关注店铺哦活动会在微淘发表呢 用户：哦好的 | 嗯嗯 | 对的一包一片 |  |
