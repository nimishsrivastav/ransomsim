'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  OrganizationSize,
  DataSensitivity,
  PersonaType,
  ScenarioCreateRequest,
  INDUSTRIES,
  PERSONA_INFO,
} from '@/types';
import { generateScenario, startNegotiation } from '@/lib/api';

const LOADING_MESSAGES = [
  'Initializing threat simulation...',
  'Generating adversary profile...',
  'Creating breach scenario...',
  'Preparing ransom demands...',
  'Encrypting simulated files...',
  'Establishing communication channel...',
];

function LoadingOverlay() {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="text-center">
        {/* Animated skull/lock icon */}
        <div className="relative mb-8">
          <div className="w-24 h-24 mx-auto">
            <svg
              className="w-full h-full text-red-500 animate-pulse"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <circle cx="12" cy="16" r="1" fill="currentColor" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>
          {/* Rotating ring */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 border-4 border-red-500/20 border-t-red-500 rounded-full animate-spin" />
          </div>
        </div>

        {/* Loading message */}
        <p className="text-xl text-red-400 font-mono mb-4 min-h-[28px] transition-opacity duration-300">
          {LOADING_MESSAGES[messageIndex]}
        </p>

        {/* Progress dots */}
        <div className="flex justify-center gap-2">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 bg-red-500 rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>

        {/* Binary rain effect */}
        <div className="mt-8 text-green-500/30 font-mono text-xs overflow-hidden h-16">
          <div className="animate-pulse">
            {Array.from({ length: 3 }, (_, i) => (
              <div key={i} className="whitespace-nowrap">
                {Array.from({ length: 50 }, () => Math.round(Math.random())).join(' ')}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ConfigurePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isDemo = searchParams.get('demo') === 'true';

  // Form state
  const [organizationSize, setOrganizationSize] = useState<OrganizationSize>('medium');
  const [industry, setIndustry] = useState<string>('Healthcare');
  const [dataSensitivity, setDataSensitivity] = useState<DataSensitivity>('high');
  const [personaType, setPersonaType] = useState<PersonaType>('professional');
  const [difficulty, setDifficulty] = useState<number>(5);

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartSimulation = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Create scenario request
      const scenarioRequest: ScenarioCreateRequest = {
        organization: {
          size: organizationSize,
          industry,
          data_sensitivity: dataSensitivity,
        },
        persona_type: personaType,
        difficulty,
      };

      // Generate scenario
      const scenario = await generateScenario(scenarioRequest);

      // Start negotiation with scenario
      const negotiation = await startNegotiation({
        scenario_id: scenario.id,
        persona_type: personaType,
      });

      // Store scenario and client token in session storage for the negotiation page
      sessionStorage.setItem(`scenario_${negotiation.session_id}`, JSON.stringify(scenario));
      if (negotiation.client_token) {
        sessionStorage.setItem(`client_token_${negotiation.session_id}`, negotiation.client_token);
      }

      // Navigate to negotiation page
      router.push(`/negotiate/${negotiation.session_id}`);
    } catch (err) {
      console.error('Failed to start simulation:', err);
      setError(err instanceof Error ? err.message : 'Failed to start simulation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoMode = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Use demo preset: Healthcare, Professional
      const demoRequest: ScenarioCreateRequest = {
        organization: {
          size: 'medium',
          industry: 'Healthcare',
          data_sensitivity: 'critical',
        },
        persona_type: 'professional',
        difficulty: 7,
      };

      const scenario = await generateScenario(demoRequest);
      const negotiation = await startNegotiation({
        scenario_id: scenario.id,
        persona_type: 'professional',
      });

      // Store scenario and client token in session storage for the negotiation page
      sessionStorage.setItem(`scenario_${negotiation.session_id}`, JSON.stringify(scenario));
      if (negotiation.client_token) {
        sessionStorage.setItem(`client_token_${negotiation.session_id}`, negotiation.client_token);
      }

      router.push(`/negotiate/${negotiation.session_id}`);
    } catch (err) {
      console.error('Failed to start demo:', err);
      setError(err instanceof Error ? err.message : 'Failed to start demo. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white">
      {/* Loading Overlay */}
      {isLoading && <LoadingOverlay />}

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
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Configure Your Scenario</h1>
          <p className="text-zinc-400 mb-8">
            Set up your organization profile and select the type of threat actor you want to face.
          </p>

          {error && (
            <Alert className="mb-6 bg-red-900/20 border-red-600/50">
              <AlertDescription className="text-red-400">{error}</AlertDescription>
            </Alert>
          )}

          {isDemo ? (
            <Card className="bg-zinc-800/50 border-zinc-700 mb-8">
              <CardHeader>
                <CardTitle className="text-zinc-100">Quick Demo Mode</CardTitle>
                <CardDescription className="text-zinc-400">
                  Jump straight into a pre-configured scenario: Healthcare organization facing a professional threat actor.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={handleDemoMode}
                  disabled={isLoading}
                  className="bg-red-600 hover:bg-red-700"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Starting Demo...
                    </span>
                  ) : 'Start Demo Scenario'}
                </Button>
                <Link href="/configure" className="ml-4">
                  <Button variant="outline" className="border-zinc-600">
                    Customize Instead
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : null}

          <div className="grid md:grid-cols-2 gap-8">
            {/* Organization Profile */}
            <Card className="bg-zinc-800/50 border-zinc-700">
              <CardHeader>
                <CardTitle className="text-zinc-100">Organization Profile</CardTitle>
                <CardDescription className="text-zinc-400">
                  Define your simulated organization
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Organization Size */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-200">Organization Size</label>
                  <Select value={organizationSize} onValueChange={(v) => setOrganizationSize(v as OrganizationSize)}>
                    <SelectTrigger className="bg-zinc-900 border-zinc-700 text-zinc-100">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-700">
                      <SelectItem value="small" className="text-zinc-100">Small (&lt; 100 employees)</SelectItem>
                      <SelectItem value="medium" className="text-zinc-100">Medium (100-500 employees)</SelectItem>
                      <SelectItem value="large" className="text-zinc-100">Large (500-5000 employees)</SelectItem>
                      <SelectItem value="enterprise" className="text-zinc-100">Enterprise (5000+ employees)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Industry */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-200">Industry</label>
                  <Select value={industry} onValueChange={setIndustry}>
                    <SelectTrigger className="bg-zinc-900 border-zinc-700 text-zinc-100">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-700">
                      {INDUSTRIES.map((ind) => (
                        <SelectItem key={ind} value={ind} className="text-zinc-100">{ind}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Data Sensitivity */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-200">Data Sensitivity</label>
                  <Select value={dataSensitivity} onValueChange={(v) => setDataSensitivity(v as DataSensitivity)}>
                    <SelectTrigger className="bg-zinc-900 border-zinc-700 text-zinc-100">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-700">
                      <SelectItem value="low" className="text-zinc-100">Low - General business data</SelectItem>
                      <SelectItem value="medium" className="text-zinc-100">Medium - Some PII/financial data</SelectItem>
                      <SelectItem value="high" className="text-zinc-100">High - Sensitive PII, financial records</SelectItem>
                      <SelectItem value="critical" className="text-zinc-100">Critical - PHI, regulated data, IP</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Difficulty */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-200">Difficulty Level: {difficulty}</label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={difficulty}
                    onChange={(e) => setDifficulty(parseInt(e.target.value))}
                    className="w-full h-2 rounded-full appearance-none cursor-pointer accent-amber-600 bg-zinc-700 slider-range"
                  />
                  <div className="flex justify-between text-xs text-zinc-400">
                    <span>Easy</span>
                    <span>Realistic</span>
                    <span>Expert</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Threat Actor Selection */}
            <Card className="bg-zinc-800/50 border-zinc-700">
              <CardHeader>
                <CardTitle className="text-zinc-100">Select Threat Actor</CardTitle>
                <CardDescription className="text-zinc-400">
                  Choose the type of adversary you want to negotiate with
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(PERSONA_INFO).map(([key, persona]) => (
                  <div
                    key={key}
                    onClick={() => setPersonaType(key as PersonaType)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      personaType === key
                        ? 'border-red-500 bg-red-500/10'
                        : 'border-zinc-700 hover:border-zinc-600'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-zinc-100">{persona.name}</span>
                      <Badge
                        variant="outline"
                        className={
                          persona.difficulty === 'Hard'
                            ? 'border-red-500 text-red-400'
                            : persona.difficulty === 'Medium'
                            ? 'border-amber-500 text-amber-400'
                            : 'border-green-500 text-green-400'
                        }
                      >
                        {persona.difficulty}
                      </Badge>
                    </div>
                    <p className="text-sm text-zinc-400">{persona.description}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Start Button */}
          <div className="mt-8 flex justify-center">
            <Button
              onClick={handleStartSimulation}
              disabled={isLoading}
              size="lg"
              className="bg-red-600 hover:bg-red-700 px-12 py-6 text-lg"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating Scenario...
                </span>
              ) : 'Launch Simulation'}
            </Button>
          </div>

          {/* Info Card */}
          <Card className="mt-8 bg-zinc-800/30 border-zinc-700">
            <CardContent className="py-6">
              <h3 className="font-semibold mb-2 text-zinc-100">What happens next?</h3>
              <ol className="text-sm text-zinc-400 space-y-2 list-decimal list-inside">
                <li>AI generates a realistic breach scenario based on your profile</li>
                <li>You&apos;ll receive an initial ransom demand from the threat actor</li>
                <li>Negotiate in real-time via chat interface</li>
                <li>After concluding, receive detailed analysis of your performance</li>
              </ol>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

export default function ConfigurePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white flex items-center justify-center">
        <div className="text-zinc-400">Loading configuration...</div>
      </div>
    }>
      <ConfigurePageContent />
    </Suspense>
  );
}
