import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Brain, Sparkles, Lock, Mail, ArrowRight, Loader2, ShieldCheck, Database, Search } from 'lucide-react';
import { ScaleIn } from '@/components/shared/motion';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate('/');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background text-foreground relative overflow-hidden p-6 selection:bg-primary/20 selection:text-primary">
      {/* Background Mesh Gradients */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-1/4 left-1/4 w-[700px] h-[700px] bg-primary/15 rounded-full blur-[150px] animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-[700px] h-[700px] bg-purple-600/15 rounded-full blur-[150px] animate-pulse" />
      </div>

      <ScaleIn className="w-full max-w-2xl relative z-10">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-8 space-y-3">
          <div className="relative flex h-18 w-18 items-center justify-center rounded-2xl bg-gradient-to-br from-primary via-blue-600 to-indigo-600 shadow-xl shadow-primary/30 glow-md">
            <Brain className="h-10 w-10 text-white" />
            <Sparkles className="absolute -top-1 -right-1 h-5 w-5 text-sky-300 animate-pulse" />
          </div>
          <h1 className="text-5xl lg:text-6xl font-sketch font-bold tracking-wide text-foreground">
            ATLAS
          </h1>
          <p className="text-base text-muted-foreground font-semibold">
            Sign in to access your intelligent document workspace
          </p>
        </div>

        {/* Form Card */}
        <Card className="glass-card border border-border shadow-2xl p-10 md:p-12 rounded-3xl">
          <CardHeader className="space-y-2 pb-6 p-0">
            <CardTitle className="text-3xl font-black text-center text-foreground">Welcome Back</CardTitle>
            <CardDescription className="text-center text-base font-semibold text-muted-foreground">
              Enter your credentials to manage your knowledge bases
            </CardDescription>
          </CardHeader>

          <CardContent className="p-0 pt-6">
            {error && (
              <Alert variant="destructive" className="mb-6 text-base py-3.5 font-bold rounded-xl">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2.5">
                <Label htmlFor="email" className="text-base font-bold">Email Address</Label>
                <div className="relative flex items-center">
                  <Mail className="absolute left-4 z-10 h-5 w-5 text-muted-foreground pointer-events-none" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{ paddingLeft: '3.5rem' }}
                    className="h-14 text-lg font-medium rounded-xl"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password" className="text-base font-bold">Password</Label>
                </div>
                <div className="relative flex items-center">
                  <Lock className="absolute left-4 z-10 h-5 w-5 text-muted-foreground pointer-events-none" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{ paddingLeft: '3.5rem' }}
                    className="h-14 text-lg font-medium rounded-xl"
                    required
                  />
                </div>
              </div>

              <Button type="submit" size="lg" className="w-full gap-3 mt-4 h-14 text-lg font-extrabold shadow-lg shadow-primary/25 rounded-xl" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </Button>
            </form>

            <div className="mt-8 text-center text-base font-semibold text-muted-foreground">
              Don't have an account?{' '}
              <Link to="/register" className="font-extrabold text-primary hover:underline">
                Create Account
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Feature Highlights */}
        <div className="mt-10 flex flex-wrap justify-center items-center gap-8 text-base font-bold text-muted-foreground">
          <span className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" /> Enterprise Grade
          </span>
          <span className="flex items-center gap-2">
            <Database className="h-5 w-5 text-purple-500" /> Hybrid Search
          </span>
          <span className="flex items-center gap-2">
            <Search className="h-5 w-5 text-emerald-500" /> Fast RAG
          </span>
        </div>
      </ScaleIn>
    </div>
  );
}
