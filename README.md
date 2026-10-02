# GradAtlas

**GradAtlas — 面向留学申请的硕士项目智能检索与 RAG 问答系统**

## 当前进度（2026-09-30）

结构化查询和入学季详情已经可用。数据库里有 246 所学校、363 个项目、54 条入学季，其中 52 条已核对，2 条仍是样例（慕尼黑工业大学 MSc Informatics、赫尔辛基大学 Master's Programme in Computer Science）。

第一版 RAG 先做斯坦福大学 MS Computer Science、2027 年 9 月入学（入学季 2）。该季已核对，而且种子里已经记下 4 个官网地址。这 4 页已经抓取、解析并切块：4 份原文、34 个片段。原始网页按 `国家代码/学校 slug/项目 slug/入学年/` 放在 `app/backend/data/snapshots`。重复执行导入会复用同一内容，不会再插入。

问答接口是 `POST /intakes/{id}/ask`。它只检索该入学季、该年份的片段。样例入学季和没有原文的入学季会直接说明，不会拿别的项目来回答。对话使用 DeepSeek（`DEEPSEEK_API_KEY`、`CHAT_MODEL`，默认 `deepseek-flash`）。嵌入使用 `.env` 里的 `EMBEDDING_*`。当前模型是阿里云百炼 `text-embedding-v4`，请求时指定 1536 维，每批最多 10 条。入学季 2 的 34 个片段已有向量。问 GRE 时，回答依据计算机系 FAQ：MS 申请者不需要、也不考虑 GRE，并附上检索到的原文。入学季 4 会说明仍是样例；没有原文的入学季不会返回斯坦福片段。重复执行嵌入不会新增向量。

同一份网页按内容哈希只存一次。重复执行导入不会再插入同一快照。招生种子如果再次运行，只会停用不再列出的网址，不会删掉已经入库的原文。

### 启动

在 `app/backend` 目录：

```bash
docker compose up -d --build backend
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.seed.ingest_stanford_mscs
docker compose run --rm backend python -m app.rag.index --intake 2
```

浏览页是 <http://127.0.0.1:8000/browse>。原文快照写在容器里的 `/app/data/snapshots`，对应本机 `app/backend/data/snapshots`（已在 `.gitignore` 中忽略）。

### 下一步

1. 再选 5–8 个已核对项目，按同样流程抓取、切块、嵌入。大规模补录继续暂停。

## 1. 项目背景

留学申请信息通常分散在大学官网、学院网站、招生简章 PDF、FAQ、课程页面、研究室网站等不同来源中。

对于申请者而言，真正困难的并不是“找不到学校”，而是：

- 招生要求分散在多个页面或 PDF 中
- 不同年份的招生政策可能发生变化
- 同一大学不同项目要求差异很大
- GPA、语言、GRE、推荐信、教授联系、入学考试等条件难以统一比较
- PDF 和网页中包含大量非结构化信息
- 通用搜索引擎很难直接回答复杂的组合条件问题
- LLM 在没有可靠来源的情况下容易产生幻觉

GradAtlas 的目标是构建一个面向留学申请场景的智能信息系统，将分散的官方信息采集、结构化、索引，并通过 RAG 和结构化查询为用户提供可追溯的答案。

第一阶段主要覆盖：

**欧洲大陆 + 日本的 Computer Science / AI / Data Science / Informatics 等相关硕士项目。**

---

# 2. 核心目标

GradAtlas 不是简单的“留学 ChatGPT”，而是一个：

**Structured Search + RAG + LLM**

结合的留学信息检索系统。

系统需要能够同时处理两类问题。

### 结构化查询

例如：

> 找出欧洲学费低于 5000 欧元、不要求 GRE、英语授课的计算机硕士。

这类问题应该主要通过结构化数据库完成筛选。

涉及字段包括：

- 国家
- 学校
- 项目
- 学位
- 学费
- GPA 要求
- IELTS / TOEFL
- GRE
- 推荐信
- 是否需要教授联系
- 是否有入学考试
- 申请截止日期
- 入学时间
- 授课语言

---

### 非结构化知识查询

例如：

> 东京大学创意信息学修士的入学考试具体考什么？

> 为什么某项目不适合跨专业申请？

> 某项目对本科课程背景有什么要求？

这类问题需要从：

- 招生简章
- 项目官网
- FAQ
- 课程要求
- 学院页面
- 官方 PDF

中检索相关内容，再由 LLM 基于检索结果回答。

---

# 3. 系统核心架构

整体流程：

```text
大学官网 / 项目官网 / 招生简章 PDF / FAQ
                    │
                    ▼
                Data Crawler
                    │
                    ▼
           Parser / Data Cleaning
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
 Structured Database     Document Store
                               │
                               ▼
                         Chunking
                               │
                               ▼
                          Embedding
                               │
                               ▼
                          Vector DB

```

用户查询阶段：

```text
                     User Query
                         │
                         ▼
                    Query Router
                    /          \
                   /            \
          Structured Query     RAG Query
                 │                 │
               SQL            Retriever
                 │                 │
                 │              Reranker
                 │                 │
                 └────────┬────────┘
                          ▼
                         LLM
                          │
                          ▼
              Answer + Source Citation

```

---

# 4. 数据设计

系统的数据分为两部分。

## Structured Data

存储适合筛选和比较的信息。

例如：

```text
University

Program

Country

Degree

Field

Tuition

ApplicationDeadline

ApplicationRound

IELTS

TOEFL

GRE

GPARequirement

RecommendationLetter

ProfessorContact

EntranceExam

Interview

TeachingLanguage

```

---

## Unstructured Knowledge

保存官方原始文档内容，例如：

- Admission Guidelines
- Program Description
- FAQ
- Curriculum
- Eligibility Requirements
- Entrance Examination Information
- Department Website
- Laboratory / Professor Information

文档经过：

```text
Document
↓
Parse
↓
Clean
↓
Chunk
↓
Embedding
↓
Vector Database

```

---

# 5. Metadata 设计

GradAtlas 一个重要特点是处理留学信息的**时间版本问题**。

同一个项目：

```text
2025 Admission
2026 Admission
2027 Admission

```

可能存在不同要求。

因此每个 Document / Chunk 需要携带 Metadata，例如：

```json
{
  "university": "University of Tokyo",
  "department": "Graduate School of Information Science and Technology",
  "program": "Creative Informatics",
  "country": "Japan",
  "admission_year": 2027,
  "document_type": "admission_guideline",
  "language": "ja",
  "source_url": "...",
  "updated_at": "2026-09-10"
}

```

检索阶段应优先使用：

**Metadata Filtering + Semantic Search**

而不是单纯 Vector Similarity。

---

# 6. 典型用户问题

系统最终应该能够回答：

### 单项目查询

> ETH CS Master 是否要求 GRE？

> 东京大学情报理工修士考试考什么？

> TU Delft Computer Science 的英语要求是什么？

---

### 条件搜索

> 欧洲有哪些学费低于 5000 欧的英语授课 CS Master？

> 找出不要求 GRE 且接受 IELTS 的项目。

> 日本有哪些情报类修士存在冬季招生？

---

### 项目比较

> Aalto 和 KTH 的 CS Master 对中国本科生的申请要求有什么区别？

> 东京大学和东京科学大学的信息类修士考试方式有什么区别？

---

### 自然语言条件查询

例如用户输入：

> 我是中国计算机本科，GPA 3.3，IELTS 7.0，不会德语，希望一年学费不超过 1 万欧，想找欧洲的 CS/AI Master。

系统首先提取条件：

```text
Bachelor Major = CS
GPA = 3.3
IELTS = 7.0
Teaching Language = English
Tuition <= 10000 EUR
Region = Europe
Field = CS / AI

```

然后：

```text
Structured Filtering
↓
Candidate Programs
↓
RAG Retrieval
↓
读取每个项目官方申请要求
↓
LLM 总结
↓
结果 + 原始来源

```

---

# 7. RAG Pipeline

RAG 部分至少需要实现：

```text
Document Ingestion

→ Parsing

→ Cleaning

→ Chunking

→ Metadata Extraction

→ Embedding

→ Vector Storage

→ Query Processing

→ Metadata Filtering

→ Semantic Retrieval

→ Reranking

→ Context Construction

→ LLM Generation

→ Citation

```

后续可以研究不同 Chunking Strategy 对检索结果的影响。

例如：

- Fixed-size Chunking
- Recursive Chunking
- Heading-based Chunking
- Document Structure-aware Chunking

---

# 8. Query Router

系统不能把所有问题都交给 RAG。

需要判断用户问题属于：

```text
Structured Query
RAG Query
Hybrid Query

```

例如：

> 学费低于 5000 欧的学校有哪些？

属于 Structured Query。

---

> 东京大学创情考试考什么？

属于 RAG Query。

---

> 找出欧洲学费低于 5000 欧、不要求 GRE，而且适合 CS 本科申请的 AI Master。

属于 Hybrid Query：

```text
SQL Filtering
+
RAG Retrieval
+
LLM

```

Query Router 是 GradAtlas 的核心功能之一。

---

# 9. Citation

系统生成的答案必须尽量附带原始来源。

例如：

```text
Tokyo University Creative Informatics

Entrance Examination:
- Mathematics
- Programming
- Interview

Source:
2027 Admission Guidelines
Page 12
University of Tokyo

```

目标是：

**用户可以验证 LLM 的每个重要结论。**

而不是单纯相信模型输出。

---

# 10. RAG Evaluation

GradAtlas 需要设计自己的测试集，而不是只判断“看起来回答得不错”。

建立一组 Ground Truth Questions，例如：

```text
Q1 ETH CS Master 是否要求 GRE？

Q2 东京大学创情修士考试科目是什么？

Q3 Aalto CS Master IELTS 最低要求是什么？

Q4 哪些项目学费低于 5000 欧且不要求 GRE？

Q5 日本哪些信息类硕士存在冬季考试？

```

评估指标可以包括：

```text
Retrieval Recall

Retrieval Precision

Answer Correctness

Citation Correctness

Faithfulness

Hallucination Rate

```

通过 evaluation 比较：

```text
不同 embedding model

不同 chunk size

Top-K

Hybrid Search

Reranker

Metadata Filtering

```

对结果的影响。

---

# 11. MVP 范围

第一版不要试图覆盖全球所有大学。

MVP 控制在：

**日本 + 欧洲大陆**

领域：

**Computer Science / AI / Data Science / Informatics**

学校数量：

**20–30 所大学**

项目数量：

**50–100 个 Master Program**

优先保证：

```text
数据准确性
>
检索准确性
>
Citation
>
系统架构
>
项目数量

```

而不是单纯追求数据规模。

---

# 12. 第一阶段不做的事情

暂时不重点实现：

- 根据 GPA 给用户计算“录取概率”
- 自动判断“保底 / 冲刺”
- 爬取大量小红书、知乎等经验帖
- 覆盖全球所有专业
- 自动替用户选择学校
- 复杂的推荐算法

第一阶段的核心是：

**可靠的信息检索系统，而不是留学推荐算法。**

---

# 13. 项目学习目标

通过 GradAtlas 系统学习并实践：

### Backend

- REST API
- FastAPI
- ORM
- PostgreSQL
- Database Design
- Async Programming
- Caching

### Data Engineering

- Web Crawling
- HTML Parsing
- PDF Parsing
- ETL
- Data Cleaning
- Metadata Extraction
- Data Versioning

### AI / RAG

- Embedding
- Vector Database
- Chunking
- Semantic Search
- Hybrid Search
- Metadata Filtering
- Reranking
- Prompt Engineering
- Citation
- RAG Evaluation

### System Design

- Query Router
- Structured + Unstructured Retrieval
- Data Pipeline
- Retrieval Pipeline
- Update Strategy
- Observability
- Evaluation Pipeline

---

# 14. 最终项目定位

GradAtlas 最终不是一个简单的：

> ChatGPT + Vector Database Demo

而是一个完整的：

> **面向留学申请领域的结构化搜索与 Retrieval-Augmented Generation 信息系统。**

核心工程问题包括：

1. 如何从不同大学网站和 PDF 中采集异构数据
2. 如何把留学信息同时表示成结构化数据和非结构化文档
3. 如何处理不同年份招生政策
4. 如何根据用户问题选择 SQL、RAG 或 Hybrid Retrieval
5. 如何提高 Retriever 的准确率
6. 如何减少 LLM Hallucination
7. 如何为答案提供可验证 Citation
8. 如何通过 Evaluation 系统衡量 RAG 效果

项目开发过程中，应优先理解这些问题背后的原理，而不是单纯依赖 AI Agent 自动生成代码。
## 批量收集官网 HTML / PDF

```bash
cd app/backend
docker compose exec backend python -m app.ingest.collect --dry-run          # 只看会抓什么
docker compose exec backend python -m app.ingest.collect --university university-of-tokyo
docker compose exec backend python -m app.ingest.collect                    # 全部
```

- 只抓库里已有的地址：`sources`、`programs.official_url`、`app/seed/source_urls.csv`（列：`university_slug,program_slug,url,source_type`）。
- 遵守 robots.txt，同一站点默认每 2 秒一次请求，超过 50MB、登录页、拦截页会跳过并记入报告。
- 文件按 `国家/学校/项目/年份/` 存入 `data/snapshots`，相同内容不重复保存，重复运行安全；已抓过的默认跳过，`--refresh` 重新检查更新。
- 报告在 `data/snapshots/reports/`：`collect-时间.csv`（每个地址的结果）、`missing-urls.csv`（全量运行时列出还没有任何地址的项目）。
- 这一步只保存原文件，不解析、不嵌入；PDF 解析尚未实现。
