'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { PERSONA_INFO } from '@/types';

const EXAMPLE_CONVERSATION = [
  {
    sender: 'ai' as const,
    label: 'Threat Actor',
    content:
      'We have encrypted your entire network and exfiltrated 2.4TB of data including patient records, financial documents, and employee PII. The price for the decryption key and deletion of your data is $2,800,000 in Bitcoin. You have 72 hours. Do not contact law enforcement or we publish everything.',
    tactic: null,
  },
  {
    sender: 'user' as const,
    label: 'You',
    content:
      'We have received your message. Before we discuss anything further, we need to verify that you actually have access to our systems. Can you provide a sample of the data you claim to have, or decrypt a test file for us?',
    tactic: 'Requesting Proof of Access',
  },
  {
    sender: 'ai' as const,
    label: 'Threat Actor',
    content:
      'Attached is a decrypted copy of your Q3 financial report and a sample of 500 patient records from your cardiology department. We trust this is sufficient proof. The clock is ticking \u2014 68 hours remain.',
    tactic: null,
  },
  {
    sender: 'user' as const,
    label: 'You',
    content:
      'We acknowledge you have our data. However, I need to be transparent \u2014 I am not the final decision-maker here. Our board must approve any payment, and they are currently convening an emergency session. The amount you are asking is far beyond what we could authorize. Can we discuss a more realistic figure?',
    tactic: 'Claiming Limited Authority',
  },
  {
    sender: 'ai' as const,
    label: 'Threat Actor',
    content:
      'We understand organizational processes. However, our price reflects the value of your data. We could consider $2,200,000 if payment is received within 48 hours. This is our only concession.',
    tactic: null,
  },
  {
    sender: 'user' as const,
    label: 'You',
    content:
      'We appreciate the willingness to negotiate. Our board has reviewed the situation but our cyber insurance only covers up to $500,000 for incidents like this, and our available reserves are limited. We could potentially get approval for $750,000 if you can also guarantee and demonstrate full deletion of the exfiltrated data. Can you provide proof of your deletion capability?',
    tactic: 'Anchoring Low & Requesting Proof of Deletion',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-900 to-black text-white">
      {/* Training Simulation Banner */}
      <div className="bg-amber-600 text-black text-center py-2 text-sm font-medium">
        TRAINING SIMULATION ONLY - Not for real incident response
      </div>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="outline" className="mb-4 border-red-500 text-red-400">
            Cybersecurity Training Platform
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold mb-6 pb-2 leading-tight md:leading-tight bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-amber-500">
            RansomSim: AI‑Driven Ransomware Negotiation Training
          </h1>
          <p className="text-xl md:text-2xl text-zinc-400 mb-8 max-w-2xl mx-auto">
            Practice the negotiation you hope you&apos;ll never have — in a safe environment where mistakes don&apos;t cost millions.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/configure">
              <Button size="lg" className="bg-red-600 hover:bg-red-700 text-white px-8 py-6 text-lg">
                Start Simulation
              </Button>
            </Link>
            <Link href="/configure?demo=true">
              <Button size="lg" variant="outline" className="border-zinc-600 text-zinc-300 hover:bg-zinc-800 px-8 py-6 text-lg">
                Quick Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Problem Statement */}
      <section className="bg-zinc-900/50 py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl md:text-3xl font-bold mb-6">The Problem</h2>
            <p className="text-lg text-zinc-400 mb-8">
              Every 11 seconds, a business falls victim to ransomware. When it happens,
              most organizations are completely unprepared for what comes next: <span className="text-white font-semibold">the negotiation</span>.
            </p>
            <div className="grid md:grid-cols-3 gap-6 text-left">
              <Card className="bg-zinc-800/50 border-zinc-700">
                <CardHeader>
                  <CardTitle className="text-red-400 text-lg">Poor Decisions</CardTitle>
                </CardHeader>
                <CardContent className="text-zinc-400">
                  Under extreme pressure, teams make costly mistakes that could have been avoided with training.
                </CardContent>
              </Card>
              <Card className="bg-zinc-800/50 border-zinc-700">
                <CardHeader>
                  <CardTitle className="text-red-400 text-lg">Overpayment</CardTitle>
                </CardHeader>
                <CardContent className="text-zinc-400">
                  Without experience, victims often pay more than necessary or make dangerous concessions.
                </CardContent>
              </Card>
              <Card className="bg-zinc-800/50 border-zinc-700">
                <CardHeader>
                  <CardTitle className="text-red-400 text-lg">Compliance Risks</CardTitle>
                </CardHeader>
                <CardContent className="text-zinc-400">
                  Legal and regulatory missteps during negotiations can compound the damage.
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Threat Actor Personas */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">Face Different Adversaries</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {Object.entries(PERSONA_INFO).map(([key, persona]) => (
                <Card key={key} className="bg-zinc-800/50 border-zinc-700 hover:border-zinc-600 transition-colors">
                  <CardHeader>
                    <div className="flex items-center justify-between mb-2">
                      <CardTitle className="text-lg">{persona.name}</CardTitle>
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
                    <CardDescription className="text-zinc-400">
                      {persona.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-zinc-900/50 py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">How It Works</h2>
            <div className="space-y-8">
              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-600/20 text-red-500 flex items-center justify-center text-xl font-bold">
                  1
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Configure Your Scenario</h3>
                  <p className="text-zinc-400">
                    Select your organization profile, industry, and the type of threat actor you want to face.
                  </p>
                </div>
              </div>
              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-600/20 text-red-500 flex items-center justify-center text-xl font-bold">
                  2
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Negotiate with AI</h3>
                  <p className="text-zinc-400">
                    Engage in realistic negotiations with an AI-powered threat actor that adapts to your tactics.
                  </p>
                </div>
              </div>
              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-600/20 text-red-500 flex items-center justify-center text-xl font-bold">
                  3
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Get Expert Analysis</h3>
                  <p className="text-zinc-400">
                    Receive detailed feedback on your performance, including tactical insights and improvement recommendations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Example Negotiation */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-3 text-center">
              See a Negotiation in Action
            </h2>
            <p className="text-zinc-400 text-center mb-8 max-w-2xl mx-auto">
              Here&apos;s a sample exchange against <span className="text-white font-semibold">The Professional</span> persona,
              annotated with the key tactics being used.
            </p>

            <Card className="bg-zinc-800/50 border-zinc-700">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <CardTitle className="text-lg">Sample Negotiation</CardTitle>
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className="border-red-500 text-red-400">
                      Professional
                    </Badge>
                    <Badge variant="outline" className="border-zinc-600 text-zinc-400">
                      Healthcare Scenario
                    </Badge>
                  </div>
                </div>
              </CardHeader>

              <Separator className="bg-zinc-700" />

              <CardContent className="pt-6">
                <div className="space-y-4">
                  {EXAMPLE_CONVERSATION.map((message, index) => (
                    <div key={index}>
                      {message.sender === 'ai' ? (
                        <div className="flex justify-start">
                          <div className="max-w-[80%] rounded-lg p-4 bg-zinc-700 text-zinc-100">
                            <div className="text-xs mb-1 opacity-70">{message.label}</div>
                            <div className="text-sm leading-relaxed">{message.content}</div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex flex-col items-end">
                          <div className="max-w-[80%] rounded-lg p-4 bg-blue-600 text-white">
                            <div className="text-xs mb-1 opacity-70">{message.label}</div>
                            <div className="text-sm leading-relaxed">{message.content}</div>
                          </div>
                          {message.tactic && (
                            <Badge
                              variant="outline"
                              className="mt-1.5 border-amber-500/60 text-amber-400 text-xs font-normal"
                            >
                              Tactic: {message.tactic}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  ))}

                  <div className="flex justify-start">
                    <div className="bg-zinc-700/50 text-zinc-500 rounded-lg px-4 py-3 text-sm italic">
                      Negotiation continues...
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="mt-6 text-center">
              <p className="text-sm text-zinc-500 mb-3">Key tactics demonstrated:</p>
              <div className="flex flex-wrap justify-center gap-2">
                <Badge variant="outline" className="border-amber-500/40 text-amber-400/80 text-xs">
                  Verify Data Access
                </Badge>
                <Badge variant="outline" className="border-amber-500/40 text-amber-400/80 text-xs">
                  Claim Limited Authority
                </Badge>
                <Badge variant="outline" className="border-amber-500/40 text-amber-400/80 text-xs">
                  Anchor Low
                </Badge>
                <Badge variant="outline" className="border-amber-500/40 text-amber-400/80 text-xs">
                  Request Proof of Deletion
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Ethical Disclaimer */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <Alert className="bg-zinc-800/50 border-amber-600/50">
              <AlertTitle className="text-amber-500 text-lg font-semibold">Important Notice</AlertTitle>
              <AlertDescription className="text-zinc-400 mt-2 space-y-2">
                <p>
                  This is a <strong className="text-white">training simulation only</strong>. It is not a substitute for
                  professional incident response services or legal advice.
                </p>
                <p>
                  If you are experiencing a real ransomware incident, contact law enforcement immediately:
                </p>
                <ul className="list-disc list-inside mt-2">
                  <li>FBI Internet Crime Complaint Center (IC3): <a href="https://www.ic3.gov" className="text-amber-400 hover:underline">ic3.gov</a></li>
                  <li>CISA: <a href="https://www.cisa.gov/stopransomware" className="text-amber-400 hover:underline">cisa.gov/stopransomware</a></li>
                </ul>
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-2xl md:text-3xl font-bold mb-4">Ready to Train?</h2>
          <p className="text-zinc-400 mb-8 max-w-xl mx-auto">
            Don&apos;t wait until you&apos;re under attack. Practice makes prepared.
          </p>
          <Link href="/configure">
            <Button size="lg" className="bg-red-600 hover:bg-red-700 text-white px-8 py-6 text-lg">
              Start Your First Simulation
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800 py-8">
        <div className="container mx-auto px-4 text-center text-zinc-500 text-sm">
          <p>RansomSim: AI‑Driven Ransomware Negotiation Training - A Gemini 3 Hackathon Project</p>
          <p className="mt-2">Built for educational purposes only.</p>
        </div>
      </footer>
    </div>
  );
}
