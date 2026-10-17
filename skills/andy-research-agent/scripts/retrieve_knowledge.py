#!/usr/bin/env python3
"""Search reviewed cards, not the raw topic index. Local, read-only, stdlib only."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

DEFAULT_ROOT = Path(__file__).resolve().parents[3] / 'knowledge'
SOURCES = (
    ('method_rule', ('methods/verified-rules.json',)),
    # Never fall back to the withdrawn v2 cards: their original source IDs were incorrect.
    ('topic_reading', ('retrieval/topic-reading-cards.jsonl', 'corpus/current-source-reading-cards.jsonl',
                       'corpus/model-reading-cards.jsonl', 'corpus/model-reading-cards.json',
                       'corpus/continuation/main-read-20261017.json')),
    ('video_text', ('video-text/reviewed-knowledge-cards.jsonl', 'video-text/reviewed-knowledge-cards.json')),
    ('article_reading', ('retrieval/article-reading-cards.jsonl',)),
    ('comment_partial_context', ('enrichment/cards/andy-deep-comment-cards.jsonl',)),
)
SOURCE_NOTES = {
    'method_rule': '局部原文核对的方法规则；不等于全主题、外链或外部科学事实已核验。',
    'topic_reading': '已阅读主题卡；以每卡实际阅读范围为限，不代表全语料已深读。',
    'video_text': '带噪字幕批次阅读卡；回查完整批次及讲者，不能冒充裸视频转写或独立实证。',
    'article_reading': '已读本地嵌入文章版本；远端独立文章版本、图片和外链未据此核验。与主题重叠不能当作独立证据。',
    'comment_partial_context': '评论原文字段已读，但原主题上下文可能未关联；不能直接提升为完整Andy方法。',
}


def text(value):
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return '\n'.join(text(x) for x in value)
    if isinstance(value, dict):
        return '\n'.join(f'{k}: {text(v)}' for k, v in value.items())
    return str(value)


def first(row, *names):
    for name in names:
        value = row.get(name)
        if value is not None and value != '' and value != []:
            return value
    return None


def load_rows(path):
    if path.suffix == '.jsonl':
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    else:
        payload = json.loads(path.read_text())
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            for key in ('rules', 'cards', 'items', 'reading_cards'):
                if isinstance(payload.get(key), list):
                    rows = payload[key]
                    break
            else:
                raise ValueError(f'Unsupported JSON schema: {path.name}')
        else:
            raise ValueError(f'Unsupported payload: {path.name}')
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f'Non-object card: {path.name}')
    return rows


def evidence(row):
    explicit = first(row, 'evidence_quote', 'short_evidence', 'quotes', 'evidence_quotes', 'quote', 'evidence')
    if explicit:
        return explicit, 'source_card_explicit_evidence_not_independently_verified'
    basis = row.get('basis')
    if isinstance(basis, list):
        excerpts = [first(part, 'transcript_excerpt', 'quote', 'evidence_quote')
                    for part in basis if isinstance(part, dict)]
        excerpts = [q for q in excerpts if q]
        if excerpts:
            return excerpts, 'transcript_excerpts_not_audio_verified'
    # A prose "basis" may be an analyst's inference; do not relabel it as a literal quote.
    return None, 'no_explicit_evidence_field'


def normalize(row, kind, source_path, line):
    nested = row.get('sources')
    nested = [part for part in nested if isinstance(part, dict)] if isinstance(nested, list) else []
    ids = first(row, 'source_topic_ids', 'topic_ids')
    if not ids:
        tid = first(row, 'topic_id', 'source_topic_id')
        if not tid and kind == 'topic_reading' and re.fullmatch(r'\d{10,20}', str(row.get('source_id', ''))):
            tid = str(row['source_id'])
        ids = [str(tid)] if tid else []
    elif not isinstance(ids, list):
        ids = [str(ids)]
    ids = [str(x) for x in ids if x is not None]
    for part in nested:
        tid = part.get('topic_id')
        if tid and str(tid) not in ids:
            ids.append(str(tid))
    url = first(row, 'source_url', 'url')
    urls = [url] if url else [f'https://wx.zsxq.com/group/15552141181242/topic/{x}' for x in ids]
    quote, quote_type = evidence(row)
    attribution = first(row, 'attribution', 'speaker_attribution', 'speaker', 'author_role', 'quote_role')
    return {
        'card_id': text(first(row, 'card_id', 'rule_id', 'id')) or f'{kind}:{line}',
        'source_kind': kind,
        'title': text(first(row, 'title', 'claim', 'principle', 'summary')),
        'claim': text(first(row, 'claim', 'principle', 'main_claim', 'summary', 'title')),
        'evidence_quote': quote,
        'evidence_type': quote_type,
        'evidence_details': row.get('basis'),
        'conditions': first(row, 'conditions', 'applicability', 'applicable_when', 'scope'),
        'boundary': first(row, 'boundary', 'limitations', 'limits', 'caveats', 'non_generalization', 'do_not_generalize'),
        'action': first(row, 'action', 'actions', 'next_action', 'operational_action'),
        'attribution': attribution or 'unresolved_do_not_assume_andy',
        'not_speaker_attributed': row.get('not_speaker_attributed', False),
        'promote_to_stable_method': row.get('promote_to_stable_method'),
        'status': first(row, 'review_status', 'status', 'reading_status'),
        'topic_ids': ids,
        'source_urls': urls,
        'batch_id': first(row, 'batch_id', 'batch'),
        'source_id': first(row, 'source_id', 'alias'),
        'source_locator': first(row, 'source_locator', 'source_path', 'batch_path', 'source_cache'),
        'time_range': first(row, 'time_range', 'timestamp_range', 'timestamps'),
        'source_details': nested,
        'card_file': str(source_path),
        'card_record': line,
        'evidence_limit': SOURCE_NOTES[kind],
        # Preserve original schema/locators: normalization must not erase attribution or uncertainty.
        'original_card': row,
    }


def tokens(query):
    query = query.casefold().strip()
    result = set(re.findall(r'[a-z0-9_]+', query))
    for part in re.findall(r'[\u3400-\u9fff]+', query):
        result.add(part)
        result.update(part[i:i+2] for i in range(len(part)-1))
    return result


def relevance(card, query):
    needle = query.casefold().strip()
    title = card['title'].casefold()
    body = text(card['original_card']).casefold()
    if not needle:
        return 0
    score = (12 if needle in title else 0) + (5 if needle in body else 0)
    for term in tokens(query):
        score += (3 if term in title else 0) + (1 if term in body else 0)
    return score


def search(root, query, limit=6, include_partial=False):
    available, missing, errors, cards, coverage, selected = {}, [], [], [], {}, {}
    for kind, candidates in SOURCES:
        path = next((root / rel for rel in candidates if (root / rel).exists()), None)
        if path is None:
            missing.append(candidates[0])
            continue
        relpath = str(path.relative_to(root))
        selected[kind] = relpath
        try:
            rows = load_rows(path)
        except (ValueError, OSError) as exc:
            errors.append({'source': relpath, 'error_type': type(exc).__name__})
            continue
        available[kind] = len(rows)
        coverage[kind] = {'loaded': len(rows), 'explicit_evidence_cards': 0,
                          'suppressed_no_explicit_evidence': 0, 'excluded_by_partial_context_policy': 0}
        for i, row in enumerate(rows, 1):
            card = normalize(row, kind, path, i)
            # Empty evidence is not silently presented as a verified source.
            if not card['evidence_quote']:
                coverage[kind]['suppressed_no_explicit_evidence'] += 1
                continue
            coverage[kind]['explicit_evidence_cards'] += 1
            if kind == 'comment_partial_context' and not include_partial:
                coverage[kind]['excluded_by_partial_context_policy'] += 1
                continue
            score = relevance(card, query)
            if score > 0:
                card['lexical_score'] = score
                cards.append(card)
    cards.sort(key=lambda c: (-c['lexical_score'], c['source_kind'], c['card_id']))
    deduped, seen = [], set()
    for card in cards:
        key = (card['source_kind'], card['card_id'])
        if key not in seen:
            seen.add(key)
            deduped.append(card)
    return {
        'query': query,
        'retrieval': 'local_lexical_matching_not_semantic_ranking_or_fact_verification',
        'available_card_counts': available,
        'selected_source_paths': selected,
        'source_coverage': coverage,
        'missing_sources': missing,
        'source_errors': errors,
        'partial_context_included': include_partial,
        'matching_cards': len(deduped),
        'result_count': min(limit, len(deduped)),
        'results': deduped[:limit],
        'usage_warning': '检索结果是回查入口，不是自动证实。须读原文上下文、确认讲者/否定/条件；独立证据按原始来源去重，不按卡数量累计。',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query')
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--limit', type=int, default=6)
    parser.add_argument('--include-partial-comments', action='store_true')
    args = parser.parse_args()
    if not args.query.strip() or not 1 <= args.limit <= 30:
        parser.error('query must be nonempty; --limit must be between 1 and 30')
    result = search(args.root, args.query, args.limit, args.include_partial_comments)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result['source_errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
