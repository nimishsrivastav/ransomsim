'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import ReactMarkdown from 'react-markdown';
import type { Message, Scenario } from '@/types';
import {
  sendMessage,
  getConversationHistory,
  completeNegotiation,
  formatRansom,
  formatTimestamp,
  getTimeRemaining,
} from '@/lib/api';

export default function NegotiatePage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  // State
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [timeRemaining, setTimeRemaining] = useState({ hours: 72, minutes: 0, expired: false });
  const [pressureLevel, setPressureLevel] = useState(1);
  const [showAllSystems, setShowAllSystems] = useState(false);
  const [showAllData, setShowAllData] = useState(false);
  const [clientToken, setClientToken] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load conversation history on mount
  useEffect(() => {
    loadConversation();
  }, [sessionId]);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Update countdown timer
  useEffect(() => {
    if (!scenario?.deadline) return;

    const interval = setInterval(() => {
      setTimeRemaining(getTimeRemaining(scenario.deadline));
    }, 60000); // Update every minute

    // Initial update
    setTimeRemaining(getTimeRemaining(scenario.deadline));

    return () => clearInterval(interval);
  }, [scenario?.deadline]);

  const loadConversation = async () => {
    setIsLoading(true);
    try {
      const history = await getConversationHistory(sessionId);
      setMessages(history.messages);

      // Try to load scenario and client token from session storage
      const storedScenario = sessionStorage.getItem(`scenario_${sessionId}`);
      if (storedScenario) {
        setScenario(JSON.parse(storedScenario));
      }
      const storedToken = sessionStorage.getItem(`client_token_${sessionId}`);
      if (storedToken) {
        setClientToken(storedToken);
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
      setError('Failed to load conversation history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isSending) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsSending(true);
    setError(null);

    // Optimistically add user message
    const tempUserMessage: Message = {
      id: `temp_${Date.now()}`,
      sender: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      const response = await sendMessage(sessionId, { content: userMessage }, clientToken ?? undefined);

      // Keep the user message (update temp id) and add AI response
      setMessages((prev) => {
        // Update the temp user message to have a proper id, then add AI response
        const updated = prev.map((m) =>
          m.id === tempUserMessage.id
            ? { ...m, id: `user_${response.message_id}` }
            : m
        );
        return [...updated, response.ai_response];
      });

      // Update pressure level
      if (response.pressure_level !== undefined) {
        setPressureLevel(response.pressure_level);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message. Please try again.');
      // Remove temp message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));
      setInputValue(userMessage); // Restore input
    } finally {
      setIsSending(false);
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleEndNegotiation = async () => {
    if (!confirm('Are you sure you want to end this negotiation? You will be taken to the analysis page.')) {
      return;
    }

    try {
      await completeNegotiation(sessionId, 'user_ended');
      router.push(`/analysis/${sessionId}`);
    } catch (err) {
      console.error('Failed to end negotiation:', err);
      setError('Failed to end negotiation');
    }
  };

  const getPressureColor = () => {
    if (pressureLevel <= 2) return 'text-green-400';
    if (pressureLevel <= 4) return 'text-amber-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white flex flex-col">
      {/* Training Simulation Banner */}
      <div className="bg-amber-600 text-black text-center py-2 text-sm font-medium">
        TRAINING SIMULATION ONLY - Not for real incident response
      </div>

      {/* Header */}
      <header className="border-b border-zinc-800 flex-shrink-0">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-lg font-bold text-red-500">
            RansomSim: AI‑Driven Ransomware Negotiation Training
          </Link>
          <Button
            onClick={handleEndNegotiation}
            variant="outline"
            className="border-zinc-600 text-zinc-300 hover:bg-zinc-800"
          >
            End Negotiation
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-4 flex gap-4 overflow-hidden">
        {/* Left Sidebar - Scenario Info */}
        <aside className="w-80 flex-shrink-0 hidden lg:block">
          <Card className="bg-zinc-800/50 border-zinc-700 h-full">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Scenario Briefing</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Timer */}
              <div className="p-3 bg-zinc-900 rounded-lg">
                <div className="text-sm text-zinc-400 mb-1">Deadline Countdown</div>
                <div className={`text-2xl font-mono font-bold ${timeRemaining.expired ? 'text-red-500' : 'text-amber-400'}`}>
                  {timeRemaining.expired ? 'EXPIRED' : `${timeRemaining.hours}h ${timeRemaining.minutes}m`}
                </div>
              </div>

              {/* Pressure Level */}
              <div className="p-3 bg-zinc-900 rounded-lg">
                <div className="text-sm text-zinc-400 mb-1">Threat Level</div>
                <div className={`font-semibold ${getPressureColor()}`}>
                  {pressureLevel <= 2 ? 'Low' : pressureLevel <= 4 ? 'Moderate' : 'High'}
                </div>
                <div className="mt-2 h-2 bg-zinc-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      pressureLevel <= 2 ? 'bg-green-500' : pressureLevel <= 4 ? 'bg-amber-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${(pressureLevel / 5) * 100}%` }}
                  />
                </div>
              </div>

              {scenario && (
                <>
                  <Separator className="bg-zinc-700" />

                  {/* Ransom Demand */}
                  <div>
                    <div className="text-sm text-zinc-400">Initial Demand</div>
                    <div className="text-xl font-bold text-red-400">
                      {formatRansom(scenario.ransom_amount)}
                    </div>
                  </div>

                  {/* Systems Affected */}
                  <div>
                    <div className="text-sm text-zinc-400 mb-2">Systems Affected</div>
                    <div className="flex flex-col gap-1.5">
                      {(showAllSystems ? scenario.systems_affected : scenario.systems_affected.slice(0, 4)).map((system, i) => (
                        <div key={i} className="text-xs text-zinc-300 bg-zinc-800 border border-zinc-600 rounded px-2 py-1 break-words">
                          {system}
                        </div>
                      ))}
                      {scenario.systems_affected.length > 4 && (
                        <button
                          onClick={() => setShowAllSystems(!showAllSystems)}
                          className="text-xs text-zinc-400 hover:text-zinc-200 text-left underline"
                        >
                          {showAllSystems ? 'Show less' : `+${scenario.systems_affected.length - 4} more`}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Data at Risk */}
                  <div>
                    <div className="text-sm text-zinc-400 mb-2">Data at Risk</div>
                    <div className="flex flex-col gap-1.5">
                      {(showAllData ? scenario.data_at_risk : scenario.data_at_risk.slice(0, 3)).map((data, i) => (
                        <div key={i} className="text-xs text-red-400 bg-red-950/50 border border-red-500/60 rounded px-2 py-1 break-words">
                          {data}
                        </div>
                      ))}
                      {scenario.data_at_risk.length > 3 && (
                        <button
                          onClick={() => setShowAllData(!showAllData)}
                          className="text-xs text-red-400 hover:text-red-300 text-left underline"
                        >
                          {showAllData ? 'Show less' : `+${scenario.data_at_risk.length - 3} more`}
                        </button>
                      )}
                    </div>
                  </div>
                </>
              )}

              {/* Tips */}
              <Separator className="bg-zinc-700" />
              <div>
                <div className="text-sm text-zinc-400 mb-2">Negotiation Tips</div>
                <ul className="text-xs text-zinc-500 space-y-1">
                  <li>- Verify they have your data before negotiating</li>
                  <li>- Never accept the first offer</li>
                  <li>- Claim limited budget authority</li>
                  <li>- Ask for proof of deletion capability</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </aside>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {error && (
            <Alert className="mb-4 bg-red-900/20 border-red-600/50 flex-shrink-0">
              <AlertDescription className="text-red-400">{error}</AlertDescription>
            </Alert>
          )}

          {/* Messages */}
          <Card className="flex-1 bg-zinc-800/30 border-zinc-700 flex flex-col overflow-hidden">
            <ScrollArea className="flex-1 p-4" ref={scrollRef}>
              {isLoading ? (
                <div className="flex items-center justify-center h-full text-zinc-500">
                  Loading conversation...
                </div>
              ) : messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-zinc-500">
                  Waiting for threat actor&apos;s initial contact...
                </div>
              ) : (
                <div className="space-y-4 w-full overflow-hidden">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-4 ${
                          message.sender === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-zinc-700 text-zinc-100'
                        }`}
                      >
                        <div className="text-xs mb-1 opacity-70">
                          {message.sender === 'user' ? 'You' : 'Threat Actor'} - {formatTimestamp(message.timestamp)}
                        </div>
                        <div className="break-words overflow-hidden prose prose-invert prose-base max-w-none prose-p:my-2 prose-li:my-0.5 prose-ul:my-2 prose-ol:my-2 prose-strong:text-white prose-hr:my-3">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  ))}
                  {isSending && (
                    <div className="flex justify-start">
                      <div className="bg-zinc-700 text-zinc-400 rounded-lg p-4">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" />
                          <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                          <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>

            {/* Input Area */}
            <div className="p-4 border-t border-zinc-700 flex-shrink-0">
              <div className="flex gap-2">
                <Textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your response... (Enter to send, Shift+Enter for new line)"
                  className="bg-zinc-900 border-zinc-700 resize-none min-h-[60px]"
                  disabled={isSending}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isSending}
                  className="bg-red-600 hover:bg-red-700 px-6"
                >
                  Send
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
