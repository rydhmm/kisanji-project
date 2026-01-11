import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { 
  CloudRain, 
  Sun, 
  CloudDrizzle, 
  Droplets, 
  Wind, 
  ThermometerSun,
  Sunrise,
  Sunset,
  MapPin,
  Calendar,
  AlertCircle,
  Cloud,
  Loader2,
  Search,
  RefreshCw
} from 'lucide-react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import apiService from '@/services/api';

// Weather icon mapping
const getWeatherIcon = (iconCode) => {
  if (iconCode?.includes('01')) return Sun;
  if (iconCode?.includes('02') || iconCode?.includes('03')) return CloudDrizzle;
  if (iconCode?.includes('04')) return Cloud;
  if (iconCode?.includes('09') || iconCode?.includes('10')) return CloudRain;
  if (iconCode?.includes('11')) return CloudRain;
  if (iconCode?.includes('13')) return CloudDrizzle;
  return Cloud;
};

const Weather = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [location, setLocation] = useState('Kacholi');
  const [searchInput, setSearchInput] = useState('');
  const [coords, setCoords] = useState({ lat: 30.3165, lon: 78.0322 });
  const [weatherData, setWeatherData] = useState(null);
  const [dataSource, setDataSource] = useState('');

  // Predefined locations for quick selection
  const locations = {
    'Kacholi': { lat: 30.3165, lon: 78.0322 },
    'Dehradun': { lat: 30.3165, lon: 78.0322 },
    'Haridwar': { lat: 29.9457, lon: 78.1642 },
    'Roorkee': { lat: 29.8543, lon: 77.8880 },
    'Rishikesh': { lat: 30.0869, lon: 78.2676 },
    'Vikasnagar': { lat: 30.4677, lon: 77.7719 },
  };

  const fetchWeather = async (lat, lon, locationName) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getWeatherForecast(lat, lon, locationName);
      setWeatherData(data);
      setDataSource(data.source);
      setLocation(locationName);
    } catch (err) {
      setError('Failed to fetch weather data. Showing cached data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchWeather(coords.lat, coords.lon, location);
  }, []);

  const handleLocationSearch = (e) => {
    e.preventDefault();
    const searchTerm = searchInput.trim();
    if (locations[searchTerm]) {
      const loc = locations[searchTerm];
      setCoords({ lat: loc.lat, lon: loc.lon });
      fetchWeather(loc.lat, loc.lon, searchTerm);
    } else {
      // Default to Dehradun if location not found
      fetchWeather(coords.lat, coords.lon, searchTerm || location);
    }
    setSearchInput('');
  };

  const handleQuickLocation = (locName) => {
    const loc = locations[locName];
    setCoords({ lat: loc.lat, lon: loc.lon });
    fetchWeather(loc.lat, loc.lon, locName);
  };

  // Process weather data for display
  const currentWeather = weatherData?.current || {
    temp: 28,
    feels_like: 30,
    humidity: 65,
    wind_speed: 12,
    weather: [{ main: 'Cloudy', description: 'partly cloudy', icon: '02d' }],
    rainfall: 0,
  };

  const CurrentIcon = getWeatherIcon(currentWeather.weather?.[0]?.icon);

  const weeklyForecast = (weatherData?.daily || []).map((day, index) => {
    const date = new Date(day.dt * 1000);
    return {
      day: date.toLocaleDateString('en-US', { weekday: 'long' }),
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      high: day.temp?.max || day.temp?.day || 28,
      low: day.temp?.min || 20,
      condition: day.weather?.[0]?.main || 'Clear',
      icon: getWeatherIcon(day.weather?.[0]?.icon),
      rain: day.pop || 0,
    };
  });

  // Generate hourly data from current temp
  const baseTemp = currentWeather.temp || 28;
  const hourlyData = [
    { time: '6 AM', temp: baseTemp - 6 },
    { time: '9 AM', temp: baseTemp - 3 },
    { time: '12 PM', temp: baseTemp },
    { time: '3 PM', temp: baseTemp + 2 },
    { time: '6 PM', temp: baseTemp - 1 },
    { time: '9 PM', temp: baseTemp - 4 },
  ];

  const sprayCondition = weatherData?.spray_condition || 
    (currentWeather.humidity < 70 && currentWeather.wind_speed < 15 ? 'Good' : 'Poor');

  const farmingAdvisory = [
    {
      title: 'Spraying Condition',
      status: sprayCondition,
      type: sprayCondition === 'Good' ? 'success' : 'warning',
      message: sprayCondition === 'Good' 
        ? 'Wind speed is ideal for pesticide application. Humidity is moderate.'
        : 'High humidity or wind. Avoid spraying pesticides today.',
    },
    {
      title: 'Irrigation Advisory',
      status: weeklyForecast.some(d => d.rain > 50) ? 'Reduce' : 'Normal',
      type: weeklyForecast.some(d => d.rain > 50) ? 'warning' : 'success',
      message: weeklyForecast.some(d => d.rain > 50)
        ? 'Rainfall expected soon. Reduce irrigation to avoid waterlogging.'
        : 'No significant rainfall expected. Continue regular irrigation.',
    },
    {
      title: 'Harvesting Condition',
      status: weeklyForecast.filter(d => d.rain < 30).length >= 3 ? 'Favorable' : 'Wait',
      type: weeklyForecast.filter(d => d.rain < 30).length >= 3 ? 'success' : 'warning',
      message: weeklyForecast.filter(d => d.rain < 30).length >= 3
        ? 'Clear weather expected. Good time for harvesting crops.'
        : 'Rainy conditions ahead. Delay harvesting if possible.',
    },
  ];

  if (loading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto flex items-center justify-center min-h-[60vh]">
          <div className="text-center glass-card p-12 rounded-3xl">
            <Loader2 className="h-16 w-16 animate-spin text-blue-400 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">Loading weather data...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Enhanced Header */}
        <motion.div 
          className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-4">
            <motion.div 
              className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 p-4 rounded-2xl border border-blue-500/20 shadow-lg shadow-blue-500/20"
              whileHover={{ scale: 1.1, rotate: 10 }}
              transition={{ type: 'spring' }}
            >
              <CloudRain className="h-10 w-10 text-blue-400" />
            </motion.div>
            <div>
              <h1 className="text-4xl font-bold text-white">Weather Forecast</h1>
              <p className="text-gray-400 flex items-center gap-2 mt-1">
                <MapPin className="h-4 w-4 text-blue-400" />
                {location}
                <span className="mx-2 text-gray-600">•</span>
                <Calendar className="h-4 w-4 text-blue-400" />
                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                {dataSource === 'live' && (
                  <Badge className="ml-2 bg-emerald-500/20 text-emerald-400 border-emerald-500/30 animate-pulse">
                    🔴 Live
                  </Badge>
                )}
                {dataSource === 'mock' && (
                  <Badge className="ml-2 bg-gray-500/20 text-gray-400 border-gray-500/30">Offline</Badge>
                )}
              </p>
            </div>
          </div>

          {/* Search and Quick Locations */}
          <div className="flex flex-col sm:flex-row gap-2">
            <form onSubmit={handleLocationSearch} className="flex gap-2">
              <Input
                placeholder="Search location..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-40 bg-white/5 border-white/10 text-white"
              />
              <Button type="submit" size="icon" variant="outline" className="border-white/20 text-white hover:bg-white/10">
                <Search className="h-4 w-4" />
              </Button>
            </form>
            <Button 
              variant="outline" 
              size="icon"
              onClick={() => fetchWeather(coords.lat, coords.lon, location)}
              className="border-white/20 text-white hover:bg-white/10"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </motion.div>

        {/* Quick Location Buttons */}
        <div className="flex flex-wrap gap-2">
          {Object.keys(locations).map((loc) => (
            <Button
              key={loc}
              variant={location === loc ? "default" : "outline"}
              size="sm"
              onClick={() => handleQuickLocation(loc)}
              className={location === loc ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white" : "border-white/20 text-gray-400 hover:text-white hover:bg-white/10"}
            >
              {loc}
            </Button>
          ))}
        </div>

        {error && (
          <Card className="bg-orange-50 border-orange-200">
            <CardContent className="p-4">
              <p className="text-orange-700 flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                {error}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Current Weather */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="shadow-elegant border-border gradient-sky">
            <CardContent className="p-8">
              <div className="grid md:grid-cols-2 gap-8">
                {/* Left: Main Weather */}
                <div className="text-center md:text-left">
                  <div className="flex items-center justify-center md:justify-start gap-4 mb-4">
                    <CurrentIcon className="h-20 w-20 text-accent" />
                    <div>
                      <p className="text-6xl font-bold text-foreground">{currentWeather.temp}°C</p>
                      <p className="text-xl text-muted-foreground capitalize">
                        {currentWeather.weather?.[0]?.description || 'Partly Cloudy'}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Feels like {currentWeather.feels_like}°C
                  </p>
                </div>

                {/* Right: Details Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-card/80 backdrop-blur-sm p-4 rounded-xl">
                    <Droplets className="h-5 w-5 text-accent mb-2" />
                    <p className="text-xs text-muted-foreground">Humidity</p>
                    <p className="text-2xl font-bold text-foreground">{currentWeather.humidity}%</p>
                  </div>
                  <div className="bg-card/80 backdrop-blur-sm p-4 rounded-xl">
                    <Wind className="h-5 w-5 text-accent mb-2" />
                    <p className="text-xs text-muted-foreground">Wind Speed</p>
                    <p className="text-2xl font-bold text-foreground">{currentWeather.wind_speed} km/h</p>
                  </div>
                  <div className="bg-card/80 backdrop-blur-sm p-4 rounded-xl">
                    <CloudRain className="h-5 w-5 text-accent mb-2" />
                    <p className="text-xs text-muted-foreground">Rainfall</p>
                    <p className="text-2xl font-bold text-foreground">{currentWeather.rainfall || 0} mm</p>
                  </div>
                  <div className="bg-card/80 backdrop-blur-sm p-4 rounded-xl">
                    <ThermometerSun className="h-5 w-5 text-accent mb-2" />
                    <p className="text-xs text-muted-foreground">Spray Condition</p>
                    <Badge className={sprayCondition === 'Good' ? 'bg-green-600' : 'bg-orange-600'}>
                      {sprayCondition}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Sun Times */}
              <Separator className="my-6" />
              <div className="flex justify-around text-center">
                <div>
                  <Sunrise className="h-6 w-6 mx-auto mb-2 text-accent" />
                  <p className="text-xs text-muted-foreground">Sunrise</p>
                  <p className="text-sm font-semibold text-foreground">6:15 AM</p>
                </div>
                <div>
                  <Sunset className="h-6 w-6 mx-auto mb-2 text-accent" />
                  <p className="text-xs text-muted-foreground">Sunset</p>
                  <p className="text-sm font-semibold text-foreground">6:45 PM</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Hourly Temperature Chart */}
        <Card className="shadow-elegant border-border">
          <CardHeader>
            <CardTitle>Today's Temperature Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={hourlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                />
                <Line type="monotone" dataKey="temp" stroke="hsl(var(--accent))" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* 7-Day Forecast */}
        <Card className="shadow-elegant border-border">
          <CardHeader>
            <CardTitle>7-Day Forecast</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {weeklyForecast.length > 0 ? weeklyForecast.map((day, index) => {
                const Icon = day.icon;
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 bg-muted/30 rounded-xl hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <Icon className="h-6 w-6 text-accent" />
                      <div>
                        <p className="font-semibold text-foreground">{day.day}</p>
                        <p className="text-xs text-muted-foreground">{day.date}</p>
                      </div>
                    </div>
                    <div className="text-center flex-1">
                      <p className="text-sm text-muted-foreground">{day.condition}</p>
                      {day.rain > 0 && (
                        <Badge variant="secondary" className="text-xs mt-1">
                          {day.rain}% rain
                        </Badge>
                      )}
                    </div>
                    <div className="text-right flex-1">
                      <p className="text-lg font-bold text-foreground">
                        {Math.round(day.high)}° <span className="text-muted-foreground text-sm">{Math.round(day.low)}°</span>
                      </p>
                    </div>
                  </motion.div>
                );
              }) : (
                <p className="text-center text-muted-foreground py-8">No forecast data available</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Farming Advisory */}
        <Card className="shadow-elegant border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-primary" />
              Farming Advisory
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              {farmingAdvisory.map((advisory, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-4 rounded-xl border-2 ${
                    advisory.type === 'success'
                      ? 'bg-green-50 border-green-500'
                      : 'bg-orange-50 border-orange-500'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-sm text-foreground">{advisory.title}</h3>
                    <Badge
                      className={advisory.type === 'success' ? 'bg-green-600' : 'bg-orange-600'}
                    >
                      {advisory.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{advisory.message}</p>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Weather;
