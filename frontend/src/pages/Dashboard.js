import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import Layout from '@/components/Layout';
import { FeatureCard, WeatherCard, QuickToolCard } from '@/components/Cards';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Sprout, 
  CloudRain, 
  TrendingUp, 
  Bug, 
  Users, 
  Calculator,
  Phone,
  FileText,
  BookOpen,
  Sun,
  CloudDrizzle,
  Droplets,
  Wind,
  AlertTriangle,
  CheckCircle,
  ChevronRight,
  Cloud,
  Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import apiService from '@/services/api';

// Weather icon mapping
const getWeatherIcon = (iconCode) => {
  if (iconCode?.includes('01')) return Sun;
  if (iconCode?.includes('02') || iconCode?.includes('03')) return CloudDrizzle;
  if (iconCode?.includes('04')) return Cloud;
  if (iconCode?.includes('09') || iconCode?.includes('10')) return CloudRain;
  return Cloud;
};

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  
  const [weatherData, setWeatherData] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/auth');
    }
  }, [isAuthenticated, navigate]);

  // Fetch live weather data
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        setWeatherLoading(true);
        // Default to Kacholi/Dehradun coordinates
        const data = await apiService.getWeatherForecast(30.3165, 78.0322, 'Kacholi');
        setWeatherData(data);
      } catch (err) {
        console.error('Error fetching weather:', err);
      } finally {
        setWeatherLoading(false);
      }
    };
    
    if (isAuthenticated) {
      fetchWeather();
    }
  }, [isAuthenticated]);

  if (!isAuthenticated || !user) {
    return null;
  }

  const features = [
    {
      icon: Sprout,
      title: t('cropRecommendation'),
      description: 'Get AI-powered crop recommendations based on soil, weather, and location',
      path: '/crop-recommendation',
    },
    {
      icon: CloudRain,
      title: t('weather'),
      description: '7-day weather forecast with farming advisories',
      path: '/weather',
    },
    {
      icon: TrendingUp,
      title: t('marketPrices'),
      description: 'Real-time mandi prices and market trends',
      path: '/market-prices',
    },
    {
      icon: Bug,
      title: t('pestDetection'),
      description: 'Detect crop diseases using AI image analysis',
      path: '/pest-detection',
    },
    {
      icon: BookOpen,
      title: t('diseaseKnowledge'),
      description: 'Comprehensive disease database with treatments',
      path: '/disease-knowledge',
    },
    {
      icon: Users,
      title: t('community'),
      description: 'Connect with fellow farmers and share experiences',
      path: '/community',
    },
    {
      icon: FileText,
      title: t('schemes'),
      description: 'Browse government schemes and benefits',
      path: '/schemes',
    },
    {
      icon: Phone,
      title: t('expertContact'),
      description: 'Get in touch with agricultural experts',
      path: '/expert-contact',
    },
  ];

  const quickTools = [
    { icon: Calculator, label: 'Fertilizer Calc', path: '/calculators?tool=fertilizer' },
    { icon: Droplets, label: 'Pesticide Calc', path: '/calculators?tool=pesticide' },
    { icon: Sprout, label: 'Farming Calc', path: '/calculators?tool=farming' },
  ];

  // Process weather data from API
  const currentWeather = weatherData?.current || { temp: 28, humidity: 65, wind_speed: 12, rainfall: 0 };
  const currentTemp = currentWeather.temp || 28;
  const rainfall = currentWeather.rainfall || 0;
  const humidity = currentWeather.humidity || 65;
  const windSpeed = currentWeather.wind_speed || 12;
  const sprayCondition = weatherData?.spray_condition === 'Good' || (humidity < 70 && windSpeed < 15);

  // Process 7-day forecast
  const weekWeather = (weatherData?.daily || []).slice(0, 7).map((day, index) => {
    const date = new Date(day.dt * 1000);
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return {
      day: dayNames[date.getDay()],
      temp: Math.round(day.temp?.day || day.temp?.max || 28),
      condition: day.weather?.[0]?.main || 'Clear',
      icon: getWeatherIcon(day.weather?.[0]?.icon),
    };
  });

  // Fallback weather data if API fails
  const defaultWeekWeather = [
    { day: 'Mon', temp: 28, condition: 'Sunny', icon: Sun },
    { day: 'Tue', temp: 26, condition: 'Cloudy', icon: CloudDrizzle },
    { day: 'Wed', temp: 24, condition: 'Rainy', icon: Droplets },
    { day: 'Thu', temp: 27, condition: 'Windy', icon: Wind },
    { day: 'Fri', temp: 29, condition: 'Sunny', icon: Sun },
    { day: 'Sat', temp: 28, condition: 'Cloudy', icon: CloudDrizzle },
    { day: 'Sun', temp: 30, condition: 'Sunny', icon: Sun },
  ];

  const displayWeekWeather = weekWeather.length > 0 ? weekWeather : defaultWeekWeather;
  const CurrentWeatherIcon = weatherData?.current?.weather?.[0]?.icon 
    ? getWeatherIcon(weatherData.current.weather[0].icon) 
    : Sun;

  return (
    <Layout>
      <div className="space-y-8">
        {/* Enhanced Hero Section with Glassmorphism */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, type: 'spring' }}
          className="relative overflow-hidden rounded-3xl glass-card p-8 md:p-12 border border-emerald-500/20"
        >
          {/* Animated gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-600/20 via-transparent to-cyan-600/20 animate-gradient" style={{ backgroundSize: '200% 200%' }} />
          
          <div className="relative z-10 grid md:grid-cols-2 gap-8 items-center">
            <div className="space-y-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Badge className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-4 py-1.5 text-sm">
                  👋 {t('goodMorning')}, {user.name}!
                </Badge>
              </motion.div>
              <motion.h1 
                className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight text-white"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <span className="gradient-text">Smart Farming</span>,
                <br />
                Better Yields
              </motion.h1>
              <motion.p 
                className="text-lg text-gray-300 leading-relaxed max-w-lg"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                Your intelligent farming companion. Get AI-powered recommendations, real-time market insights, and expert guidance.
              </motion.p>
              <motion.div 
                className="flex flex-wrap gap-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white shadow-lg shadow-emerald-500/30 px-6"
                  onClick={() => navigate('/crop-recommendation')}
                >
                  Get Crop Advice
                  <ChevronRight className="ml-2 h-5 w-5" />
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="border-white/20 text-white hover:bg-white/10 px-6"
                  onClick={() => navigate('/pest-detection')}
                >
                  <Bug className="mr-2 h-5 w-5" />
                  Scan Disease
                </Button>
              </motion.div>
            </div>
            <motion.div 
              className="hidden md:block relative"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4, type: 'spring' }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/30 to-cyan-500/30 rounded-3xl blur-3xl" />
              <img
                src="/images/1i.png"
                alt="Smart farming"
                className="relative rounded-3xl shadow-2xl object-cover w-full h-72 lg:h-80 border border-white/10"
              />
            </motion.div>
          </div>
        </motion.div>

        {/* Weather Strip - Enhanced Glass Style */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="glass-card border-white/10 shadow-2xl overflow-hidden">
            <CardContent className="p-6">
              {weatherLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-emerald-500 mr-3" />
                  <span className="text-gray-400">Loading live weather...</span>
                </div>
              ) : (
              <>
              <div className="flex flex-col lg:flex-row gap-6 items-start lg:items-center justify-between">
                {/* Current Weather */}
                <div className="flex-1">
                  <div className="flex items-center gap-4">
                    <motion.div 
                      className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 p-4 rounded-2xl border border-blue-500/20"
                      animate={{ y: [0, -5, 0] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    >
                      <CurrentWeatherIcon className="h-12 w-12 text-cyan-400" />
                    </motion.div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-medium text-gray-400">{t('todayWeather')}</h3>
                        {weatherData?.source === 'live' && (
                          <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs animate-pulse">
                            🔴 Live
                          </Badge>
                        )}
                      </div>
                      <p className="text-5xl font-bold text-white">{currentTemp}°C</p>
                      <p className="text-sm text-gray-400 flex items-center gap-1">
                        <span>📍</span> {weatherData?.location || user.village || 'Kacholi'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Weather Stats */}
                <div className="grid grid-cols-3 gap-6 flex-1">
                  {[
                    { icon: Droplets, label: 'Rainfall', value: `${rainfall}mm`, color: 'text-blue-400' },
                    { icon: CloudDrizzle, label: 'Humidity', value: `${humidity}%`, color: 'text-cyan-400' },
                    { icon: Wind, label: 'Wind', value: `${windSpeed}km/h`, color: 'text-teal-400' }
                  ].map((stat, i) => (
                    <motion.div 
                      key={stat.label}
                      className="text-center p-3 rounded-xl bg-white/5 border border-white/5"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + i * 0.1 }}
                    >
                      <stat.icon className={`h-6 w-6 mx-auto mb-2 ${stat.color}`} />
                      <p className="text-xs text-gray-500">{stat.label}</p>
                      <p className="text-xl font-bold text-white">{stat.value}</p>
                    </motion.div>
                  ))}
                </div>

                {/* Spray Condition */}
                <div className="flex-1">
                  <motion.div
                    className={`p-5 rounded-2xl border-2 backdrop-blur-sm ${
                      sprayCondition
                        ? 'bg-emerald-500/10 border-emerald-500/30'
                        : 'bg-orange-500/10 border-orange-500/30'
                    }`}
                    whileHover={{ scale: 1.02 }}
                  >
                    <div className="flex items-center gap-3">
                      {sprayCondition ? (
                        <CheckCircle className="h-8 w-8 text-emerald-400" />
                      ) : (
                        <AlertTriangle className="h-8 w-8 text-orange-400" />
                      )}
                      <div>
                        <p className="text-xs font-medium text-gray-400">{t('sprayCondition')}</p>
                        <p className={`text-lg font-bold ${sprayCondition ? 'text-emerald-400' : 'text-orange-400'}`}>
                          {sprayCondition ? '✓ Good for Spraying' : '⚠ Not Ideal'}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>

              {/* 7-Day Weather */}
              <div className="mt-6 pt-6 border-t border-white/10">
                <h4 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <Cloud className="h-4 w-4 text-blue-400" />
                  7-Day Forecast
                </h4>
                <div className="grid grid-cols-4 sm:grid-cols-7 gap-3">
                  {displayWeekWeather.map((day, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + index * 0.05 }}
                    >
                      <WeatherCard {...day} />
                    </motion.div>
                  ))}
                </div>
              </div>
              </>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Tools - Enhanced */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="p-2 rounded-lg bg-gradient-to-br from-teal-500/20 to-teal-600/20 border border-teal-500/20">
              <Calculator className="h-5 w-5 text-teal-400" />
            </span>
            {t('quickTools')}
          </h2>
          <div className="grid grid-cols-3 gap-4">
            {quickTools.map((tool, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="cursor-pointer"
                onClick={() => navigate(tool.path)}
              >
                <div className="glass-card p-6 rounded-2xl border border-white/10 text-center hover:border-teal-500/30 transition-all hover:shadow-lg hover:shadow-teal-500/10">
                  <div className="bg-gradient-to-br from-teal-500/20 to-cyan-500/20 p-4 rounded-xl inline-block mb-3">
                    <tool.icon className="h-8 w-8 text-teal-400" />
                  </div>
                  <p className="text-white font-medium">{tool.label}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Features Grid - Enhanced */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <span className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-purple-600/20 border border-purple-500/20">
              <Sprout className="h-5 w-5 text-purple-400" />
            </span>
            {t('features')}
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.05 }}
              >
                <FeatureCard
                  icon={feature.icon}
                  title={feature.title}
                  description={feature.description}
                  onClick={() => navigate(feature.path)}
                />
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default Dashboard;
