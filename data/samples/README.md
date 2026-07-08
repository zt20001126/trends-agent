# Amazon Reviews 2023 MVP 样本数据说明

第一阶段样本类目选择：

- Electronics
- Wearable Technology
- Activity Trackers
- Smartwatches

## products_sample.json

商品 metadata 样本使用 JSON 数组，每个元素建议包含：

```json
{
  "parent_asin": "B001",
  "title": "Smart Fitness Band with Heart Rate Monitor",
  "description": "Waterproof smart fitness band with sleep tracking and app sync.",
  "brand": "FitNova",
  "categories": ["Electronics", "Wearable Technology", "Activity Trackers"],
  "price": 39.99
}
```

字段说明：

- `parent_asin`：商品父 ASIN，用于和评论样本关联。
- `title`：商品标题，用于关键词匹配。
- `description`：商品描述，用于关键词匹配。
- `brand`：品牌名称，用于品牌分布统计。
- `categories`：类目路径，用于类目分布统计。
- `price`：商品价格，用于价格区间和利润潜力估算。

## reviews_sample.json

评论样本使用 JSON 数组，每个元素建议包含：

```json
{
  "parent_asin": "B001",
  "title": "Battery is disappointing",
  "text": "The smart fitness band works but the battery drains fast and charging is slow.",
  "rating": 2
}
```

字段说明：

- `parent_asin`：关联商品父 ASIN。
- `title`：评论标题，用于关键词匹配。
- `text`：评论正文，用于痛点提取。
- `rating`：评论星级，`rating <= 3` 视为低星评论。

## 数据体积约束

仓库只提交小样本 JSON。全量 Amazon Reviews 2023、parquet、csv、jsonl 等大文件不得提交到 git，应放在本地 `data/imports` 或缓存目录中。
