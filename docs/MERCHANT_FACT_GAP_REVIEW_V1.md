# Merchant Fact Gap Review v1

- source: `data/eval/real_replay_mining_v1/action_buckets/merchant_fact_gap.jsonl`
- total_rows: 431

## 1. Scene Distribution

| expected_scene | count |
|---|---:|
| promotion_policy | 76 |
| product_qa_policy | 59 |
| express_policy | 53 |
| bulk_purchase_policy | 46 |
| coupon_policy | 45 |
| stock_policy | 34 |
| order_modify_policy | 33 |
| shipping_fee_policy | 33 |
| gift_policy | 29 |
| invoice_policy | 23 |

## 2. Source Pool Distribution

| source_pool | count |
|---|---:|
| scene_mismatch | 185 |
| low_score | 181 |
| no_hit_or_weak | 65 |

## 3. Review Table

| idx | query | expected_scene | hit_status | top1_scene | top1_score | suggested_fact_group | note |
|---:|---|---|---|---|---:|---|---|
| 1 | 是纯棉的吗百分百棉麻；会不会添加了荧光增白剂 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 2 | 是纯棉的吗百分百棉麻；会不会添加了荧光增白剂 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 3 | 26号之前哦；差不多吧寄过来路上三天 | stock_policy | no_hit |  | 0 | stock_fact |  |
| 4 | 26号之前哦；差不多吧寄过来路上三天 | stock_policy | no_hit |  | 0 | stock_fact |  |
| 5 | 我看图片上有；我先买吧好用我再来多买 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 6 | 180块钱行不行十盒；哈哈哈都差不多 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 7 | 有开收据吗；福建艺术职业学院白茶馆 | invoice_policy | no_hit |  | 0 | invoice_fact |  |
| 8 | 这两种有区别吗；图片这种是干的对吧 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 9 | 528105689823；好的谢谢 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 10 | 536023110028；好的谢谢 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 11 | 550995848415；好的谢谢 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 12 | 550995848415；好的谢谢 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 13 | 不好我可要退的哦；杭州桐庐几天到 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 14 | 还行吧；亲皮也不薄呀开壳也挺费劲 | express_policy | no_hit |  | 0 | shipping_config_fact |  |
| 15 | 孩子特别喜欢吃你家里的榴莲干呢 | express_policy | no_hit |  | 0 | shipping_config_fact |  |
| 16 | 买二送一那买四送二嘛；送几份呢 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 17 | 請問這茶刀和養壺筆是小號的嗎 | express_policy | no_hit |  | 0 | shipping_config_fact |  |
| 18 | 来晚了；那个公众号是微信号吗 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 19 | 送脐带贴；能换别的吗同价位的 | gift_policy | no_hit |  | 0 | gift_fact |  |
| 20 | 用得好再大量批嗯嗯；一共五把 | bulk_purchase_policy | no_hit |  | 0 | bulk_purchase_fact |  |
| 21 | 用得好再大量批嗯嗯；一共五把 | bulk_purchase_policy | no_hit |  | 0 | bulk_purchase_fact |  |
| 22 | 抓紧发啊别等到过年了放假了啊 | order_modify_policy | no_hit |  | 0 | order_modify_fact |  |
| 23 | 跟你说个悲剧；我都说了是悲剧 | order_modify_policy | no_hit |  | 0 | order_modify_fact |  |
| 24 | 我也很想买但卡里真的没钱了 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 25 | 在吗哪款是加大尺寸的棉柔巾 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 26 | 为何又要19号能送到阿；行 | express_policy | no_hit |  | 0 | shipping_config_fact |  |
| 27 | 那你说里面有五斤是五袋是吗 | shipping_fee_policy | no_hit |  | 0 | shipping_config_fact |  |
| 28 | 满39送花茶；给个花茶链接 | coupon_policy | no_hit |  | 0 | coupon_fact |  |
| 29 | 满39送花茶；给个花茶链接 | coupon_policy | no_hit |  | 0 | coupon_fact |  |
| 30 | 我只要3个肉其它不要行不行 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 31 | 我只要3个肉其它不要行不行 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 32 | 我看便宜一点小很多么；哦 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 33 | 黑檀茶刀几钱批发；贵了些 | bulk_purchase_policy | no_hit |  | 0 | bulk_purchase_fact |  |
| 34 | 比较慢；嗯防溢乳垫199 | stock_policy | no_hit |  | 0 | stock_fact |  |
| 35 | 用得好再大量批嗯嗯；哦了 | bulk_purchase_policy | no_hit |  | 0 | bulk_purchase_fact |  |
| 36 | 在吗有人吗；那997的呢 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 37 | 在吗有人吗；那997的呢 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 38 | 好了；那就按2959开吧 | invoice_policy | no_hit |  | 0 | invoice_fact |  |
| 39 | 好了；那就按2959开吧 | invoice_policy | no_hit |  | 0 | invoice_fact |  |
| 40 | 在吗；茶刀铜上面有个坑 | shipping_fee_policy | no_hit |  | 0 | shipping_config_fact |  |
| 41 | 你好在吗；唉淡淡的忧伤 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 42 | 买二送一在；都送豆沙吗 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 43 | 一份是六包；一份还送吗 | express_policy | no_hit |  | 0 | shipping_config_fact |  |
| 44 | 亲在吗；买两份送两份吗 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 45 | 可不要忽悠人；也没用 | order_modify_policy | no_hit |  | 0 | order_modify_fact |  |
| 46 | 能扣上吧；怕蒸发水分 | order_modify_policy | no_hit |  | 0 | order_modify_fact |  |
| 47 | 没添加剂吧；够柔软吗 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 48 | 在吗；我换两包湿纸巾 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 49 | 在吗；我换两包湿纸巾 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 50 | 谢谢；现在赶不上了啦 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 51 | 好滴我撤销了撒了；哦 | stock_policy | no_hit |  | 0 | stock_fact |  |
| 52 | 也太慢了点吧；哦谢谢 | order_modify_policy | no_hit |  | 0 | order_modify_fact |  |
| 53 | 也太慢了点吧；哦谢谢 | order_modify_policy | no_hit |  | 0 | order_modify_fact |  |
| 54 | 亲在吗；他们太慢了 | express_policy | no_hit |  | 0 | shipping_config_fact |  |
| 55 | 在没；我用汇通重庆 | express_policy | no_hit |  | 0 | shipping_config_fact |  |
| 56 | 拍好了收藏呢；对的 | gift_policy | no_hit |  | 0 | gift_fact |  |
| 57 | 拍好了收藏呢；对的 | gift_policy | no_hit |  | 0 | gift_fact |  |
| 58 | 这榴莲干好吃吗；好 | promotion_policy | no_hit |  | 0 | promotion_fact |  |
| 59 | 在；完事了谢谢你啦 | coupon_policy | no_hit |  | 0 | coupon_fact |  |
| 60 | 在；完事了谢谢你啦 | coupon_policy | no_hit |  | 0 | coupon_fact |  |
| 61 | 在吗；你家有围兜吗 | invoice_policy | no_hit |  | 0 | invoice_fact |  |
| 62 | 在吗；你家有围兜吗 | invoice_policy | no_hit |  | 0 | invoice_fact |  |
| 63 | 核桃多大；哦谢谢亲 | product_qa_policy | no_hit |  | 0 | product_fact |  |
| 64 | 在吗；之前就是9元 | order_modify_policy | no_hit |  | 0 | order_modify_fact |  |
| 65 | 在吗；之前就是9元 | order_modify_policy | no_hit |  | 0 | order_modify_fact |  |
| 66 | 521521942026你好发什么快递；“让我们一起清凉一夏”为回馈广大亲们的支持屹茗堂特精选1000罐花茶凡在全场购物满39元即赠花茶一罐赠完为止领取方式亲们挑选自己喜爱的花茶并与所购商品一同拍下联 | promotion_policy | scene_mismatch | express_policy | 79.0 | promotion_fact |  |
| 67 | 您好遇到问题请详细描述由于用户很多可能会稍后给您解答请亲们见谅；亲您的这个一口价是6元您可以设置满2件减3元不要勾选上不封顶即可那么买家买下2件的价格就是66-3=9元购买3件就是666-3=15元 | promotion_policy | scene_mismatch | quality_issue | 27.0 | promotion_fact |  |
| 68 | 稍等；亲海报全屏效果宽度是1920高度是无限制的1920宽度是在各个显示器都显示全屏效果的所以您海报内容是要集中做在中间950990部分因为不同的显示器是会显示不一样的效果的 | order_modify_policy | scene_mismatch | logistics_policy | 34.0 | order_modify_fact |  |
| 69 | 稍等；亲海报全屏效果宽度是1920高度是无限制的1920宽度是在各个显示器都显示全屏效果的所以您海报内容是要集中做在中间950990部分因为不同的显示器是会显示不一样的效果的 | order_modify_policy | scene_mismatch | logistics_policy | 34.0 | order_modify_fact |  |
| 70 | 核桃什么时候到我同时拍的一个发了一个还没发好奇怪发的那个快递信息也中断了问了也没答复我等着送人的还不到我就不要了；嗯希望这次不是石沉大海前几次也都说帮我查最终连回音都没有 | express_policy | scene_mismatch | return_exchange | 57.0 | shipping_config_fact |  |
| 71 | 核桃什么时候到我同时拍的一个发了一个还没发好奇怪发的那个快递信息也中断了问了也没答复我等着送人的还不到我就不要了；嗯希望这次不是石沉大海前几次也都说帮我查最终连回音都没有 | express_policy | scene_mismatch | return_exchange | 57.0 | shipping_config_fact |  |
| 72 | 货在你们自己手上发货是你们自己发；你上面讲的话完全是忽悠我的我都没有跟你讲多少因为是第4天晚上了你还这么忽悠我太气人了一般的在网上我不喜欢说人的你自己也好好想想这事 | express_policy | scene_mismatch | logistics_policy | 21.0 | shipping_config_fact |  |
| 73 | 我发你的图看到了吗这是你们的图我的明显是红木其他的都对颜色也一样；我刚好一套黑檀的叫你们补发我又退的话你们太亏要不我买多一支茶针你们在补发我一个大号黑檀茶笔可以不 | bulk_purchase_policy | scene_mismatch | refund_policy | 23.0 | bulk_purchase_fact |  |
| 74 | 我发你的图看到了吗这是你们的图我的明显是红木其他的都对颜色也一样；我刚好一套黑檀的叫你们补发我又退的话你们太亏要不我买多一支茶针你们在补发我一个大号黑檀茶笔可以不 | bulk_purchase_policy | scene_mismatch | refund_policy | 23.0 | bulk_purchase_fact |  |
| 75 | 发过霉一样；牌子是怎么做起来卖这些烂核桃能长久吗早扔了我拉了3次我两个明友吃了多也拉了吃几个没事吃了10几个等半时就拉我也不会为这点钱黑你希望你们检查质量 | coupon_policy | scene_mismatch | logistics_policy | 17.0 | coupon_fact |  |
| 76 | 发过霉一样；牌子是怎么做起来卖这些烂核桃能长久吗早扔了我拉了3次我两个明友吃了多也拉了吃几个没事吃了10几个等半时就拉我也不会为这点钱黑你希望你们检查质量 | coupon_policy | scene_mismatch | logistics_policy | 17.0 | coupon_fact |  |
| 77 | 剛查到是假簽收淘寶海外倉查不到說他們未收到；說麻煩連續賣家問快遞公司提供簽收面單的圖片進行核實處理說麻煩聯繫賣家問快遞公司提供簽收面單的圖片進行核實處理 | order_modify_policy | scene_mismatch | logistics_policy | 43.0 | order_modify_fact |  |
| 78 | 13422170743768063我这一单东西给我运到哪去了昨天应该到的今天还没到这会儿看见预估说要7号才能到前次买不是很正常吗第二天就到了什么情况 | express_policy | scene_mismatch | return_exchange | 38.0 | shipping_config_fact |  |
| 79 | 电话多少邮政电话我这里看不到我在等送人去的晕回话急回话你说昨天电话打通的电话给我什么意思在等货大姐7号今天11号；晚点用会忘了现在的事马上安排 | express_policy | scene_mismatch | quality_issue | 57.0 | shipping_config_fact |  |
| 80 | 借口；我又不是吃一次我不知道奶油味是什么样孑吗我从不吃原味的别人家都油亮黄色的一句对不起都不说还强词夺理你一个客服吃了多少核桃说的很懂样孑 | coupon_policy | scene_mismatch | quality_issue | 34.0 | coupon_fact |  |
| 81 | 就是我之前确认收货后申请退款的刚刚截图也给你们看了退款中这三个字看到了么；快递你看下11号就已经签收了今天几号了那你那边看不到怎么处理呢 | coupon_policy | scene_mismatch | logistics_policy | 140.0 | coupon_fact |  |
| 82 | 你好在吗；之前有一家的发的韵达也是龙武这里没有韵达到哨冲就打电话给我了叫我去哨冲拿我说我地址是龙武然后他说到龙武要加5元我怕这个也会这样 | express_policy | scene_mismatch | gift_policy | 21.0 | shipping_config_fact |  |
| 83 | 怎么回事啊是不是他们把货搞丢了我后买的三只松鼠都到货了本来一直都买的三只松鼠的榴莲干那天看见你家的了就想换个牌子尝尝结果还尝出来麻烦了 | express_policy | scene_mismatch | logistics_policy | 46.0 | shipping_config_fact |  |
| 84 | 你们什么态度吗可是人家跟我打电话说丟了没有拉我不是把号码给你了；我只要把钱赶紧退我好了什么态度吗人家已经说丢了的你们自己跟快递去联系把 | express_policy | scene_mismatch | refund_policy | 29.0 | shipping_config_fact |  |
| 85 | 你们什么态度吗可是人家跟我打电话说丟了没有拉我不是把号码给你了；我只要把钱赶紧退我好了什么态度吗人家已经说丢了的你们自己跟快递去联系把 | express_policy | scene_mismatch | refund_policy | 29.0 | shipping_config_fact |  |
| 86 | 你也是够够的前两天就说到货了会发的一直说补发补发现在又没到货；你已经不是第一次和我说这句话了真的是够够的我估计你过几天又要和我说丢件了 | stock_policy | scene_mismatch | logistics_policy | 32.0 | stock_fact |  |
| 87 | 你也是够够的前两天就说到货了会发的一直说补发补发现在又没到货；你已经不是第一次和我说这句话了真的是够够的我估计你过几天又要和我说丢件了 | stock_policy | scene_mismatch | logistics_policy | 32.0 | stock_fact |  |
| 88 | 这不是江西么我是买到江西啊而且我换地址给别人浙江的也要运费我之前买就不用啊可以改运费吗；对不起我地址错了可以再拍一次么我要寄给浙江的 | promotion_policy | scene_mismatch | order_modify_policy | 69.0 | promotion_fact |  |
| 89 | 我是说前面的标题我在你店买的80抽那些标题就有口手标明就这个款没有标明；因为口手湿巾和不是口手湿巾都会标清楚我都是看标题多好小看后面 | gift_policy | scene_mismatch | logistics_policy | 21.0 | gift_fact |  |
| 90 | 以前没有我们学校有邮政代售点而且以前的话都是有快递员电话我总是会看到谁在派件专门有派件员为我服务；我的订单号快递现在是不是下班了 | express_policy | scene_mismatch | logistics_policy | 45.0 | shipping_config_fact |  |
| 91 | 复制这条信息打开手机淘宝即可看到SHOPNAME婴儿纯棉柔巾宝宝棉柔巾纸巾干湿巾干湿两用巾100抽12包au71n6kMba | gift_policy | scene_mismatch | quality_issue | 14.0 | gift_fact |  |
| 92 | 我的货发错地址了可以帮我调解吗；我定了两次单送给两个客户结果发到一个地方了21号那个单发错了21号的要发河南运费我们这边出 | shipping_fee_policy | scene_mismatch | order_modify_policy | 68.0 | shipping_config_fact |  |
| 93 | 我根本没有打开就在外面拍的是看你们做生意也不容易才会跟你说这些难道你们的东西就是这样吗不要烦我呢购物是开心的我不是找气的 | promotion_policy | scene_mismatch | logistics_policy | 36.0 | promotion_fact |  |
| 94 | 我两次拍为什么不能改价呢我两袋是寄到宁波6袋寄到湖北寄在一起我还得寄一次；宁波这边两袋我出5元可以吗不行就拍6袋寄湖北 | promotion_policy | scene_mismatch | refund_policy | 84.0 | promotion_fact |  |
| 95 | 卖家怎么一直没有快递信息的我8号买的今天已经12号；我没有问下午还是上午到我只需要你们明天发货还叫我退货怎么做客服的 | stock_policy | scene_mismatch | logistics_policy | 66.0 | stock_fact |  |
| 96 | 卖家怎么一直没有快递信息的我8号买的今天已经12号；我没有问下午还是上午到我只需要你们明天发货还叫我退货怎么做客服的 | stock_policy | scene_mismatch | logistics_policy | 66.0 | stock_fact |  |
| 97 | 两个快递同时到的家人没帮我拒签你这边给我补下邮费多的一份我给你寄回去；我在外面怎么联系而且接快递的电话是我家人不是我 | shipping_fee_policy | scene_mismatch | return_exchange | 55.0 | shipping_config_fact |  |
| 98 | 两个快递同时到的家人没帮我拒签你这边给我补下邮费多的一份我给你寄回去；我在外面怎么联系而且接快递的电话是我家人不是我 | shipping_fee_policy | scene_mismatch | return_exchange | 55.0 | shipping_config_fact |  |
| 99 | 卖家怎么一直没有快递信息的我8号买的今天已经12号；你们太不负责任了乱填快递单送人去的一直等着没货不跟我说一声的啊 | stock_policy | scene_mismatch | logistics_policy | 52.0 | stock_fact |  |
| 100 | 我就是看到无添加任何香精才买的买回来一股味道不是骗人吗；那能给我一个解释香味什么情况拿了湿巾的手一个小时还能一股味 | coupon_policy | scene_mismatch | quality_issue | 59.0 | coupon_fact |  |
| 101 | 我就想知道我的快递天天快递拿走了吗还是你们还没发还在你们库里；我是提前那么多天买的意思就是在路上了直接就显示到了吗 | express_policy | scene_mismatch | service_recovery | 39.0 | shipping_config_fact |  |
| 102 | 20065110070079683帮忙看下订单怎么付不了款呢；21622588981079683帮忙改下价格呗谢谢 | promotion_policy | scene_mismatch | logistics_policy | 25.0 | promotion_fact |  |
| 103 | 20065110070079683帮忙看下订单怎么付不了款呢；21622588981079683帮忙改下价格呗谢谢 | promotion_policy | scene_mismatch | logistics_policy | 25.0 | promotion_fact |  |
| 104 | 复制这条信息打开手机淘宝即可看到九都纸皮核桃薄皮奶油味休闲坚果零食炒货年货干果2500g新货v87tmu1QZn | stock_policy | scene_mismatch | logistics_policy | 12.0 | stock_fact |  |
| 105 | 我之前买的都是绵柔巾因为用着还不错才买这么多你家的湿巾囤货给还没出生的宝宝试用了一下居然浮那么多油让我怎么放心用 | gift_policy | scene_mismatch | service_recovery | 27.0 | gift_fact |  |
| 106 | 那我能买一罐柠檬和一罐枸杞再加5元买一罐菊花茶吗；你看一下吧那是不是能都装在一起啊分开有点麻烦的就是送过来的时候 | promotion_policy | scene_mismatch | logistics_policy | 26.0 | promotion_fact |  |
| 107 | 528690173109；你虽然价钱弄底了但是你运费算了5块还不是一样啊上次买没有减价但是包邮算清楚还比这次便宜 | shipping_fee_policy | scene_mismatch | logistics_policy | 38.0 | shipping_config_fact |  |
| 108 | 528690173109；你虽然价钱弄底了但是你运费算了5块还不是一样啊上次买没有减价但是包邮算清楚还比这次便宜 | shipping_fee_policy | scene_mismatch | logistics_policy | 38.0 | shipping_config_fact |  |
| 109 | 花茶要改价是吗我的意思是昨晚我没看见你家有花茶现在见了本来我也要买就不用返现了你一起送我吧一会我拍下你看看改价吧 | promotion_policy | scene_mismatch | logistics_policy | 15.0 | promotion_fact |  |
| 110 | 花茶要改价是吗我的意思是昨晚我没看见你家有花茶现在见了本来我也要买就不用返现了你一起送我吧一会我拍下你看看改价吧 | promotion_policy | scene_mismatch | logistics_policy | 15.0 | promotion_fact |  |
| 111 | 是的亲在下单页面可以任意修改的您先点击立即购买选择10个或者是10个以内点击立即购买在下单的页面可以增加件数的哦 | order_modify_policy | scene_mismatch | refund_policy | 24.0 | order_modify_fact |  |
| 112 | 是的亲在下单页面可以任意修改的您先点击立即购买选择10个或者是10个以内点击立即购买在下单的页面可以增加件数的哦 | order_modify_policy | scene_mismatch | refund_policy | 24.0 | order_modify_fact |  |
| 113 | 我希望是每次都能50支然后这个价因为接下来应该会继续做赠品；好的要检查好每一支的质量哦不然会影响我们以后的合作 | promotion_policy | scene_mismatch | quality_issue | 18.0 | promotion_fact |  |
| 114 | 收获地址就是订单地址不是上面的地址发票内容商品名称明细发票抬头阳光财产保险股份有限公司工会委员会这个是发票内容 | invoice_policy | scene_mismatch | logistics_policy | 43.0 | invoice_fact |  |
| 115 | 收获地址就是订单地址不是上面的地址发票内容商品名称明细发票抬头阳光财产保险股份有限公司工会委员会这个是发票内容 | invoice_policy | scene_mismatch | logistics_policy | 43.0 | invoice_fact |  |
| 116 | 是袋装还是有包装纸盒的；屹茗堂推荐SHOPNAME焦糖味瓜子坚果零食炒货休闲特产葵花籽220g2这么对不上呢 | coupon_policy | scene_mismatch | return_exchange | 15.0 | coupon_fact |  |
| 117 | 在；你好啊我这边是淘宝官方合作伙伴试客联盟-众划算的呢想邀请贵店来我们网站做期活动给我们会员抢购的呢您方便吗 | promotion_policy | scene_mismatch | return_exchange | 21.0 | promotion_fact |  |
| 118 | 无锡是个别人的先到了别人也不好意思说吗我的这里到了吃了有问题我才问的无锡的朋友朋友说是有哈拉味我都不好意思呢 | stock_policy | scene_mismatch | shipping_fee_policy | 24.0 | stock_fact |  |
| 119 | 如果可以的话顺丰快递过来嘉兴离宁波也不远吧确实比较重要所以麻烦你用心帮我去催下明天务必到人呢；很高大概多少 | express_policy | scene_mismatch | quality_issue | 17.0 | shipping_config_fact |  |
| 120 | 如果可以的话顺丰快递过来嘉兴离宁波也不远吧确实比较重要所以麻烦你用心帮我去催下明天务必到人呢；很高大概多少 | express_policy | scene_mismatch | quality_issue | 17.0 | shipping_config_fact |  |
| 121 | 今天不是199了在吗520401029636不在啊520401029636520401029636；那算了 | promotion_policy | scene_mismatch | logistics_policy | 11.0 | promotion_fact |  |
| 122 | 那申请领导的结果呢这样可以吗我也不要优惠券就买17份另送我一份可以吗是否可以请尽快告诉我吧货寄到江苏常州 | coupon_policy | scene_mismatch | logistics_policy | 25.0 | coupon_fact |  |
| 123 | 修改之后我改成2双的我提交订单看了金额的现在你改了我重新付款加起来要高些所以你直接把运费反给我吧我重新拍 | shipping_fee_policy | scene_mismatch | shipping_policy | 57.0 | shipping_config_fact |  |
| 124 | 店家准备帮朋友再拍两把普洱刀上次换了一把有问题的普洱刀原来说好返回换刀运费的一直没见这回能在刀款上扣减吗 | coupon_policy | scene_mismatch | promotion_policy | 47.0 | coupon_fact |  |
| 125 | 店家准备帮朋友再拍两把普洱刀上次换了一把有问题的普洱刀原来说好返回换刀运费的一直没见这回能在刀款上扣减吗 | coupon_policy | scene_mismatch | promotion_policy | 47.0 | coupon_fact |  |
| 126 | 我怀疑她一开始吃的时候就不新鲜；我们好多同事都在你们家里买东西你们不应该卖这样的产品给我们特别是吃的东西 | shipping_fee_policy | scene_mismatch | logistics_policy | 30.0 | shipping_config_fact |  |
| 127 | 亲优惠劵不能领取；满50减25的优惠劵我还没有到两点就在开始领根本就没有过不是上午10点跟下午2点开抢吗 | coupon_policy | scene_mismatch | logistics_policy | 21.0 | coupon_fact |  |
| 128 | 亲优惠劵不能领取；满50减25的优惠劵我还没有到两点就在开始领根本就没有过不是上午10点跟下午2点开抢吗 | coupon_policy | scene_mismatch | logistics_policy | 21.0 | coupon_fact |  |
| 129 | 我是老顾客啦可是我买的时候显示邮费三元；我现在在买的时候夏威夷果显示库存紧张买不了下午再来买吧现在忙了 | shipping_fee_policy | scene_mismatch | logistics_policy | 28.0 | shipping_config_fact |  |
| 130 | 我是老顾客啦可是我买的时候显示邮费三元；我现在在买的时候夏威夷果显示库存紧张买不了下午再来买吧现在忙了 | shipping_fee_policy | scene_mismatch | logistics_policy | 28.0 | shipping_config_fact |  |
| 131 | 那我买你那么多之前也买那么多；假如你现在还是82一箱优惠券一用是不是还要便宜十元我现在只要你再给我五元 | promotion_policy | scene_mismatch | logistics_policy | 30.0 | promotion_fact |  |
| 132 | 上面有邮费价改一下我就拍可否是笔与刀为什么还有运费笔拍了是免运费的同时拍了一茶刀为什么不可免费同时发来 | shipping_fee_policy | scene_mismatch | logistics_policy | 51.0 | shipping_config_fact |  |
| 133 | 上面有邮费价改一下我就拍可否是笔与刀为什么还有运费笔拍了是免运费的同时拍了一茶刀为什么不可免费同时发来 | shipping_fee_policy | scene_mismatch | logistics_policy | 51.0 | shipping_config_fact |  |
| 134 | 新货怎么会这样我妈说有的有有的没有就是那种闷了的味你懂的吧；哦8元应该也够了吧你给我换一包好的可以吗 | coupon_policy | scene_mismatch | logistics_policy | 32.0 | coupon_fact |  |
| 135 | 你不是说1-2天吗现在都什么时候啦你们要是不能发货我就退货啦；速度这么慢没货你们东西也不下架库存也在 | stock_policy | scene_mismatch | service_recovery | 62.0 | stock_fact |  |
| 136 | 亲你们家限购能不能在两件的基础上多加3个肉粽呢下单后修改下价格就好了呀；好的亲什么快递这单是我的哈 | order_modify_policy | scene_mismatch | express_policy | 50.0 | order_modify_fact |  |
| 137 | 最近我拆了一包湿巾感觉有点洗涤剂的味道放在热水里蘸一下再拧干的话热水里会有油花有遇到过这种情况的么 | product_qa_policy | scene_mismatch | return_exchange | 13.0 | product_fact |  |
| 138 | 528105689823亲在吗这个是前一分钟买二减十吗还是不管时间呀买四减20吗同时能使用优惠券吗 | coupon_policy | scene_mismatch | description_mismatch | 24.0 | coupon_fact |  |
| 139 | 528105689823亲在吗这个是前一分钟买二减十吗还是不管时间呀买四减20吗同时能使用优惠券吗 | coupon_policy | scene_mismatch | description_mismatch | 24.0 | coupon_fact |  |
| 140 | 你好这个送的湿巾5包每包多少张；54476844278044265219693这两款有什么不一样吗 | gift_policy | scene_mismatch | refund_policy | 45.0 | gift_fact |  |
| 141 | 是的是的5斤吃不完送点别人吃这种袋袋有吗有的话当天买了给你们留言下你们给我放2个密封袋子可以的吧 | order_modify_policy | scene_mismatch | refund_policy | 15.0 | order_modify_fact |  |
| 142 | 你好；干湿两用的是不是这几款除了大小还有材质区别528690173109547453705709 | promotion_policy | scene_mismatch | logistics_policy | 26.0 | promotion_fact |  |
| 143 | SHOPNAME婴儿湿纸巾宝宝手口湿巾棉柔湿巾纸无香随身25抽12小包点击链接再选择浏览器打开 | gift_policy | scene_mismatch | quality_issue | 10.0 | gift_fact |  |
| 144 | SHOPNAME婴儿湿纸巾宝宝手口湿巾棉柔湿巾纸无香随身25抽12小包点击链接再选择浏览器打开 | gift_policy | scene_mismatch | quality_issue | 10.0 | gift_fact |  |
| 145 | 你这不对我没加棉袜光两包棉柔巾结算的时候就才106加了棉袜还有109减5的优惠券呢怎么还多些了 | coupon_policy | scene_mismatch | return_exchange | 30.0 | coupon_fact |  |
| 146 | 你这不对我没加棉袜光两包棉柔巾结算的时候就才106加了棉袜还有109减5的优惠券呢怎么还多些了 | coupon_policy | scene_mismatch | return_exchange | 30.0 | coupon_fact |  |
| 147 | 没回复你也没给我说啊而且又是我再次找你们你们这也不负责啊我昨天才做的剖腹产还要忍着巨疼天天追件 | express_policy | low_score | refund_policy | 6.0 | shipping_config_fact |  |
| 148 | 不公平呀我买啊2袋可以优惠15元一袋我买3袋反而只能优惠13元一袋了买多了反而单价还高于买少的 | promotion_policy | scene_mismatch | logistics_policy | 13.0 | promotion_fact |  |
| 149 | 亲；刚下单的时候告诉我十五号可以到昨天改成十六号现在又该成十七号到底怎么回事马上都一个星期了 | express_policy | scene_mismatch | refund_policy | 24.0 | shipping_config_fact |  |
| 150 | 怎么这做事明不好吃叫我好评也只有五元十元我也损失比你们多呀；是否叫我家人尝尝吃过了都说不好吃 | coupon_policy | scene_mismatch | quality_issue | 16.0 | coupon_fact |  |
| 151 | 亲可以通过满减活动来实现哦满2件减多少元哦；亲不能的哦打折是总金额的基础上打折那样会更亏的 | promotion_policy | scene_mismatch | quality_issue | 30.0 | promotion_fact |  |
| 152 | 哎哟这看不出什么我上次订的反正你给我的价格是7块酷爱但是好像是大号的你们这是不是最低价了啊 | promotion_policy | scene_mismatch | refund_policy | 51.0 | promotion_fact |  |
| 153 | 那我要5斤的话你给我发2包奶油的3包椒盐的价格还是85还不是一样的吗这样不就有两种口味的啦 | shipping_fee_policy | scene_mismatch | logistics_policy | 15.0 | shipping_config_fact |  |
| 154 | 我定了两次单送给两个客户结果发到一个地方了21号那个单发错了21号的要发河南运费我们这边出 | shipping_fee_policy | scene_mismatch | order_modify_policy | 35.0 | shipping_config_fact |  |
| 155 | 我刚拍了个茶刀用的可以的话我批发问你批发价多少一个我是卖茶的我买了送客人的；大号黑颤木茶刀 | bulk_purchase_policy | scene_mismatch | quality_issue | 15.0 | bulk_purchase_fact |  |
| 156 | 我刚拍了个茶刀用的可以的话我批发问你批发价多少一个我是卖茶的我买了送客人的；大号黑颤木茶刀 | bulk_purchase_policy | scene_mismatch | quality_issue | 15.0 | bulk_purchase_fact |  |
| 157 | 那我怎么买呢我要买4包你要怎么送我麻烦你给我发货哦；意思我买肉松的买榴莲的就送我豆沙的是吗 | promotion_policy | scene_mismatch | logistics_policy | 21.0 | promotion_fact |  |
| 158 | 538872953711你好请问这个多买的话有没有优惠538872953711发中通可以咩 | coupon_policy | scene_mismatch | logistics_policy | 30.0 | coupon_fact |  |
| 159 | 那我8号买不是可以省20元啊；我今天早上才看到的套路我你这也太骗人了吧买5箱不能便宜了啊 | coupon_policy | scene_mismatch | refund_policy | 21.0 | coupon_fact |  |
| 160 | 没有发票吧；过几天也还有优惠吧那我现在拍了不就有了呢那你可以过一个星期再发货么清明的时候 | promotion_policy | scene_mismatch | return_exchange | 26.0 | promotion_fact |  |
| 161 | 我都买过了我意思能不能把优惠给我的哇昨晚拍的5箱减了20元按照那个活动貌似可以减40元哇 | coupon_policy | scene_mismatch | quality_issue | 36.0 | coupon_fact |  |
| 162 | 这次我买来送朋友你们能不能不要打印就是订单上面不能有价格直接发快递不要打印订单；哇真的么 | promotion_policy | scene_mismatch | quality_issue | 47.0 | promotion_fact |  |
| 163 | 怎么回事；不来就退货了昨天都跟你们说了没到帮我看看现在呢还没到都不知道你们还做不做生意的 | express_policy | scene_mismatch | return_exchange | 36.0 | shipping_config_fact |  |
| 164 | 发货那我年前能收到不海南三亚；啊今天16就算5天后发货21发27还不能到么从哪里发货的呢 | coupon_policy | scene_mismatch | logistics_policy | 21.0 | coupon_fact |  |
| 165 | 发票上需把买的每样东西写清楚名称单位数量不能这么写母婴用品1批这样单位是无法报销的谢谢 | invoice_policy | scene_mismatch | logistics_policy | 17.0 | invoice_fact |  |
| 166 | 发票上需把买的每样东西写清楚名称单位数量不能这么写母婴用品1批这样单位是无法报销的谢谢 | invoice_policy | scene_mismatch | logistics_policy | 17.0 | invoice_fact |  |
| 167 | 发票上需把买的每样东西写清楚名称单位数量不能这么写母婴用品1批这样单位是无法报销的谢谢 | invoice_policy | scene_mismatch | logistics_policy | 17.0 | invoice_fact |  |
| 168 | 发票上需把买的每样东西写清楚名称单位数量不能这么写母婴用品1批这样单位是无法报销的谢谢 | invoice_policy | scene_mismatch | logistics_policy | 17.0 | invoice_fact |  |
| 169 | 发票上需把买的每样东西写清楚名称单位数量不能这么写母婴用品1批这样单位是无法报销的谢谢 | invoice_policy | scene_mismatch | logistics_policy | 17.0 | invoice_fact |  |
| 170 | 信息上不是已经从上海发回了吗；又不是我退货造成的是你们自身问题不能等收到货再给退款的啊 | stock_policy | scene_mismatch | logistics_policy | 43.0 | stock_fact |  |
| 171 | 我一共买了119的东西都需要邮费吗；我这边要付款的时候提示有6块钱的运费所以就没有付款 | shipping_fee_policy | scene_mismatch | shipping_policy | 35.0 | shipping_config_fact |  |
| 172 | 我一共买了119的东西都需要邮费吗；我这边要付款的时候提示有6块钱的运费所以就没有付款 | shipping_fee_policy | scene_mismatch | shipping_policy | 35.0 | shipping_config_fact |  |
| 173 | 538832022583这个岂不是超级划算；无纺布不是纯棉的是吧哦哦无纺布是什么材质呀 | product_qa_policy | scene_mismatch | return_exchange | 31.0 | product_fact |  |
| 174 | 538832022583这个岂不是超级划算；无纺布不是纯棉的是吧哦哦无纺布是什么材质呀 | product_qa_policy | scene_mismatch | return_exchange | 31.0 | product_fact |  |
| 175 | 我有几个之前用全棉时代的都比我言起买你家的了没注意嘛搞得啥活动那我不是要等到双11了 | promotion_policy | scene_mismatch | refund_policy | 21.0 | promotion_fact |  |
| 176 | 深圳汇络天下投资基金有限公司；三十份里面有两份地址是不同的其他28份的地址都是一样的 | invoice_policy | scene_mismatch | logistics_policy | 26.0 | invoice_fact |  |
| 177 | 老板那个可以给我处理下退款吗你们没货等了5天了麻烦您款退下我上别家买；好那我就不退了 | stock_policy | scene_mismatch | logistics_policy | 42.0 | stock_fact |  |
| 178 | 我比较着急你得给我加急我着急用赶紧发货；那就百世汇通吧亲你给我备注一下尽快发货加个急 | express_policy | scene_mismatch | shipping_policy | 104.0 | shipping_config_fact |  |
| 179 | 我比较着急你得给我加急我着急用赶紧发货；那就百世汇通吧亲你给我备注一下尽快发货加个急 | express_policy | scene_mismatch | shipping_policy | 104.0 | shipping_config_fact |  |
| 180 | 我是要拍三代的我拍错了拍成一袋了你先帮我退了我重新下单；哦哦好吧那我搞错了不好意思哈 | bulk_purchase_policy | scene_mismatch | order_modify_policy | 78.0 | bulk_purchase_fact |  |
| 181 | 感觉像别人用过的一样盒子也是破的；可是外面的盒子是好的呀为什么里面的感觉被撕开过一样 | express_policy | scene_mismatch | refund_policy | 36.0 | shipping_config_fact |  |
| 182 | 你们是不是有什么问题发货一再推迟昨天又没发你们是不是有什么问题发货一再推迟昨天又没发 | stock_policy | scene_mismatch | logistics_policy | 30.0 | stock_fact |  |
| 183 | 你们太不负责任了乱填快递单送人去的一直等着没货不跟我说一声的啊；明天再不发货怎么办 | express_policy | scene_mismatch | shipping_policy | 113.0 | shipping_config_fact |  |
| 184 | 你们就这样给我的答复吗我十多天没收到货才找你们是应该跟踪一下吧；我不是有具体地址吗 | express_policy | scene_mismatch | logistics_policy | 65.0 | shipping_config_fact |  |
| 185 | 你们就这样给我的答复吗我十多天没收到货才找你们是应该跟踪一下吧；我不是有具体地址吗 | stock_policy | scene_mismatch | logistics_policy | 65.0 | stock_fact |  |
| 186 | 帮忙备注一下吧发货的时候写茶具或者文体不要写茶刀；就是包裹信息上面不要出现刀就行了 | order_modify_policy | scene_mismatch | logistics_policy | 23.0 | order_modify_fact |  |
| 187 | 帮忙备注一下吧发货的时候写茶具或者文体不要写茶刀；就是包裹信息上面不要出现刀就行了 | order_modify_policy | scene_mismatch | logistics_policy | 23.0 | order_modify_fact |  |
| 188 | 在吗亲；哦谢谢了那我再拍点记得明天一早发货哈本周五年会要用的谢谢到货晚了就耽误事了 | coupon_policy | scene_mismatch | logistics_policy | 15.0 | coupon_fact |  |
| 189 | 您好我刚才拍了一个茶刀因为我这边现在没有圆通提醒您一下别发圆通的谢谢啦；那到啥时候 | express_policy | scene_mismatch | return_exchange | 14.0 | shipping_config_fact |  |
| 190 | 亲这次双十二便宜点嘛下回涨了就涨了吧之前你们跟我说过都可以299的就这次把通融一下 | promotion_policy | scene_mismatch | return_exchange | 9.0 | promotion_fact |  |
| 191 | 店家我想再买五包大核桃能原来价82元一包买给我吗我可是买了你们很多了也算老客户了吧 | promotion_policy | low_score | order_modify_policy | 6.0 | promotion_fact |  |
| 192 | 订多少个可以刻字啊我去年在你们店里定了好多的你可以查记录的；那大的是多大小的是多少 | promotion_policy | scene_mismatch | logistics_policy | 19.0 | promotion_fact |  |
| 193 | 在吗；如果今天不能发货这边快递关门了能不能确认下今天能否发货如果不能发申请订单取消 | express_policy | scene_mismatch | order_modify_policy | 72.0 | shipping_config_fact |  |
| 194 | 在吗；如果今天不能发货这边快递关门了能不能确认下今天能否发货如果不能发申请订单取消 | express_policy | scene_mismatch | order_modify_policy | 72.0 | shipping_config_fact |  |
| 195 | 538832022583；之前我买纯棉那款包邮三亚了买无纺布这款12包的能包三亚吗 | product_qa_policy | scene_mismatch | return_exchange | 12.0 | product_fact |  |
| 196 | 538405926243有货吗椒盐味的送夹子吗538405926243在吗人呢；哦 | coupon_policy | scene_mismatch | return_exchange | 9.0 | coupon_fact |  |
| 197 | 520401029636怎么不是199546487395690这个不是买二减五元吗 | coupon_policy | scene_mismatch | logistics_policy | 19.0 | coupon_fact |  |
| 198 | 他没有打电话给我发短信让我去取；不方便因为我在家不在那那还是不要了可以申请退款吗 | shipping_fee_policy | scene_mismatch | quality_issue | 84.0 | shipping_config_fact |  |
| 199 | 以前吃原味的没这种情况；前段时间看新闻说核桃用化学成分的水泡过的不知道是不是真的 | product_qa_policy | scene_mismatch | logistics_policy | 39.0 | product_fact |  |
| 200 | 以前吃原味的没这种情况；前段时间看新闻说核桃用化学成分的水泡过的不知道是不是真的 | product_qa_policy | scene_mismatch | logistics_policy | 39.0 | product_fact |  |
