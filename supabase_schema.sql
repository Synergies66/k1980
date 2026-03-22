-- ============================================================
-- k1980.app 新闻系统 SQL v3.0
-- 8分类：时事 科技 财经 移民 教育 生活 旅游 游戏
-- 全天不间断发布支持
-- ============================================================

-- 全新建表
CREATE TABLE IF NOT EXISTS news_articles (
    id              BIGSERIAL PRIMARY KEY,
    guid            VARCHAR(64)  UNIQUE NOT NULL,
    title           TEXT         NOT NULL,
    summary         TEXT,
    content         TEXT,
    tags            TEXT[]       DEFAULT '{}',
    category        VARCHAR(20)  NOT NULL
                    CHECK (category IN (
                        '时事','科技','财经','移民','教育','生活','旅游','游戏',
                        '新西兰本地','澳洲本地','加拿大本地','美国本地','英国本地',
                        '日本本地','韩国本地','新加坡本地','马来西亚本地','印尼本地'
                    )),
    source_name     VARCHAR(100),
    original_url    TEXT,
    original_title  TEXT,
    is_published    BOOLEAN      DEFAULT TRUE,
    view_count      INTEGER      DEFAULT 0,
    published_at    TIMESTAMPTZ  DEFAULT now(),
    created_at      TIMESTAMPTZ  DEFAULT now()
);

-- 已有旧表则用此脚本升级约束（跳过建表，单独执行这段）：
/*
DO $$
BEGIN
  EXECUTE (
    SELECT 'ALTER TABLE news_articles DROP CONSTRAINT ' || conname
    FROM pg_constraint
    WHERE conrelid = 'news_articles'::regclass AND contype = 'c'
    AND conname LIKE '%category%' LIMIT 1
  );
  ALTER TABLE news_articles ADD CONSTRAINT news_articles_category_check
    CHECK (category IN ('时事','科技','财经','移民','教育','生活','旅游','游戏'));
END $$;
*/

-- 索引
CREATE INDEX IF NOT EXISTS idx_news_category  ON news_articles (category);
CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles (is_published, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_tags      ON news_articles USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_news_created   ON news_articles (created_at DESC);

-- RLS
ALTER TABLE news_articles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "public_read_published" ON news_articles;
CREATE POLICY "public_read_published"
    ON news_articles FOR SELECT USING (is_published = TRUE);

DROP POLICY IF EXISTS "service_role_all" ON news_articles;
CREATE POLICY "service_role_all"
    ON news_articles FOR ALL TO service_role
    USING (TRUE) WITH CHECK (TRUE);

-- 浏览次数自增
CREATE OR REPLACE FUNCTION increment_view_count(article_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE news_articles SET view_count = view_count + 1 WHERE id = article_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 统计视图（8分类）
CREATE OR REPLACE VIEW news_category_stats AS
SELECT
    category,
    COUNT(*) FILTER (WHERE is_published)                               AS published,
    MAX(created_at)                                                    AS latest_at,
    COUNT(*) FILTER (WHERE is_published AND created_at > now() - interval '24 hours') AS last_24h,
    COUNT(*) FILTER (WHERE is_published AND created_at > now() - interval '1 hour')   AS last_1h
FROM news_articles
GROUP BY category
ORDER BY published DESC;
