'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { Analysis, TacticalInsight, Mistake, Success, Recommendation } from '@/types';
import { generateAnalysis, getAnalysis } from '@/lib/api';

const ANALYSIS_LOADING_MESSAGES = [
  'Reviewing conversation transcript...',
  'Evaluating negotiation tactics...',
  'Identifying key decision points...',
  'Assessing threat actor responses...',
  'Calculating performance metrics...',
  'Generating recommendations...',
];

function AnalysisLoadingScreen() {
  const [messageIndex, setMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const msgInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % ANALYSIS_LOADING_MESSAGES.length);
    }, 2500);
    return () => clearInterval(msgInterval);
  }, []);

  useEffect(() => {
    const progressInterval = setInterval(() => {
      setProgress((prev) => (prev >= 90 ? 90 : prev + Math.random() * 8));
    }, 500);
    return () => clearInterval(progressInterval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white flex items-center justify-center">
      <div className="text-center max-w-md mx-auto px-4">
        {/* Animated magnifying glass / scan icon */}
        <div className="relative mb-8">
          <div className="w-24 h-24 mx-auto">
            <svg
              className="w-full h-full text-red-500"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <circle cx="11" cy="11" r="7" className="animate-pulse" />
              <path d="M21 21l-4.35-4.35" strokeLinecap="round" />
              {/* Scan lines inside the circle */}
              <path d="M8 9h6" className="animate-pulse" style={{ animationDelay: '0s' }} />
              <path d="M8 11h6" className="animate-pulse" style={{ animationDelay: '0.2s' }} />
              <path d="M8 13h4" className="animate-pulse" style={{ animationDelay: '0.4s' }} />
            </svg>
          </div>
          {/* Rotating ring */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 border-4 border-red-500/20 border-t-red-500 rounded-full animate-spin" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold mb-2">Analyzing Your Negotiation</h2>
        <p className="text-zinc-500 text-sm mb-6">Our AI is reviewing every message and tactic</p>

        {/* Loading message */}
        <p className="text-lg text-red-400 font-mono mb-6 min-h-[28px] transition-opacity duration-300">
          {ANALYSIS_LOADING_MESSAGES[messageIndex]}
        </p>

        {/* Progress bar */}
        <div className="w-full bg-zinc-800 rounded-full h-2 mb-4 overflow-hidden">
          <div
            className="bg-red-500 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Bouncing dots */}
        <div className="flex justify-center gap-2 mb-6">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 bg-red-500 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>

        <p className="text-zinc-600 text-xs">This may take a moment</p>
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalysis();
  }, [sessionId]);

  const loadAnalysis = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Try to get cached analysis first
      let analysisData = await getAnalysis(sessionId).catch(() => null);

      // If not cached, generate new analysis
      if (!analysisData) {
        analysisData = await generateAnalysis(sessionId);
      }

      setAnalysis(analysisData);
    } catch (err) {
      console.error('Failed to load analysis:', err);
      setError('Failed to generate analysis. The session may have expired or there was an error.');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-400';
    if (score >= 6) return 'text-amber-400';
    if (score >= 4) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 9) return 'Excellent';
    if (score >= 7) return 'Good';
    if (score >= 5) return 'Average';
    if (score >= 3) return 'Needs Improvement';
    return 'Poor';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-red-500 text-red-400';
      case 'medium':
        return 'border-amber-500 text-amber-400';
      default:
        return 'border-green-500 text-green-400';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500/20 text-red-400';
      case 'medium':
        return 'bg-amber-500/20 text-amber-400';
      default:
        return 'bg-green-500/20 text-green-400';
    }
  };

  if (isLoading) {
    return <AnalysisLoadingScreen />;
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white">
        <div className="container mx-auto px-4 py-16">
          <Alert className="max-w-xl mx-auto bg-red-900/20 border-red-600/50">
            <AlertDescription className="text-red-400">
              {error || 'Failed to load analysis'}
            </AlertDescription>
          </Alert>
          <div className="text-center mt-8">
            <Link href="/configure">
              <Button className="bg-red-600 hover:bg-red-700">Start New Simulation</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white">
      {/* Training Simulation Banner */}
      <div className="bg-amber-600 text-black text-center py-2 text-sm font-medium">
        TRAINING SIMULATION ONLY - Not for real incident response
      </div>

      {/* Header */}
      <header className="border-b border-zinc-800">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-red-500">
            RansomSim: AI‑Driven Ransomware Negotiation Training
          </Link>
          <Link href="/configure">
            <Button className="bg-red-600 hover:bg-red-700">Try Another Scenario</Button>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Negotiation Analysis</h1>

          {/* Performance Score Card */}
          <Card className="bg-zinc-800/50 border-zinc-700 mb-8">
            <CardContent className="py-8">
              <div className="flex flex-col md:flex-row items-center gap-8">
                {/* Score Circle */}
                <div className="flex-shrink-0">
                  <div className={`w-32 h-32 rounded-full border-4 ${getScoreColor(analysis.performance_score).replace('text-', 'border-')} flex flex-col items-center justify-center`}>
                    <span className={`text-4xl font-bold ${getScoreColor(analysis.performance_score)}`}>
                      {analysis.performance_score.toFixed(1)}
                    </span>
                    <span className="text-sm text-zinc-400">/ 10</span>
                  </div>
                </div>

                {/* Score Details */}
                <div className="flex-1 text-center md:text-left">
                  <div className={`text-2xl font-bold mb-2 ${getScoreColor(analysis.performance_score)}`}>
                    {getScoreLabel(analysis.performance_score)}
                  </div>
                  <p className="text-zinc-400 mb-4">{analysis.outcome}</p>
                  <div className="flex flex-wrap gap-4 justify-center md:justify-start">
                    <div className="text-center">
                      <div className="text-2xl font-bold">{analysis.message_count}</div>
                      <div className="text-xs text-zinc-500">Messages</div>
                    </div>
                    <Separator orientation="vertical" className="h-12 bg-zinc-700 hidden md:block" />
                    <div className="text-center">
                      <div className="text-2xl font-bold">{analysis.time_to_resolution}</div>
                      <div className="text-xs text-zinc-500">Minutes</div>
                    </div>
                    <Separator orientation="vertical" className="h-12 bg-zinc-700 hidden md:block" />
                    <div className="text-center">
                      <div className="text-2xl font-bold">{analysis.concessions_made}</div>
                      <div className="text-xs text-zinc-500">Concessions</div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Mistakes Section */}
            <Card className="bg-zinc-800/50 border-zinc-700">
              <CardHeader>
                <CardTitle className="text-red-400">Areas for Improvement</CardTitle>
                <CardDescription className="text-zinc-400">
                  Key mistakes identified in your negotiation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {analysis.mistakes.length === 0 ? (
                    <p className="text-zinc-500">No major mistakes identified. Great job!</p>
                  ) : (
                    <div className="space-y-4">
                      {analysis.mistakes.map((mistake: Mistake, index: number) => (
                        <div key={index} className="p-4 bg-zinc-900/50 rounded-lg">
                          <div className="flex items-start justify-between mb-2">
                            <span className="font-medium">{mistake.description}</span>
                            <Badge variant="outline" className={getSeverityColor(mistake.severity)}>
                              {mistake.severity}
                            </Badge>
                          </div>
                          <p className="text-sm text-zinc-400 mb-2">
                            <span className="text-red-400">Consequence:</span> {mistake.consequence}
                          </p>
                          <p className="text-sm text-zinc-400">
                            <span className="text-green-400">Better approach:</span> {mistake.better_approach}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Successes Section */}
            <Card className="bg-zinc-800/50 border-zinc-700">
              <CardHeader>
                <CardTitle className="text-green-400">What Worked Well</CardTitle>
                <CardDescription className="text-zinc-400">
                  Successful tactics you employed
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {analysis.successes.length === 0 ? (
                    <p className="text-zinc-500">No notable successes identified.</p>
                  ) : (
                    <div className="space-y-4">
                      {analysis.successes.map((success: Success, index: number) => (
                        <div key={index} className="p-4 bg-zinc-900/50 rounded-lg">
                          <div className="font-medium mb-2">{success.description}</div>
                          <p className="text-sm text-zinc-400">
                            <span className="text-green-400">Impact:</span> {success.impact}
                          </p>
                          <p className="text-xs text-zinc-500 mt-1">{success.message_ref}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Tactical Breakdown */}
          <Card className="bg-zinc-800/50 border-zinc-700 mt-8">
            <CardHeader>
              <CardTitle>Tactical Breakdown</CardTitle>
              <CardDescription className="text-zinc-400">
                Message-by-message analysis of your negotiation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                {analysis.tactical_breakdown.length === 0 ? (
                  <p className="text-zinc-500">No tactical insights available.</p>
                ) : (
                  <div className="space-y-4">
                    {analysis.tactical_breakdown.map((insight: TacticalInsight) => (
                      <div key={insight.id} className="p-4 bg-zinc-900/50 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-sm text-zinc-500">{insight.message_ref}</span>
                          <Badge
                            variant="outline"
                            className={
                              insight.insight_type === 'mistake'
                                ? 'border-red-500 text-red-400'
                                : insight.insight_type === 'success'
                                ? 'border-green-500 text-green-400'
                                : 'border-amber-500 text-amber-400'
                            }
                          >
                            {insight.insight_type}
                          </Badge>
                        </div>
                        <p className="text-zinc-300 mb-2">{insight.analysis}</p>
                        {insight.improvement && (
                          <p className="text-sm text-zinc-400">
                            <span className="text-amber-400">Suggestion:</span> {insight.improvement}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card className="bg-zinc-800/50 border-zinc-700 mt-8">
            <CardHeader>
              <CardTitle>Recommendations</CardTitle>
              <CardDescription className="text-zinc-400">
                Prioritized areas for skill development
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {analysis.recommendations.map((rec: Recommendation, index: number) => (
                  <div key={index} className={`p-4 rounded-lg ${getPriorityColor(rec.priority)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{rec.skill}</span>
                      <Badge variant="outline" className="border-current">
                        {rec.priority}
                      </Badge>
                    </div>
                    <p className="text-sm opacity-80">{rec.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Benchmark Comparison */}
          {analysis.benchmarks && (
            <Card className="bg-zinc-800/50 border-zinc-700 mt-8">
              <CardHeader>
                <CardTitle>Benchmark Comparison</CardTitle>
                <CardDescription className="text-zinc-400">
                  How you compare to typical negotiations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-8">
                  <div>
                    <div className="text-sm text-zinc-400 mb-2">Time to Resolution</div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-bold">{analysis.benchmarks.user_time} min</span>
                      <span className="text-zinc-500">vs avg {analysis.benchmarks.avg_time} min</span>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-zinc-400 mb-2">Concessions Made</div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-bold">{analysis.benchmarks.user_concessions}</span>
                      <span className="text-zinc-500">vs avg {analysis.benchmarks.avg_concessions}</span>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-zinc-400 mb-2">Effective Outcome</div>
                    <div className="text-2xl font-bold text-green-400">
                      {analysis.performance_score >= 6 ? 'Above Average' : 'Below Average'}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Resources Section */}
          <Card className="bg-zinc-800/30 border-zinc-700 mt-8">
            <CardHeader>
              <CardTitle>Additional Resources</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-medium mb-2">Ransomware Response</h4>
                  <ul className="text-zinc-400 space-y-1">
                    <li>
                      <a href="https://www.cisa.gov/stopransomware" className="text-amber-400 hover:underline" target="_blank" rel="noopener noreferrer">
                        CISA StopRansomware
                      </a>
                    </li>
                    <li>
                      <a href="https://www.ic3.gov" className="text-amber-400 hover:underline" target="_blank" rel="noopener noreferrer">
                        FBI IC3 - Report Incidents
                      </a>
                    </li>
                    <li>
                      <a href="https://www.nomoreransom.org" className="text-amber-400 hover:underline" target="_blank" rel="noopener noreferrer">
                        No More Ransom Project
                      </a>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Important Reminders</h4>
                  <ul className="text-zinc-400 space-y-1">
                    <li>- Always involve law enforcement early</li>
                    <li>- Paying ransom does not guarantee recovery</li>
                    <li>- Document everything for insurance and legal</li>
                    <li>- Consider professional negotiation services</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/configure">
              <Button size="lg" className="bg-red-600 hover:bg-red-700 px-8">
                Try Another Scenario
              </Button>
            </Link>
            <Link href="/">
              <Button size="lg" variant="outline" className="border-zinc-600 text-zinc-300 hover:bg-zinc-800 px-8">
                Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800 py-8 mt-16">
        <div className="container mx-auto px-4 text-center text-zinc-500 text-sm">
          <p>RansomSim: AI‑Driven Ransomware Negotiation Training - A Gemini 3 Hackathon Project</p>
          <p className="mt-2">Built for educational purposes only.</p>
        </div>
      </footer>
    </div>
  );
}
