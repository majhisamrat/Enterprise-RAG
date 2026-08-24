import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Brain, Sparkles, Lock, Mail, User, Building, ArrowRight, Loader2, CheckCircle, ArrowLeft } from 'lucide-react';
import { ScaleIn } from '@/components/shared/motion';

type RegistrationStep = 'form' | 'otp' | 'success';

export default function RegisterPage() {
  const [step, setStep] = useState<RegistrationStep>('form');
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    organization_name: '',
    department: '',
  });
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleInitialSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Step 1: Send registration details and get OTP sent to email
      const response = await fetch('/api/v1/auth/register-init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          password: form.password,
          organization_name: form.organization_name || 'Default Enterprise',
          department: form.department || 'Engineering',
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to start registration');
      }

      setStep('otp');
      setError('');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to initiate registration');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Step 2: Verify OTP and create account
      const response = await fetch('/api/v1/auth/register-verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: form.email,
          otp: otp,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'OTP verification failed');
      }

      const data = await response.json();
      
      // Store tokens
      localStorage.setItem('access_token', data.access_token);
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }

      setStep('success');
      
      // Redirect to dashboard after success
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'OTP verification failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Google Sign-Up handler
  const handleGoogleSignUp = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      setError('');
      setIsLoading(true);
      try {
        const userInfoResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
          headers: { 'Authorization': `Bearer ${codeResponse.access_token}` },
        });
        
        if (!userInfoResponse.ok) {
          throw new Error('Failed to get Google user info');
        }

        const userInfo = await userInfoResponse.json();

        const backendResponse = await fetch('/api/v1/auth/google-login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            access_token: codeResponse.access_token,
            email: userInfo.email,
            name: userInfo.name,
            picture: userInfo.picture,
            organization_name: form.organization_name || 'Default Enterprise',
          }),
        });

        if (!backendResponse.ok) {
          const errorData = await backendResponse.json();
          throw new Error(errorData.detail || 'Google authentication failed');
        }

        const data = await backendResponse.json();
        
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }

        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 100);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Google Sign-Up failed');
      } finally {
        setIsLoading(false);
      }
    },
    onError: () => {
      setError('Google Sign-Up failed. Please try again.');
      setIsLoading(false);
    },
    flow: 'implicit',
  });

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background text-foreground relative overflow-hidden p-4 sm:p-6 selection:bg-primary/20 selection:text-primary">
      {/* Ambient Lighting */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-1/3 right-1/4 w-[700px] h-[700px] bg-primary/15 rounded-full blur-[150px] animate-pulse" />
        <div className="absolute bottom-1/3 left-1/4 w-[700px] h-[700px] bg-indigo-600/15 rounded-full blur-[150px] animate-pulse" />
      </div>

      <ScaleIn className="w-full max-w-sm md:max-w-2xl relative z-10 my-4 md:my-8">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-5 md:mb-8 space-y-2 md:space-y-3">
          <div className="relative flex h-12 md:h-18 w-12 md:w-18 items-center justify-center rounded-2xl bg-gradient-to-br from-primary via-blue-600 to-indigo-600 shadow-xl shadow-primary/30 glow-md">
            <Brain className="h-6 md:h-10 w-6 md:w-10 text-white" />
            <Sparkles className="absolute -top-0.5 -right-0.5 h-3 md:h-4.5 w-3 md:w-4.5 text-sky-300 animate-pulse" />
          </div>
          <h1 className="text-2xl md:text-4xl lg:text-5xl font-black tracking-tight text-foreground">
            {step === 'form' && 'Create Your Account'}
            {step === 'otp' && 'Verify Your Email'}
            {step === 'success' && 'Account Created!'}
          </h1>
          <p className="text-xs md:text-base text-muted-foreground font-semibold">
            {step === 'form' && 'Get started with ATLAS in less than two minutes'}
            {step === 'otp' && `We sent a code to ${form.email}`}
            {step === 'success' && 'Redirecting to dashboard...'}
          </p>
        </div>

        {/* Form Card */}
        <Card className="glass-card border border-border shadow-2xl p-5 md:p-10 lg:p-12 rounded-3xl">
          <CardContent className="p-0">
            {error && (
              <Alert variant="destructive" className="mb-4 md:mb-6 text-sm md:text-base py-2.5 md:py-3.5 font-bold rounded-xl">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Step 1: Registration Form */}
            {step === 'form' && (
              <>
                {/* Google Sign-Up Button */}
                <button 
                  type="button" 
                  onClick={() => handleGoogleSignUp()} 
                  disabled={isLoading}
                  className="flex h-12 md:h-14 w-full items-center justify-center gap-2 md:gap-3 rounded-full bg-[#1246b8] text-base md:text-lg font-bold text-white shadow-lg shadow-blue-900/20 transition hover:bg-[#0e3b99] disabled:opacity-50 disabled:cursor-not-allowed mb-4 md:mb-6"
                >
                  <span className="grid h-5 md:h-6 w-5 md:w-6 place-items-center rounded-full bg-white text-sm md:text-base font-black text-[#1246b8]">G</span>
                  {isLoading ? 'Creating account...' : 'Sign up with Google'}
                </button>

                <div className="relative mb-4 md:mb-6">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border/40"></span>
                  </div>
                  <div className="relative flex justify-center text-xs md:text-sm">
                    <span className="bg-card px-2 text-muted-foreground">Or continue with email</span>
                  </div>
                </div>

                <form onSubmit={handleInitialSubmit} className="space-y-4 md:space-y-6">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-5">
                    <div className="space-y-1.5 md:space-y-2">
                      <Label htmlFor="name" className="text-xs md:text-base font-bold">Full Name</Label>
                      <div className="relative flex items-center">
                        <User className="absolute left-3 md:left-4 z-10 h-4 md:h-5 w-4 md:w-5 text-muted-foreground pointer-events-none" />
                        <Input
                          id="name"
                          placeholder="Jane Doe"
                          value={form.name}
                          onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                          style={{ paddingLeft: '2.5rem' }}
                          className="h-10 md:h-14 text-sm md:text-lg font-medium rounded-xl"
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5 md:space-y-2">
                      <Label htmlFor="email" className="text-xs md:text-base font-bold">Work Email</Label>
                      <div className="relative flex items-center">
                        <Mail className="absolute left-3 md:left-4 z-10 h-4 md:h-5 w-4 md:w-5 text-muted-foreground pointer-events-none" />
                        <Input
                          id="email"
                          type="email"
                          placeholder="jane@company.com"
                          value={form.email}
                          onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                          style={{ paddingLeft: '2.5rem' }}
                          className="h-10 md:h-14 text-sm md:text-lg font-medium rounded-xl"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-1.5 md:space-y-2">
                    <Label htmlFor="password" className="text-xs md:text-base font-bold">Password</Label>
                    <div className="relative flex items-center">
                      <Lock className="absolute left-3 md:left-4 z-10 h-4 md:h-5 w-4 md:w-5 text-muted-foreground pointer-events-none" />
                      <Input
                        id="password"
                        type="password"
                        placeholder="At least 6 characters"
                        value={form.password}
                        onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                        style={{ paddingLeft: '2.5rem' }}
                        className="h-10 md:h-14 text-sm md:text-lg font-medium rounded-xl"
                        required
                        minLength={6}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-5">
                    <div className="space-y-1.5 md:space-y-2">
                      <Label htmlFor="org" className="text-xs md:text-base font-bold">Organization (Optional)</Label>
                      <div className="relative flex items-center">
                        <Building className="absolute left-3 md:left-4 z-10 h-4 md:h-5 w-4 md:w-5 text-muted-foreground pointer-events-none" />
                        <Input
                          id="org"
                          placeholder="Acme Inc."
                          value={form.organization_name}
                          onChange={(e) => setForm((p) => ({ ...p, organization_name: e.target.value }))}
                          style={{ paddingLeft: '2.5rem' }}
                          className="h-10 md:h-14 text-sm md:text-lg font-medium rounded-xl"
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5 md:space-y-2">
                      <Label htmlFor="dept" className="text-xs md:text-base font-bold">Department (Optional)</Label>
                      <Input
                        id="dept"
                        placeholder="Engineering / Sales"
                        value={form.department}
                        onChange={(e) => setForm((p) => ({ ...p, department: e.target.value }))}
                        className="h-10 md:h-14 text-sm md:text-lg font-medium rounded-xl px-3 md:px-5"
                      />
                    </div>
                  </div>

                  <Button type="submit" size="lg" className="w-full gap-2 md:gap-3 mt-2 md:mt-4 h-10 md:h-14 text-sm md:text-lg font-extrabold shadow-lg shadow-primary/25 rounded-xl" disabled={isLoading}>
                    {isLoading ? (
                      <>
                        <Loader2 className="h-4 md:h-5 w-4 md:w-5 animate-spin" />
                        Sending OTP...
                      </>
                    ) : (
                      <>
                        Complete Registration
                        <ArrowRight className="h-4 md:h-5 w-4 md:w-5" />
                      </>
                    )}
                  </Button>
                </form>

                <div className="mt-4 md:mt-8 text-center text-xs md:text-base font-semibold text-muted-foreground">
                  Already have an account?{' '}
                  <Link to="/login" className="font-bold text-primary hover:underline">
                    Sign In
                  </Link>
                </div>
              </>
            )}

            {/* Step 2: OTP Verification */}
            {step === 'otp' && (
              <form onSubmit={handleVerifyOTP} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="otp" className="text-sm md:text-base font-bold">6-Digit Code</Label>
                  <Input
                    id="otp"
                    type="text"
                    placeholder="000000"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    maxLength={6}
                    className="h-14 md:h-16 text-3xl font-bold text-center tracking-widest rounded-xl"
                    required
                  />
                  <p className="text-xs md:text-sm text-muted-foreground">Enter the code sent to your email</p>
                </div>

                <Button type="submit" size="lg" className="w-full gap-2 md:gap-3 h-12 md:h-14 text-base md:text-lg font-extrabold shadow-lg shadow-primary/25 rounded-xl" disabled={isLoading || otp.length !== 6}>
                  {isLoading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Verifying...
                    </>
                  ) : (
                    <>
                      Verify & Create Account
                      <ArrowRight className="h-5 w-5" />
                    </>
                  )}
                </Button>

                <button
                  type="button"
                  onClick={() => {
                    setStep('form');
                    setOtp('');
                    setError('');
                  }}
                  className="flex items-center gap-2 text-sm md:text-base font-semibold text-primary hover:underline mx-auto"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Registration
                </button>
              </form>
            )}

            {/* Step 3: Success */}
            {step === 'success' && (
              <div className="flex flex-col items-center justify-center py-8 md:py-12 text-center space-y-4">
                <div className="relative flex h-16 md:h-20 w-16 md:w-20 items-center justify-center rounded-full bg-green-500/20">
                  <CheckCircle className="h-10 md:h-12 w-10 md:w-12 text-green-600" />
                </div>
                <h2 className="text-xl md:text-2xl font-bold text-foreground">Account Created!</h2>
                <p className="text-sm md:text-base text-muted-foreground">Email verified and account ready to use</p>
                <p className="text-xs md:text-sm text-muted-foreground">Redirecting to dashboard...</p>
              </div>
            )}
          </CardContent>
        </Card>
      </ScaleIn>
    </div>
  );
}
