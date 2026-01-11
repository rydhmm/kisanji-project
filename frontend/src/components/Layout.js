import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Home, 
  Sprout, 
  CloudRain, 
  TrendingUp, 
  Bug, 
  Users, 
  User, 
  BookOpen, 
  FileText, 
  Calculator, 
  Phone,
  Menu,
  LogOut,
  Globe,
  Bell
} from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Layout = ({ children }) => {
  const { t, language, changeLanguage, availableLanguages } = useLanguage();
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const menuItems = [
    { icon: Home, label: t('dashboard'), path: '/', color: 'from-emerald-500 to-emerald-600' },
    { icon: Sprout, label: t('cropRecommendation'), path: '/crop-recommendation', color: 'from-green-500 to-green-600' },
    { icon: CloudRain, label: t('weather'), path: '/weather', color: 'from-blue-500 to-blue-600' },
    { icon: TrendingUp, label: t('marketPrices'), path: '/market-prices', color: 'from-amber-500 to-amber-600' },
    { icon: Bug, label: t('pestDetection'), path: '/pest-detection', color: 'from-red-500 to-red-600' },
    { icon: BookOpen, label: t('diseaseKnowledge'), path: '/disease-knowledge', color: 'from-purple-500 to-purple-600' },
    { icon: Users, label: t('community'), path: '/community', color: 'from-cyan-500 to-cyan-600' },
    { icon: FileText, label: t('schemes'), path: '/schemes', color: 'from-indigo-500 to-indigo-600' },
    { icon: Calculator, label: t('calculators'), path: '/calculators', color: 'from-teal-500 to-teal-600' },
    { icon: Phone, label: t('expertContact'), path: '/expert-contact', color: 'from-orange-500 to-orange-600' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  const languageNames = {
    en: 'English',
    hi: 'हिंदी',
    mr: 'मराठी',
  };

  return (
    <div className="min-h-screen relative">
      {/* Enhanced Top Navigation with Glassmorphism */}
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, type: 'spring' }}
        className="sticky top-0 z-50 glass border-b border-white/10 shadow-lg"
      >
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Mobile Menu */}
            <div className="flex items-center gap-3">
              <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
                <SheetTrigger asChild className="lg:hidden">
                  <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
                    <Menu className="h-6 w-6" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-72 p-0 glass border-r border-white/10">
                  <div className="gradient-primary p-6">
                    <div className="flex items-center gap-3">
                      <motion.div 
                        className="p-2 bg-white/20 rounded-xl"
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.5 }}
                      >
                        <Sprout className="h-8 w-8 text-white" />
                      </motion.div>
                      <div>
                        <h2 className="font-bold text-lg text-white">Kisan.JI</h2>
                        <p className="text-xs text-white/80">Smart Agri Platform</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 space-y-1">
                    {menuItems.map((item, index) => {
                      const Icon = item.icon;
                      const isActive = location.pathname === item.path;
                      return (
                        <motion.div
                          key={item.path}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <Link
                            to={item.path}
                            onClick={() => setMobileOpen(false)}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                              isActive
                                ? `bg-gradient-to-r ${item.color} text-white shadow-lg`
                                : 'text-gray-300 hover:bg-white/10 hover:text-white'
                            }`}
                          >
                            <Icon className="h-5 w-5" />
                            <span className="font-medium">{item.label}</span>
                          </Link>
                        </motion.div>
                      );
                    })}
                  </div>
                </SheetContent>
              </Sheet>

              <Link to="/" className="flex items-center gap-3 group">
                <motion.div 
                  className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-2.5 rounded-xl shadow-lg shadow-emerald-500/30"
                  whileHover={{ scale: 1.1, rotate: 10 }}
                  transition={{ type: 'spring', stiffness: 300 }}
                >
                  <Sprout className="h-6 w-6 text-white" />
                </motion.div>
                <div className="hidden sm:block">
                  <h1 className="font-bold text-xl text-white leading-none group-hover:text-emerald-400 transition-colors">
                    Kisan.JI
                  </h1>
                  <p className="text-xs text-gray-400">Smart Agri Platform</p>
                </div>
              </Link>
            </div>

            {/* Desktop Menu */}
            <div className="hidden lg:flex items-center gap-1">
              {menuItems.slice(0, 6).map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`relative flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                      isActive
                        ? 'text-white'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className={`absolute inset-0 bg-gradient-to-r ${item.color} rounded-xl shadow-lg`}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                      />
                    )}
                    <span className="relative z-10 flex items-center gap-2">
                      <Icon className="h-4 w-4" />
                      <span className="hidden xl:inline">{item.label}</span>
                    </span>
                  </Link>
                );
              })}
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center gap-2">
              {/* Notification Bell */}
              <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                <Button variant="ghost" size="icon" className="relative text-gray-400 hover:text-white hover:bg-white/10">
                  <Bell className="h-5 w-5" />
                  <span className="absolute top-1 right-1 w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                </Button>
              </motion.div>
              
              {/* Language Selector */}
              <Select value={language} onValueChange={changeLanguage}>
                <SelectTrigger className="w-[100px] bg-white/5 border-white/10 text-white hover:bg-white/10">
                  <Globe className="h-4 w-4 mr-1" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="glass border-white/10">
                  {availableLanguages.map((lang) => (
                    <SelectItem key={lang} value={lang} className="hover:bg-white/10">
                      {languageNames[lang]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Profile & Logout */}
              {user && (
                <>
                  <Link to="/profile">
                    <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant={location.pathname === '/profile' ? 'default' : 'ghost'}
                        size="icon"
                        className={location.pathname === '/profile' 
                          ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white' 
                          : 'text-gray-400 hover:text-white hover:bg-white/10'}
                      >
                        <User className="h-5 w-5" />
                      </Button>
                    </motion.div>
                  </Link>
                  <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={handleLogout}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                    >
                      <LogOut className="h-5 w-5" />
                    </Button>
                  </motion.div>
                </>
              )}
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Main Content with Animation */}
      <AnimatePresence mode="wait">
        <motion.main 
          key={location.pathname}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="container mx-auto px-4 py-8"
        >
          {children}
        </motion.main>
      </AnimatePresence>
    </div>
  );
};

export default Layout;
