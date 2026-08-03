import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Brain, Sparkles, Lock, Mail, User, Building, ArrowRight, Loader2 } from 'lucide-react';
import { ScaleIn } from '@/components/shared/motion';

export default function RegisterPage() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    organization_name: '',
    department: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register, isAuthenticated } = useAuth();
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
      await register({
        name: form.name,
        email: form.email,
        password: form.password,
        organization_name: form.organization_name || undefined,
        department: form.department || undefined,
      });
      navigate('/');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };



  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background text-foreground relative overflow-hidden p-6 selection:bg-primary/20 selection:text-primary">
      {/* Ambient Lighting */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-1/3 right-1/4 w-[700px] h-[700px] bg-primary/15 rounded-full blur-[150px] animate-pulse" />
        <div className="absolute bottom-1/3 left-1/4 w-[700px] h-[700px] bg-indigo-600/15 rounded-full blur-[150px] animate-pulse" />
      </div>

      <ScaleIn className="w-full max-w-2xl relative z-10 my-8">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-8 space-y-3">
          <div className="relative flex h-18 w-18 items-center justify-center rounded-2xl bg-gradient-to-br from-primary via-blue-600 to-indigo-600 shadow-xl shadow-primary/30 glow-md">
            <Brain className="h-10 w-10 text-white" />
            <Sparkles className="absolute -top-1 -right-1 h-4.5 w-4.5 text-sky-300 animate-pulse" />
          </div>
          <h1 className="text-4xl lg:text-5xl font-black tracking-tight text-foreground">
            Create Your Account
          </h1>
          <p className="text-base text-muted-foreground font-semibold">
            Get started with ATLAS in less than two minutes
          </p>
        </div>

        {/* Form Card */}
        <Card className="glass-card border border-border shadow-2xl p-10 md:p-12 rounded-3xl">
          <CardContent className="p-0">
            {error && (
              <Alert variant="destructive" className="mb-6 text-base py-3.5 font-bold rounded-xl">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-base font-bold">Full Name</Label>
                  <div className="relative flex items-center">
                    <User className="absolute left-4 z-10 h-5 w-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="name"
                      placeholder="Jane Doe"
                      value={form.name}
                      onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                      style={{ paddingLeft: '3.5rem' }}
                      className="h-14 text-lg font-medium rounded-xl"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-base font-bold">Work Email</Label>
                  <div className="relative flex items-center">
                    <Mail className="absolute left-4 z-10 h-5 w-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="jane@company.com"
                      value={form.email}
                      onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                      style={{ paddingLeft: '3.5rem' }}
                      className="h-14 text-lg font-medium rounded-xl"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-base font-bold">Password</Label>
                <div className="relative flex items-center">
                  <Lock className="absolute left-4 z-10 h-5 w-5 text-muted-foreground pointer-events-none" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="At least 6 characters"
                    value={form.password}
                    onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                    style={{ paddingLeft: '3.5rem' }}
                    className="h-14 text-lg font-medium rounded-xl"
                    required
                    minLength={6}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div className="space-y-2">
                  <Label htmlFor="org" className="text-base font-bold">Organization (Optional)</Label>
                  <div className="relative flex items-center">
                    <Building className="absolute left-4 z-10 h-5 w-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="org"
                      placeholder="Acme Inc."
                      value={form.organization_name}
                      onChange={(e) => setForm((p) => ({ ...p, organization_name: e.target.value }))}
                      style={{ paddingLeft: '3.5rem' }}
                      className="h-14 text-lg font-medium rounded-xl"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="dept" className="text-base font-bold">Department (Optional)</Label>
                  <Input
                    id="dept"
                    placeholder="Engineering / Sales"
                    value={form.department}
                    onChange={(e) => setForm((p) => ({ ...p, department: e.target.value }))}
                    className="h-14 text-lg font-medium rounded-xl px-5"
                  />
                </div>
              </div>

              <Button type="submit" size="lg" className="w-full gap-3 mt-4 h-14 text-lg font-extrabold shadow-lg shadow-primary/25 rounded-xl" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  <>
                    Complete Registration
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </Button>
            </form>

            <div className="mt-8 text-center text-base font-semibold text-muted-foreground">
              Already have an account?{' '}
              <Link to="/login" className="font-bold text-primary hover:underline">
                Sign In
              </Link>
            </div>
          </CardContent>
        </Card>
      </ScaleIn>
    </div>
  );
}
