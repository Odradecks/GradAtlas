"""Separate clients for embeddings and DeepSeek chat."""

from __future__ import annotations

from collections.abc import Iterator

from openai import OpenAI

from app.config import settings


class ModelConfigError(RuntimeError):
    """Raised when a real model call cannot be made."""


def require_embedding() -> None:
    if not settings.embedding_api_key.strip():
        raise ModelConfigError(
            "缺少 EMBEDDING_API_KEY。DeepSeek 只负责回答，嵌入需要另一个 1536 维模型。"
            "当前没有写入向量，也没有生成回答。"
        )


def require_chat() -> None:
    if not settings.deepseek_api_key.strip():
        raise ModelConfigError(
            "缺少 DEEPSEEK_API_KEY。当前没有生成回答。"
        )


def embedding_client() -> OpenAI:
    require_embedding()
    return OpenAI(api_key=settings.embedding_api_key, base_url=settings.embedding_base_url)


def chat_client() -> OpenAI:
    require_chat()
    return OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    client = embedding_client()
    expected = settings.embedding_dimensions
    vectors: list[list[float]] = []
    # Some compatible endpoints, including DashScope text-embedding-v4, default to
    # 1024 dimensions and accept at most 10 inputs per call.
    for start in range(0, len(texts), 10):
        batch = texts[start : start + 10]
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
            dimensions=expected,
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        batch_vectors = [list(item.embedding) for item in ordered]
        if len(batch_vectors) != len(batch) or any(len(vector) != expected for vector in batch_vectors):
            raise ModelConfigError(
                f"嵌入模型 {settings.embedding_model} 没有返回 {len(batch)} 条 {expected} 维向量，已拒绝写入。"
            )
        vectors.extend(batch_vectors)
    return vectors


_CITE = "每句依据原文的话，在句末用 [1]、[2] 这样的编号标出对应片段，只用给定的片段编号。"

INTAKE_SYSTEM = (
    "你只根据给定的官网原文回答，回答正文必须是中文。"
    "先用一两句中文给出结论，不要先贴英文，也不要整段照抄原文。"
    "需要强调时只用 **加粗**，需要分点时只用以 - 开头的短列表。不要输出 HTML。"
    "学校名、项目名、考试名可以保留英文，其余说明都写成中文。"
    "问题只针对标明的这一个项目和入学季。"
    "项目自己的页面已经写明的条件，按项目页面回答；全校通用页面只说各项目自行决定时，不要用它否定项目页面。"
    "原文没有写明的申请条件，要直接用中文说明资料没有写明。"
    "不要把空缺说成不要求，不要使用片段之外的学校、项目或年份。"
    + _CITE
)

COMPARE_SYSTEM = (
    "你只根据给定的各项目官网片段比较这些项目，回答正文必须是中文。"
    "先用一两句中文概括主要差别，再按项目分点说明。"
    "每个项目只使用该项目标题下的片段。某个项目的片段没有写到的条件，要写「资料没有写明」。"
    "不要用其他项目的原文补上，不要把空缺说成不要求，不要使用片段之外的学校、项目或年份。"
    "需要强调时只用 **加粗**，需要分点时只用以 - 开头的短列表。不要输出 HTML。"
    "学校名、项目名、考试名可以保留英文，其余说明都写成中文。"
    + _CITE
)


def _messages(system: str, prompt: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]


def complete(system: str, prompt: str) -> str:
    response = chat_client().chat.completions.create(
        model=settings.chat_model,
        temperature=0.1,
        messages=_messages(system, prompt),
        extra_body={"thinking": {"type": "disabled"}},
    )
    message = response.choices[0].message.content
    return (message or "").strip()


def stream_complete(system: str, prompt: str) -> Iterator[str]:
    stream = chat_client().chat.completions.create(
        model=settings.chat_model,
        temperature=0.1,
        messages=_messages(system, prompt),
        extra_body={"thinking": {"type": "disabled"}},
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        text = chunk.choices[0].delta.content
        if text:
            yield text
