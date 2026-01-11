import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Sprout, Upload, MapPin, Droplets, TestTube, Lightbulb, Thermometer, Cloud, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import apiService from '@/services/api';

const CropRecommendation = () => {
  const [formData, setFormData] = useState({
    location: 'Kacholi',
    waterSource: 'rainfall',
    soilType: 'loamy',
    soilPh: '',
    nitrogen: '',
    phosphorus: '',
    potassium: '',
  });
  const [soilReport, setSoilReport] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [allRecommendations, setAllRecommendations] = useState([]);
  const [weatherInfo, setWeatherInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [weatherLoading, setWeatherLoading] = useState(true);

  // Predefined locations with coordinates
  const locations = {
    'Kacholi': { lat: 30.3165, lon: 78.0322 },
    'Dehradun': { lat: 30.3165, lon: 78.0322 },
    'Haridwar': { lat: 29.9457, lon: 78.1642 },
    'Roorkee': { lat: 29.8543, lon: 77.8880 },
    'Rishikesh': { lat: 30.0869, lon: 78.2676 },
  };

  // Fetch current weather on load
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        setWeatherLoading(true);
        const loc = locations[formData.location] || locations['Kacholi'];
        const data = await apiService.getWeatherForecast(loc.lat, loc.lon, formData.location);
        setWeatherInfo({
          temp: data.current?.temp || 28,
          humidity: data.current?.humidity || 65,
          condition: data.current?.weather?.[0]?.main || 'Clear',
        });
      } catch (err) {
        console.error('Error fetching weather:', err);
        setWeatherInfo({ temp: 28, humidity: 65, condition: 'Clear' });
      } finally {
        setWeatherLoading(false);
      }
    };
    fetchWeather();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.location]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSoilReport(file);
      toast.success('Soil report uploaded successfully');
      // Simulate auto-fill from report
      setFormData({
        ...formData,
        soilPh: '6.8',
        nitrogen: '240',
        phosphorus: '45',
        potassium: '210',
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const loc = locations[formData.location] || locations['Kacholi'];
      const data = await apiService.getCropRecommendation(
        loc.lat,
        loc.lon,
        formData.soilType,
        formData.waterSource
      );

      if (data.recommendations && data.recommendations.length > 0) {
        // Map API recommendations to display format
        const cropImages = {
          'Rice': 'https://images.pexels.com/photos/2589457/pexels-photo-2589457.jpeg',
          'Wheat': 'https://images.pexels.com/photos/265216/pexels-photo-265216.jpeg',
          'Maize': 'https://images.pexels.com/photos/547263/pexels-photo-547263.jpeg',
          'Sugarcane': 'https://images.pexels.com/photos/4110407/pexels-photo-4110407.jpeg',
          'Mustard': 'https://images.pexels.com/photos/5472258/pexels-photo-5472258.jpeg',
          'Potato': 'https://images.pexels.com/photos/2286776/pexels-photo-2286776.jpeg',
          'Vegetables': 'https://images.pexels.com/photos/1656666/pexels-photo-1656666.jpeg',
          'Groundnut': 'https://images.pexels.com/photos/4110251/pexels-photo-4110251.jpeg',
        };

        const mappedRecommendations = data.recommendations.map((rec) => ({
          name: rec.crop,
          confidence: rec.confidence,
          season: rec.season,
          duration: rec.crop === 'Rice' ? '120-150 days' : rec.crop === 'Wheat' ? '120-140 days' : '90-120 days',
          yield: rec.crop === 'Rice' ? '45-55 quintals/hectare' : rec.crop === 'Wheat' ? '40-50 quintals/hectare' : '25-35 quintals/hectare',
          image: cropImages[rec.crop] || 'https://images.pexels.com/photos/2132171/pexels-photo-2132171.jpeg',
          advisory: rec.reason,
        }));

        setAllRecommendations(mappedRecommendations);
        setRecommendation(mappedRecommendations[0]);
        
        // Update weather info from response
        if (data.weather) {
          setWeatherInfo({
            temp: data.weather.temperature,
            humidity: data.weather.humidity,
            condition: 'Based on Analysis',
          });
        }
        
        toast.success('Crop recommendations generated based on current weather!');
      }
    } catch (err) {
      console.error('Error getting recommendations:', err);
      toast.error('Failed to get recommendations. Using fallback data.');
      
      // Fallback recommendations
      const fallbackCrops = [
        {
          name: 'Wheat',
          confidence: 92,
          season: 'Rabi',
          duration: '120-150 days',
          yield: '40-50 quintals/hectare',
          image: 'https://images.pexels.com/photos/265216/pexels-photo-265216.jpeg',
          advisory: 'Ideal conditions detected. Recommended sowing time: October-November. Ensure proper drainage.',
        },
        {
          name: 'Chickpea',
          confidence: 85,
          season: 'Rabi',
          duration: '95-105 days',
          yield: '15-20 quintals/hectare',
          image: 'https://images.pexels.com/photos/35338527/pexels-photo-35338527.jpeg',
          advisory: 'Good alternative crop. Requires less water. Suitable for your soil conditions.',
        },
      ];
      setAllRecommendations(fallbackCrops);
      setRecommendation(fallbackCrops[0]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="bg-primary/10 p-3 rounded-2xl">
            <Sprout className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Crop Recommendation</h1>
            <p className="text-muted-foreground">Get AI-powered crop suggestions based on your soil and location</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Input Form */}
          <div className="lg:col-span-2">
            <Card className="shadow-elegant border-border">
              <CardHeader>
                <CardTitle>Enter Farm Details</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Soil Report Upload */}
                  <div className="space-y-2">
                    <Label>Upload Soil Report (Optional)</Label>
                    <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer">
                      <input
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        onChange={handleFileUpload}
                        className="hidden"
                        id="soil-report"
                      />
                      <label htmlFor="soil-report" className="cursor-pointer">
                        <Upload className="h-10 w-10 mx-auto mb-2 text-muted-foreground" />
                        <p className="text-sm font-medium text-foreground">
                          {soilReport ? soilReport.name : 'Click to upload soil report'}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">PDF, JPG, PNG (Max 5MB)</p>
                      </label>
                    </div>
                  </div>

                  <Separator />

                  {/* Current Weather Info */}
                  <div className="bg-accent/10 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Cloud className="h-5 w-5 text-accent" />
                      <span className="font-semibold text-foreground">Current Weather Conditions</span>
                    </div>
                    {weatherLoading ? (
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Loading weather...
                      </div>
                    ) : (
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <Thermometer className="h-4 w-4 mx-auto mb-1 text-primary" />
                          <p className="text-lg font-bold text-foreground">{weatherInfo?.temp}°C</p>
                          <p className="text-xs text-muted-foreground">Temperature</p>
                        </div>
                        <div>
                          <Droplets className="h-4 w-4 mx-auto mb-1 text-primary" />
                          <p className="text-lg font-bold text-foreground">{weatherInfo?.humidity}%</p>
                          <p className="text-xs text-muted-foreground">Humidity</p>
                        </div>
                        <div>
                          <Cloud className="h-4 w-4 mx-auto mb-1 text-primary" />
                          <p className="text-lg font-bold text-foreground">{weatherInfo?.condition}</p>
                          <p className="text-xs text-muted-foreground">Condition</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Location */}
                  <div className="space-y-2">
                    <Label htmlFor="location">
                      <MapPin className="inline h-4 w-4 mr-2" />
                      Location
                    </Label>
                    <Select value={formData.location} onValueChange={(value) => setFormData({ ...formData, location: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select location" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Kacholi">Kacholi</SelectItem>
                        <SelectItem value="Dehradun">Dehradun</SelectItem>
                        <SelectItem value="Haridwar">Haridwar</SelectItem>
                        <SelectItem value="Roorkee">Roorkee</SelectItem>
                        <SelectItem value="Rishikesh">Rishikesh</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Soil Type */}
                  <div className="space-y-2">
                    <Label htmlFor="soilType">
                      <TestTube className="inline h-4 w-4 mr-2" />
                      Soil Type
                    </Label>
                    <Select value={formData.soilType} onValueChange={(value) => setFormData({ ...formData, soilType: value })}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="loamy">Loamy (दोमट)</SelectItem>
                        <SelectItem value="clay">Clay (चिकनी मिट्टी)</SelectItem>
                        <SelectItem value="sandy">Sandy (रेतीली)</SelectItem>
                        <SelectItem value="silt">Silt (गाद)</SelectItem>
                        <SelectItem value="black">Black Cotton (काली मिट्टी)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Water Source */}
                  <div className="space-y-2">
                    <Label htmlFor="waterSource">
                      <Droplets className="inline h-4 w-4 mr-2" />
                      Water Source
                    </Label>
                    <Select value={formData.waterSource} onValueChange={(value) => setFormData({ ...formData, waterSource: value })}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="rainfall">Rainfall</SelectItem>
                        <SelectItem value="borewell">Borewell</SelectItem>
                        <SelectItem value="canal">Canal</SelectItem>
                        <SelectItem value="mixed">Mixed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Soil Parameters */}
                  <div className="space-y-4">
                    <Label className="text-base font-semibold">
                      <TestTube className="inline h-4 w-4 mr-2" />
                      Soil Parameters
                    </Label>
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="soilPh">Soil pH</Label>
                        <Input
                          id="soilPh"
                          type="number"
                          step="0.1"
                          placeholder="e.g., 6.5"
                          value={formData.soilPh}
                          onChange={(e) => setFormData({ ...formData, soilPh: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="nitrogen">Nitrogen (N) kg/ha</Label>
                        <Input
                          id="nitrogen"
                          type="number"
                          placeholder="e.g., 240"
                          value={formData.nitrogen}
                          onChange={(e) => setFormData({ ...formData, nitrogen: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="phosphorus">Phosphorus (P) kg/ha</Label>
                        <Input
                          id="phosphorus"
                          type="number"
                          placeholder="e.g., 45"
                          value={formData.phosphorus}
                          onChange={(e) => setFormData({ ...formData, phosphorus: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="potassium">Potassium (K) kg/ha</Label>
                        <Input
                          id="potassium"
                          type="number"
                          placeholder="e.g., 210"
                          value={formData.potassium}
                          onChange={(e) => setFormData({ ...formData, potassium: e.target.value })}
                        />
                      </div>
                    </div>
                  </div>

                  <Button type="submit" className="w-full gradient-primary" size="lg" disabled={loading}>
                    {loading ? 'Analyzing...' : 'Get Recommendation'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Recommendation Result */}
          <div className="lg:col-span-1">
            {recommendation ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="shadow-elegant border-primary">
                  <CardContent className="p-0">
                    <img
                      src={recommendation.image}
                      alt={recommendation.name}
                      className="w-full h-48 object-cover rounded-t-lg"
                    />
                    <div className="p-6 space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="text-2xl font-bold text-foreground">{recommendation.name}</h3>
                        <Badge className="bg-primary text-primary-foreground">
                          {recommendation.confidence}% Match
                        </Badge>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <p className="text-xs text-muted-foreground">Season</p>
                          <p className="text-sm font-medium text-foreground">{recommendation.season}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Duration</p>
                          <p className="text-sm font-medium text-foreground">{recommendation.duration}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Expected Yield</p>
                          <p className="text-sm font-medium text-foreground">{recommendation.yield}</p>
                        </div>
                      </div>

                      <Separator />

                      <div className="bg-accent/10 p-4 rounded-lg">
                        <div className="flex items-start gap-2">
                          <Lightbulb className="h-5 w-5 text-accent mt-0.5" />
                          <div>
                            <p className="text-xs font-semibold text-foreground mb-1">Advisory</p>
                            <p className="text-sm text-muted-foreground leading-relaxed">
                              {recommendation.advisory}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              <Card className="shadow-elegant border-border">
                <CardContent className="p-12 text-center">
                  <Sprout className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">Enter your farm details to get crop recommendations</p>
                </CardContent>
              </Card>
            )}

            {/* Alternative Recommendations */}
            {allRecommendations.length > 1 && (
              <Card className="shadow-elegant border-border mt-4">
                <CardHeader>
                  <CardTitle className="text-lg">Alternative Crops</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {allRecommendations.slice(1).map((crop, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                      onClick={() => setRecommendation(crop)}
                    >
                      <img
                        src={crop.image}
                        alt={crop.name}
                        className="w-12 h-12 rounded-lg object-cover"
                      />
                      <div className="flex-1">
                        <p className="font-semibold text-foreground">{crop.name}</p>
                        <p className="text-xs text-muted-foreground">{crop.season} • {crop.duration}</p>
                      </div>
                      <Badge variant="outline">{crop.confidence}%</Badge>
                    </motion.div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CropRecommendation;
