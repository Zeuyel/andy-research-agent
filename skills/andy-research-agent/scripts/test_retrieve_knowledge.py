#!/usr/bin/env python3
"""Isolated fixtures only; no CLI, credentials, network or real research actions."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('retrieve_knowledge.py')
spec = importlib.util.spec_from_file_location('retrieve_knowledge', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, rel, payload):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == '.jsonl':
            path.write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in payload) + '\n')
        else:
            path.write_text(json.dumps(payload, ensure_ascii=False))
        return path

    def rule(self, **kwargs):
        return dict(rule_id='M01', title='前言与贡献定位', evidence_quote='先把前言写好',
                    source_topic_ids=['123'], boundary='不是普适写作顺序', **kwargs)

    def test_missing_sources_explicit(self):
        result = mod.search(self.root, '前言')
        self.assertEqual(result['result_count'], 0)
        self.assertEqual(len(result['missing_sources']), len(mod.SOURCES))

    def test_method_keeps_quote_boundary_and_citation(self):
        self.put('methods/verified-rules.json', {'rules': [self.rule()]})
        card = mod.search(self.root, '前言')['results'][0]
        self.assertEqual(card['evidence_quote'], '先把前言写好')
        self.assertIn('不是普适', card['boundary'])
        self.assertEqual(card['topic_ids'], ['123'])
        self.assertTrue(card['source_urls'][0].endswith('/123'))

    def test_comments_excluded_unless_requested(self):
        self.put('enrichment/cards/andy-deep-comment-cards.jsonl', [
            {'card_id':'c1','title':'素材库','short_evidence':'验证之后再整理素材库','topic_id':None,
             'status':'context_unlinked'}])
        result = mod.search(self.root, '素材库')
        self.assertEqual(result['available_card_counts']['comment_partial_context'], 1)
        self.assertEqual(result['result_count'], 0)
        included = mod.search(self.root, '素材库', include_partial=True)['results'][0]
        self.assertEqual(included['topic_ids'], [])
        self.assertEqual(included['source_urls'], [])
        self.assertIn('未关联', included['evidence_limit'])

    def test_video_json_fallback_preserves_speaker_and_batch(self):
        row = {'card_id':'v1','claim':'检索反馈迭代','quotes':['检索需要反馈'],
               'batch_id':'first-3h-001','source_id':'first-3h','attribution':'讲者未辨明',
               'time_range':'00:02:00--00:03:00','limitations':'ASR带噪'}
        self.put('video-text/reviewed-knowledge-cards.json', {'cards': [row]})
        card = mod.search(self.root, '检索')['results'][0]
        self.assertEqual(card['batch_id'], row['batch_id'])
        self.assertEqual(card['attribution'], '讲者未辨明')
        self.assertEqual(card['original_card'], row)
        self.assertEqual(card['source_urls'], [])

    def test_malformed_source_reported_not_empty_success(self):
        path = self.root / 'methods/verified-rules.json'
        path.parent.mkdir(parents=True)
        path.write_text('{broken')
        result = mod.search(self.root, '检索')
        self.assertEqual(len(result['source_errors']), 1)
        self.assertEqual(result['available_card_counts'], {})

    def test_unknown_schema_reported(self):
        self.put('methods/verified-rules.json', {'metadata': 'not_cards'})
        self.assertEqual(len(mod.search(self.root, '检索')['source_errors']), 1)

    def test_nonobject_card_reported(self):
        self.put('methods/verified-rules.json', {'rules': ['not_an_object']})
        self.assertEqual(len(mod.search(self.root, '检索')['source_errors']), 1)

    def test_no_evidence_not_promoted(self):
        self.put('methods/verified-rules.json', {'rules':[{'rule_id':'M0','title':'前言'}]})
        self.assertEqual(mod.search(self.root, '前言')['result_count'], 0)

    def test_id_dedup_within_source(self):
        self.put('methods/verified-rules.json', {'rules':[self.rule(), self.rule()]})
        result = mod.search(self.root, '前言')
        self.assertEqual(result['matching_cards'], 1)
        self.assertEqual(result['available_card_counts']['method_rule'], 2)

    def test_no_duplicate_json_jsonl_loading(self):
        row = {'card_id':'v1','claim':'检索','evidence_quote':'检索原话'}
        self.put('video-text/reviewed-knowledge-cards.jsonl', [row])
        self.put('video-text/reviewed-knowledge-cards.json', {'cards':[row]})
        result = mod.search(self.root, '检索')
        self.assertEqual(result['available_card_counts']['video_text'], 1)
        self.assertEqual(result['matching_cards'], 1)

    def test_limit_and_no_match(self):
        self.put('methods/verified-rules.json', {'rules':[
            dict(self.rule(), rule_id=f'M{i}') for i in range(5)]})
        self.assertEqual(mod.search(self.root, '前言', limit=2)['result_count'], 2)
        self.assertEqual(mod.search(self.root, 'xyzunmatched')['result_count'], 0)

    def test_blank_query_no_match(self):
        self.put('methods/verified-rules.json', {'rules':[self.rule()]})
        self.assertEqual(mod.search(self.root, '   ')['result_count'], 0)

    def test_real_topic_schema_role_numeric_id_and_boundary(self):
        row = {'card_id':'read-001', 'source_id':'14588218814121442', 'title':'综述问题',
               'quote':'综述中的一句原话', 'quote_role':'andy_body_reporting_third_party',
               'do_not_generalize':'不要当作Andy本人原创', 'actions':['检查来源']}
        self.put('corpus/model-reading-cards.jsonl', [row])
        card = mod.search(self.root, '综述')['results'][0]
        self.assertEqual(card['topic_ids'], ['14588218814121442'])
        self.assertEqual(card['attribution'], 'andy_body_reporting_third_party')
        self.assertIn('不要当作', card['boundary'])

    def test_real_video_basis_schema_and_nested_source(self):
        row = {'card_id':'VT-001', 'title':'背景写作', 'claim':'研究意义要有支撑',
               'basis':[{'timestamp':'00:41:16', 'transcript_excerpt':'参考引用一本教科书'}],
               'speaker_attribution':'讲者未独立核验', 'not_speaker_attributed':True,
               'sources':[{'topic_id':'5121822244551254', 'alias':'A01',
                           'time_range':'00:41:00--00:42:00'}]}
        self.put('video-text/reviewed-knowledge-cards.json', [row])
        result = mod.search(self.root, '背景')
        card = result['results'][0]
        self.assertEqual(card['evidence_quote'], ['参考引用一本教科书'])
        self.assertEqual(card['topic_ids'], ['5121822244551254'])
        self.assertEqual(card['source_details'], row['sources'])
        self.assertEqual(card['evidence_details'], row['basis'])
        self.assertTrue(card['not_speaker_attributed'])
        self.assertEqual(card['attribution'], '讲者未独立核验')
        self.assertEqual(result['source_coverage']['video_text']['explicit_evidence_cards'], 1)

    def test_prose_basis_is_not_relabelled_as_literal_quote(self):
        self.put('video-text/reviewed-knowledge-cards.json', [
            {'card_id':'VT-X','title':'背景写作','basis':'分析者推理，不是原文'}])
        result = mod.search(self.root, '背景')
        self.assertEqual(result['result_count'], 0)
        self.assertEqual(result['source_coverage']['video_text']['suppressed_no_explicit_evidence'], 1)

    def test_unresolved_author_never_defaults_to_andy(self):
        self.put('video-text/reviewed-knowledge-cards.json', [
            {'card_id':'VT-X','title':'检索','evidence_quote':'检索原话'}])
        card = mod.search(self.root, '检索')['results'][0]
        self.assertEqual(card['attribution'], 'unresolved_do_not_assume_andy')

    def test_safe_manually_read_fallback_not_wrong_v2_source(self):
        self.put('corpus/evidence-cards-v2.jsonl', [
            {'card_id':'wrong','source_id':'14588218814121442','quote':'不匹配原话','title':'检索'}])
        self.put('corpus/continuation/main-read-20261017.json', {'cards':[
            {'card_id':'real','topic_id':'14588218814121442','evidence_quote':'检索准确短引',
             'title':'检索','promote_to_stable_method':False}]})
        result = mod.search(self.root, '检索')
        self.assertEqual(result['available_card_counts']['topic_reading'], 1)
        self.assertEqual(result['results'][0]['card_id'], 'real')
        self.assertFalse(result['results'][0]['promote_to_stable_method'])
        self.assertTrue(result['selected_source_paths']['topic_reading'].endswith('main-read-20261017.json'))

    def test_video_alias_not_converted_to_topic_id(self):
        row = {'card_id':'VT-X','source_id':'A01','title':'检索','quote':'检索原文'}
        self.put('video-text/reviewed-knowledge-cards.json', [row])
        self.assertEqual(mod.search(self.root, '检索')['results'][0]['topic_ids'], [])

    def test_current_source_schema_is_used_not_withdrawn_v2(self):
        self.put('corpus/current-source-reading-cards.jsonl', [
            {'card_id':'current-1','source_id':'14588218814121442','title':'复现',
             'quote':'准确原话','quote_role':'andy_answer'}])
        self.put('corpus/evidence-cards-v2.jsonl', [
            {'card_id':'bad','source_id':'14588218814121442','title':'复现','quote':'错配原话'}])
        r=mod.search(self.root,'复现')
        self.assertEqual(r['results'][0]['card_id'],'current-1')
        self.assertEqual(r['available_card_counts']['topic_reading'],1)

    def test_article_local_version_boundary_and_speaker_preserved(self):
        self.put('retrieval/article-reading-cards.jsonl', [
            {'card_id':'ARTICLE-1','title':'图表', 'quote':'先看图表', 'speaker':'本地作者标签',
             'topic_id':'211254882121241','boundary':'远端文章版本未核对'}])
        card=mod.search(self.root,'图表')['results'][0]
        self.assertEqual(card['source_kind'],'article_reading')
        self.assertEqual(card['attribution'],'本地作者标签')
        self.assertIn('远端文章',card['boundary'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
