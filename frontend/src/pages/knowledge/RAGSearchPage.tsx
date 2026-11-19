import { useState, useEffect } from 'react';
import { Search, Sparkles, BookOpen, ExternalLink, ShieldCheck, BarChart2, Network, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { knowledgeService } from '@/services/knowledge';
import type { RAGAskResponse, RAGSearchResult } from '@/types';

export function RAGSearchPage() {
  const [query, setQuery] = useState('how to mitigate database connection pool timeouts in payment-service?');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'ask' | 'search' | 'evaluation'>('ask');
  const [askResult, setAskResult] = useState<RAGAskResponse | null>(null);
  const [searchResults, setSearchResults] = useState<RAGSearchResult[]>([]);
  const [evaluation, setEvaluation] = useState<any>(null);
  const [evalLoading, setEvalLoading] = useState(false);

  useEffect(() => {
    handleAsk();
  }, []);

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await knowledgeService.ask(query);
      if (res.data) {
        setAskResult(res.data);
      }
    } catch (e) {
      console.error('Ask error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await knowledgeService.search(query, undefined, 'hybrid_rerank', 6);
      if (res.data) {
        setSearchResults(res.data);
      }
    } catch (e) {
      console.error('Search error:', e);
    } finally {
      setLoading(false);
    }
  };

  const loadEvaluation = async () => {
    setEvalLoading(true);
    try {
      const res = await knowledgeService.getEvaluation();
      if (res.data) {
        setEvaluation(res.data);
      }
    } catch (e) {
      console.error('Evaluation error:', e);
    } finally {
      setEvalLoading(false);
    }
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'Knowledge' }, { label: 'RAG Engine & Evaluation' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="pb-space-sm border-b border-surface-container-highest flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Semantic RAG & GraphRAG Engine</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Hybrid retrieval with Reciprocal Rank Fusion, Cross-Encoder reranking, and citation grounding.
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant={activeTab === 'ask' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('ask')}
            >
              <Sparkles className="w-4 h-4 mr-1.5" />
              Grounded QA
            </Button>
            <Button
              variant={activeTab === 'search' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => {
                setActiveTab('search');
                if (searchResults.length === 0) handleSearch();
              }}
            >
              <Search className="w-4 h-4 mr-1.5" />
              Raw Chunks
            </Button>
            <Button
              variant={activeTab === 'evaluation' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => {
                setActiveTab('evaluation');
                if (!evaluation) loadEvaluation();
              }}
            >
              <BarChart2 className="w-4 h-4 mr-1.5" />
              RAG Evaluation
            </Button>
          </div>
        </div>

        {activeTab !== 'evaluation' && (
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (activeTab === 'ask' ? handleAsk() : handleSearch())}
                placeholder="Ask an engineering or architectural question..."
                className="fixora-input pl-9"
              />
            </div>
            <Button
              onClick={activeTab === 'ask' ? handleAsk : handleSearch}
              disabled={loading}
              className="min-w-[100px]"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin mr-1.5" /> : null}
              {activeTab === 'ask' ? 'Ask AI' : 'Retrieve'}
            </Button>
          </div>
        )}

        {/* TAB 1: Grounded QA with Citations & Graph Context */}
        {activeTab === 'ask' && (
          <div className="flex flex-col gap-space-md">
            {askResult && (
              <>
                <Card className="p-space-md bg-surface-container-low/80 border-primary-container/40">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2 text-primary font-headline font-bold text-headline-sm">
                      <Sparkles className="w-5 h-5 text-primary" />
                      Evidence-Grounded Synthesis
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-xs">
                        Intent: {askResult.queryIntent}
                      </Badge>
                      <Badge variant="success" className="font-mono text-xs flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Confidence {Math.round(askResult.confidenceScore * 100)}%
                      </Badge>
                    </div>
                  </div>

                  <div className="font-body text-body-md text-on-surface leading-relaxed whitespace-pre-line">
                    {askResult.answer}
                  </div>

                  {/* Faithfulness Check */}
                  <div className="mt-4 pt-3 border-t border-surface-container-highest/60 flex items-center gap-2 text-xs font-mono text-on-surface-variant">
                    {askResult.isFaithful ? (
                      <CheckCircle2 className="w-4 h-4 text-success shrink-0" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-warning shrink-0" />
                    )}
                    <span>{askResult.faithfulnessDetails}</span>
                  </div>
                </Card>

                {/* Graph Context */}
                {askResult.graphContext && askResult.graphContext.length > 0 && (
                  <Card className="p-space-md">
                    <div className="flex items-center gap-2 font-headline font-bold text-body-lg text-on-surface mb-2">
                      <Network className="w-4 h-4 text-primary" />
                      GraphRAG Architectural Relationships
                    </div>
                    <ul className="space-y-1.5 text-xs font-mono text-on-surface-variant">
                      {askResult.graphContext.map((g, idx) => (
                        <li key={idx} className="p-2 bg-surface-container rounded border border-surface-container-high">
                          {g}
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}

                {/* Verifiable Citations */}
                <div className="flex flex-col gap-2">
                  <h3 className="font-headline font-bold text-body-md text-on-surface flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-primary" />
                    Verifiable Source Citations ({askResult.citations.length})
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-space-sm">
                    {askResult.citations.map((cite, idx) => (
                      <Card key={idx} className="p-3 text-xs font-mono flex flex-col justify-between">
                        <div>
                          <div className="flex items-center justify-between text-primary font-bold mb-1">
                            <span>{cite.label} {cite.title}</span>
                            <Badge variant="outline">{cite.sourceType}</Badge>
                          </div>
                          <div className="text-on-surface-variant break-all">{cite.filePath}</div>
                        </div>
                        <div className="mt-2 text-right text-on-surface-variant text-[10px]">
                          Relevance Score: {cite.relevanceScore}
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB 2: Raw Retrieved Chunks */}
        {activeTab === 'search' && (
          <div className="flex flex-col gap-space-sm">
            {searchResults.map((hit, idx) => (
              <Card key={idx} className="p-space-md">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-headline font-bold text-body-md text-on-surface">
                    {hit.metadata?.title || hit.source}
                  </div>
                  <div className="flex items-center gap-2 font-mono text-xs">
                    <Badge variant="outline">{hit.sourceType}</Badge>
                    <span className="text-primary font-bold">RRF Score: {hit.relevanceScore}</span>
                  </div>
                </div>
                <p className="font-body text-body-sm text-on-surface-variant whitespace-pre-wrap line-clamp-3">
                  {hit.content}
                </p>
                <div className="mt-3 text-xs font-mono text-on-surface-variant border-t border-surface-container-highest/40 pt-2 flex justify-between">
                  <span>Path: {hit.source}</span>
                  <span>Method: {hit.metadata?.retrievalMethod || 'hybrid_rrf'}</span>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* TAB 3: RAG Evaluation Dashboard */}
        {activeTab === 'evaluation' && (
          <div className="flex flex-col gap-space-md">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="font-headline font-bold text-headline-sm text-on-surface">Empirical RAG Benchmark Results</h2>
                <p className="font-body text-body-xs text-on-surface-variant">Ground truth query evaluation comparing Dense, Hybrid RRF, and Cross-Encoder Reranking.</p>
              </div>
              <Button size="sm" variant="secondary" onClick={loadEvaluation} disabled={evalLoading}>
                <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${evalLoading ? 'animate-spin' : ''}`} />
                Re-run Benchmark
              </Button>
            </div>

            {evaluation && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md font-mono">
                  <Card className="p-space-md border-t-2 border-t-outline">
                    <div className="text-mono-tag text-on-surface-variant">DENSE VECTOR RETRIEVAL (QDRANT)</div>
                    <div className="mt-3 space-y-1 text-xs">
                      <div className="flex justify-between"><span>Recall@3:</span> <strong className="text-on-surface">{evaluation.denseOnly?.meanRecallAtK}</strong></div>
                      <div className="flex justify-between"><span>Precision@3:</span> <strong className="text-on-surface">{evaluation.denseOnly?.meanPrecisionAtK}</strong></div>
                      <div className="flex justify-between"><span>MRR:</span> <strong className="text-on-surface">{evaluation.denseOnly?.meanReciprocalRank}</strong></div>
                      <div className="flex justify-between"><span>nDCG@3:</span> <strong className="text-on-surface">{evaluation.denseOnly?.meanNdcgAtK}</strong></div>
                      <div className="flex justify-between text-primary"><span>Avg Latency:</span> <strong>{evaluation.denseOnly?.avgLatencyMs} ms</strong></div>
                    </div>
                  </Card>

                  <Card className="p-space-md border-t-2 border-t-outline">
                    <div className="text-mono-tag text-on-surface-variant">HYBRID RRF (DENSE + BM25)</div>
                    <div className="mt-3 space-y-1 text-xs">
                      <div className="flex justify-between"><span>Recall@3:</span> <strong className="text-on-surface">{evaluation.hybridRrf?.meanRecallAtK}</strong></div>
                      <div className="flex justify-between"><span>Precision@3:</span> <strong className="text-on-surface">{evaluation.hybridRrf?.meanPrecisionAtK}</strong></div>
                      <div className="flex justify-between"><span>MRR:</span> <strong className="text-on-surface">{evaluation.hybridRrf?.meanReciprocalRank}</strong></div>
                      <div className="flex justify-between"><span>nDCG@3:</span> <strong className="text-on-surface">{evaluation.hybridRrf?.meanNdcgAtK}</strong></div>
                      <div className="flex justify-between text-primary"><span>Avg Latency:</span> <strong>{evaluation.hybridRrf?.avgLatencyMs} ms</strong></div>
                    </div>
                  </Card>

                  <Card className="p-space-md border-t-2 border-t-primary bg-primary-container/10">
                    <div className="text-mono-tag text-primary font-bold">HYBRID RRF + RERANKING (RECOMMENDED)</div>
                    <div className="mt-3 space-y-1 text-xs">
                      <div className="flex justify-between"><span>Recall@3:</span> <strong className="text-on-surface">{evaluation.hybridWithReranking?.meanRecallAtK}</strong></div>
                      <div className="flex justify-between"><span>Precision@3:</span> <strong className="text-on-surface">{evaluation.hybridWithReranking?.meanPrecisionAtK}</strong></div>
                      <div className="flex justify-between"><span>MRR:</span> <strong className="text-on-surface">{evaluation.hybridWithReranking?.meanReciprocalRank}</strong></div>
                      <div className="flex justify-between"><span>nDCG@3:</span> <strong className="text-on-surface">{evaluation.hybridWithReranking?.meanNdcgAtK}</strong></div>
                      <div className="flex justify-between text-primary"><span>Avg Latency:</span> <strong>{evaluation.hybridWithReranking?.avgLatencyMs} ms</strong></div>
                    </div>
                  </Card>
                </div>

                <Card className="p-space-md bg-surface-container font-mono text-xs">
                  <div className="font-bold text-primary mb-1">Comparative Empirical Summary:</div>
                  <div className="text-on-surface-variant">{evaluation.comparisonSummary}</div>
                </Card>
              </>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
