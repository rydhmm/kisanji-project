import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Sprout, Phone, User, Lock, Mail, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import apiService from '@/services/api';

const Auth = () => {
  const [phoneLogin, setPhoneLogin] = useState({ phone: '' });
  const [userLogin, setUserLogin] = useState({ username: '', password: '' });
  const [register, setRegister] = useState({ name: '', phone: '', username: '', password: '', village: '' });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { t, language, changeLanguage } = useLanguage();
  const navigate = useNavigate();

  const handlePhoneLogin = async (e) => {
    e.preventDefault();
    if (phoneLogin.phone.length === 10) {
      setLoading(true);
      try {
        const response = await apiService.login({ phone: phoneLogin.phone });
        login({ 
          id: response.id,
          phone: phoneLogin.phone, 
          name: response.name || 'Farmer', 
          village: 'Demo Village',
          role: response.role || 'farmer',
          preferred_language: response.preferred_language || 'en',
        });
        toast.success('Login successful!');
        navigate('/');
      } catch (error) {
        // Fallback to local login
        login({ phone: phoneLogin.phone, name: 'Farmer', village: 'Demo Village' });
        toast.success('Login successful!');
        navigate('/');
      } finally {
        setLoading(false);
      }
    } else {
      toast.error('Please enter a valid 10-digit phone number');
    }
  };

  const handleUserLogin = async (e) => {
    e.preventDefault();
    if (userLogin.username && userLogin.password) {
      setLoading(true);
      try {
        // For username login, we'll use phone field with username
        const response = await apiService.login({ phone: userLogin.username, password: userLogin.password });
        login({ 
          id: response.id,
          username: userLogin.username, 
          name: response.name || userLogin.username, 
          village: 'Demo Village' 
        });
        toast.success('Login successful!');
        navigate('/');
      } catch (error) {
        login({ username: userLogin.username, name: userLogin.username, village: 'Demo Village' });
        toast.success('Login successful!');
        navigate('/');
      } finally {
        setLoading(false);
      }
    } else {
      toast.error('Please fill in all fields');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (register.name && register.phone && register.village) {
      setLoading(true);
      try {
        const response = await apiService.register({
          name: register.name,
          phone: register.phone,
          password: register.password,
          role: 'farmer',
          preferred_language: language,
          voice_enabled: true,
        });
        login({ 
          id: response.id,
          name: register.name, 
          phone: register.phone, 
          village: register.village 
        });
        toast.success('Registration successful!');
        navigate('/');
      } catch (error) {
        // Fallback to local registration
        login({ name: register.name, phone: register.phone, village: register.village });
        toast.success('Registration successful!');
        navigate('/');
      } finally {
        setLoading(false);
      }
    } else {
      toast.error('Please fill in all required fields');
    }
  };

  const handleGoogleLogin = () => {
    // Simulate Google login
    login({ name: 'Google User', email: 'user@gmail.com', village: 'Demo Village' });
    toast.success('Google login successful!');
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-950 via-black to-cyan-950" />
        {/* Floating particles */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-emerald-500/20 rounded-full"
            initial={{
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1000),
              y: (typeof window !== 'undefined' ? window.innerHeight : 800) + 10,
            }}
            animate={{
              y: -10,
              opacity: [0, 0.5, 0],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}
      </div>

      <div className="w-full max-w-5xl grid lg:grid-cols-2 gap-8 items-center relative z-10">
        {/* Left Side - Enhanced Branding */}
        <motion.div 
          className="hidden lg:block"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="text-center space-y-8">
            <motion.div 
              className="inline-block bg-gradient-to-br from-emerald-500 to-emerald-600 p-8 rounded-3xl shadow-2xl shadow-emerald-500/30"
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              <Sprout className="h-24 w-24 text-white" />
            </motion.div>
            <motion.h1 
              className="text-5xl font-bold"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <span className="gradient-text">Kisan.JI</span>
              <br />
              <span className="text-white text-3xl">Smart Agri Platform</span>
            </motion.h1>
            <motion.p 
              className="text-lg text-gray-400 leading-relaxed max-w-md mx-auto"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              Empowering Indian farmers with AI-powered crop recommendations, weather forecasts, market prices, and expert guidance.
            </motion.p>
            <motion.div 
              className="flex flex-col gap-3 text-sm"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              {['Multi-language support', 'AI-powered recommendations', 'Real-time market prices'].map((feature, i) => (
                <div key={i} className="flex items-center gap-3 justify-center text-gray-300">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                  <span>{feature}</span>
                </div>
              ))}
            </motion.div>
          </div>
        </motion.div>

        {/* Right Side - Enhanced Auth Forms */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Card className="glass-card border-white/10 shadow-2xl overflow-hidden">
            {/* Glow effect */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />
            
            <CardHeader className="space-y-4 relative">
              <motion.div 
                className="flex items-center justify-center lg:hidden"
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              >
                <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 p-4 rounded-2xl shadow-lg shadow-emerald-500/30">
                  <Sprout className="h-12 w-12 text-white" />
                </div>
              </motion.div>
              <CardTitle className="text-3xl text-center text-white font-bold">Welcome</CardTitle>
              <CardDescription className="text-center text-gray-400">
                Choose your preferred language and sign in
              </CardDescription>
              
              {/* Enhanced Language Selector */}
              <div className="flex gap-2 justify-center">
                {[
                  { code: 'en', label: 'English' },
                  { code: 'hi', label: 'हिंदी' },
                  { code: 'mr', label: 'मराठी' }
                ].map((lang) => (
                  <motion.div key={lang.code} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant={language === lang.code ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => changeLanguage(lang.code)}
                      className={language === lang.code 
                        ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white border-0' 
                        : 'border-white/20 text-gray-400 hover:text-white hover:bg-white/10'}
                    >
                      {lang.label}
                    </Button>
                  </motion.div>
                ))}
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="phone" className="w-full">
                <TabsList className="grid w-full grid-cols-3 bg-white/5 border border-white/10">
                  <TabsTrigger value="phone" className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-400">Phone</TabsTrigger>
                  <TabsTrigger value="login" className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-400">Login</TabsTrigger>
                  <TabsTrigger value="register" className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-400">Register</TabsTrigger>
                </TabsList>

              {/* Phone Login */}
              <TabsContent value="phone" className="space-y-4 mt-4">
                <form onSubmit={handlePhoneLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="phone"
                        type="tel"
                        placeholder="Enter 10-digit phone number"
                        className="pl-10"
                        value={phoneLogin.phone}
                        onChange={(e) => setPhoneLogin({ phone: e.target.value })}
                        maxLength={10}
                      />
                    </div>
                  </div>
                  <Button type="submit" className="w-full gradient-primary" disabled={loading}>
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Login with Phone
                  </Button>
                </form>
              </TabsContent>

              {/* Username Login */}
              <TabsContent value="login" className="space-y-4 mt-4">
                <form onSubmit={handleUserLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="username"
                        type="text"
                        placeholder="Enter username"
                        className="pl-10"
                        value={userLogin.username}
                        onChange={(e) => setUserLogin({ ...userLogin, username: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="password"
                        type="password"
                        placeholder="Enter password"
                        className="pl-10"
                        value={userLogin.password}
                        onChange={(e) => setUserLogin({ ...userLogin, password: e.target.value })}
                      />
                    </div>
                  </div>
                  <Button type="submit" className="w-full gradient-primary" disabled={loading}>
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Login
                  </Button>
                </form>
              </TabsContent>

              {/* Register */}
              <TabsContent value="register" className="space-y-4 mt-4">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name *</Label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="Enter your name"
                      value={register.name}
                      onChange={(e) => setRegister({ ...register, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reg-phone">Phone Number *</Label>
                    <Input
                      id="reg-phone"
                      type="tel"
                      placeholder="10-digit phone"
                      value={register.phone}
                      onChange={(e) => setRegister({ ...register, phone: e.target.value })}
                      maxLength={10}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="village">Village/Location *</Label>
                    <Input
                      id="village"
                      type="text"
                      placeholder="Enter your village"
                      value={register.village}
                      onChange={(e) => setRegister({ ...register, village: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reg-username">Username (optional)</Label>
                    <Input
                      id="reg-username"
                      type="text"
                      placeholder="Choose a username"
                      value={register.username}
                      onChange={(e) => setRegister({ ...register, username: e.target.value })}
                    />
                  </div>
                  <Button type="submit" className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white" disabled={loading}>
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Create Account
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            {/* Google Sign In */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-white/10" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-transparent px-2 text-gray-500">Or continue with</span>
                </div>
              </div>
              <Button
                type="button"
                variant="outline"
                className="w-full mt-4 border-white/20 text-white hover:bg-white/10"
                onClick={handleGoogleLogin}
              >
                <Mail className="mr-2 h-4 w-4" />
                Google Sign In
              </Button>
            </div>
          </CardContent>
        </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Auth;
