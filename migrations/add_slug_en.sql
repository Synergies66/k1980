-- K1980 英文 Slug 数据库迁移
-- 在 Supabase SQL Editor 中运行此文件
-- ============================================================

-- 1. 为 articles 表添加 slug_en 字段
ALTER TABLE articles
  ADD COLUMN IF NOT EXISTS slug_en TEXT;

-- 2. 创建唯一索引（保证 slug 不重复）
CREATE UNIQUE INDEX IF NOT EXISTS articles_slug_en_unique
  ON articles (slug_en)
  WHERE slug_en IS NOT NULL;

-- 3. 创建普通索引（加速查询）
CREATE INDEX IF NOT EXISTS articles_slug_en_idx
  ON articles (slug_en);

-- 4. 验证字段是否添加成功
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'articles'
  AND column_name = 'slug_en';

-- 5. 查看当前 slug_en 填充情况（迁移后用来确认进度）
SELECT
  COUNT(*) AS total,
  COUNT(slug_en) AS has_slug_en,
  COUNT(*) - COUNT(slug_en) AS missing_slug_en
FROM articles;
