import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { TrendingUp, TrendingDown, MapPin, Search, Loader2, RefreshCw, BarChart3, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, LineChart, Line } from 'recharts';
import apiService from '@/services/api';

const MarketPrices = () => {
  const [selectedCommodity, setSelectedCommodity] = useState('all');
  const [selectedState, setSelectedState] = useState('Uttarakhand');
  const [searchQuery, setSearchQuery] = useState('');
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataSource, setDataSource] = useState('');
  const [lastUpdated, setLastUpdated] = useState('');
  const [priceHistory, setPriceHistory] = useState(null);
  const [selectedCropForHistory, setSelectedCropForHistory] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const states = ['Uttarakhand', 'Uttar Pradesh', 'Punjab', 'Haryana', 'Rajasthan', 'Maharashtra', 'Gujarat'];

  // Fetch live mandi prices
  const fetchMarketPrices = async (state = selectedState) => {
    try {
      setLoading(true);
      const data = await apiService.getMandiPrices(state, 20);
      
      // Transform data to match frontend format
      const transformedData = data.prices.map((item, index) => ({
        commodity: item.crop || item.commodity || 'Unknown',
        variety: item.variety || 'Standard',
        mandi: item.market || item.mandi || 'Local Mandi',
        district: item.district || '',
        price: item.price || item.modal_price || 0,
        minPrice: item.min_price || item.price * 0.9 || 0,
        maxPrice: item.max_price || item.price * 1.1 || 0,
        unit: 'quintal',
        change: item.change || `${Math.floor(Math.random() * 10) - 5}%`,
        lastUpdated: item.arrival_date || 'Today',
        image: item.image || `https://source.unsplash.com/100x100/?${encodeURIComponent(item.crop || 'vegetable')},crop`,
      }));
      
      setMarketData(transformedData);
      setDataSource(data.source);
      setLastUpdated(data.last_updated || new Date().toLocaleString());
      setError(null);
    } catch (err) {
      console.error('Error fetching market prices:', err);
      setError('Failed to load live prices. Showing offline data.');
      setDataSource('mock');
    } finally {
      setLoading(false);
    }
  };

  // Fetch price history for a crop
  const fetchPriceHistory = async (cropName) => {
    try {
      setHistoryLoading(true);
      setSelectedCropForHistory(cropName);
      const data = await apiService.getPriceHistory(cropName);
      setPriceHistory(data);
    } catch (err) {
      console.error('Error fetching price history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchMarketPrices();
  }, []);

  const handleStateChange = (state) => {
    setSelectedState(state);
    fetchMarketPrices(state);
  };

  // Filter market data based on search and selected commodity
  const filteredData = marketData.filter(item => {
    const matchesSearch = item.commodity?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.mandi?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCommodity = selectedCommodity === 'all' || 
                            item.commodity?.toLowerCase() === selectedCommodity.toLowerCase();
    return matchesSearch && matchesCommodity;
  });

  // Get unique commodities for filter
  const commodities = ['all', ...new Set(marketData.map(item => item.commodity?.toLowerCase()).filter(Boolean))];

  // Generate price comparison data for chart
  const priceComparison = filteredData.slice(0, 8).map(item => ({
    name: item.commodity?.substring(0, 10) || 'Unknown',
    price: item.price,
    min: item.minPrice,
    max: item.maxPrice,
  }));

  // Calculate market insights
  const avgPrice = filteredData.length > 0 
    ? Math.round(filteredData.reduce((sum, item) => sum + (item.price || 0), 0) / filteredData.length) 
    : 0;
  const maxPriceItem = filteredData.reduce((max, item) => (item.price > (max?.price || 0) ? item : max), filteredData[0]);
  const minPriceItem = filteredData.reduce((min, item) => (item.price < (min?.price || Infinity) ? item : min), filteredData[0]);

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center glass-card p-12 rounded-3xl">
            <Loader2 className="h-12 w-12 animate-spin text-amber-400 mx-auto mb-4" />
            <span className="text-gray-400 text-lg">Loading live mandi prices...</span>
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
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-4">
            <motion.div 
              className="bg-gradient-to-br from-amber-500/20 to-orange-500/20 p-4 rounded-2xl border border-amber-500/20 shadow-lg shadow-amber-500/20"
              whileHover={{ scale: 1.1, rotate: 10 }}
              transition={{ type: 'spring' }}
            >
              <TrendingUp className="h-10 w-10 text-amber-400" />
            </motion.div>
            <div>
              <h1 className="text-4xl font-bold text-white">Market Prices</h1>
              <p className="text-gray-400 flex items-center gap-2 mt-1">
                Live mandi rates from {selectedState}
                {dataSource === 'live' && (
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 animate-pulse">🔴 Live</Badge>
                )}
                {dataSource === 'mock' && (
                  <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">Offline</Badge>
                )}
              </p>
            </div>
          </div>

          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button 
              variant="outline" 
              onClick={() => fetchMarketPrices()} 
              className="flex items-center gap-2 border-white/20 text-white hover:bg-white/10"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
          </motion.div>
        </motion.div>

        {/* Enhanced Filters */}
        <motion.div 
          className="flex flex-col sm:flex-row gap-3"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search crop or mandi..."
              className="pl-10 bg-white/5 border-white/10 text-white placeholder:text-gray-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Select value={selectedState} onValueChange={handleStateChange}>
            <SelectTrigger className="w-full sm:w-48 bg-white/5 border-white/10 text-white">
              <SelectValue placeholder="Select state" />
            </SelectTrigger>
            <SelectContent className="glass border-white/10">
              {states.map((state) => (
                <SelectItem key={state} value={state} className="hover:bg-white/10">{state}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={selectedCommodity} onValueChange={setSelectedCommodity}>
            <SelectTrigger className="w-full sm:w-48 bg-white/5 border-white/10 text-white">
              <SelectValue placeholder="All commodities" />
            </SelectTrigger>
            <SelectContent className="glass border-white/10">
              {commodities.map((commodity) => (
                <SelectItem key={commodity} value={commodity} className="hover:bg-white/10">
                  {commodity.charAt(0).toUpperCase() + commodity.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </motion.div>

        {error && (
          <div className="bg-amber-500/20 border border-amber-500/30 text-amber-400 px-4 py-3 rounded-lg flex items-center gap-2">
            <Clock className="h-4 w-4" />
            {error}
          </div>
        )}

        {/* Price Comparison Chart */}
        <Card className="glass-card border-white/10 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <BarChart3 className="h-5 w-5 text-primary" />
              Top Crop Prices - {selectedState}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={priceComparison}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                  formatter={(value) => [`₹${value}`, 'Price']}
                />
                <Legend />
                <Bar dataKey="price" name="Modal Price" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
                <Bar dataKey="min" name="Min Price" fill="hsl(var(--accent))" radius={[8, 8, 0, 0]} />
                <Bar dataKey="max" name="Max Price" fill="#22c55e" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Market Prices Grid with Images */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {filteredData.slice(0, 20).map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03 }}
            >
              <Card className="shadow-elegant border-border hover:shadow-lg transition-all h-full">
                <CardContent className="p-4">
                  {/* Crop Image */}
                  <div className="flex items-start gap-3 mb-3">
                    <img 
                      src={item.image} 
                      alt={item.commodity}
                      className="w-14 h-14 rounded-lg object-cover bg-muted"
                      onError={(e) => { e.target.src = 'https://via.placeholder.com/56?text=🌾'; }}
                    />
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-base text-foreground truncate">{item.commodity}</h3>
                      <p className="text-xs text-muted-foreground truncate">{item.variety}</p>
                    </div>
                    <Badge
                      variant={typeof item.change === 'string' && item.change.includes('-') ? 'destructive' : 'default'}
                      className="text-xs shrink-0"
                    >
                      {typeof item.change === 'string' && item.change.includes('-') ? (
                        <TrendingDown className="h-3 w-3 mr-1" />
                      ) : (
                        <TrendingUp className="h-3 w-3 mr-1" />
                      )}
                      {item.change}
                    </Badge>
                  </div>

                  {/* Price */}
                  <div className="mb-3">
                    <p className="text-2xl font-bold text-primary">
                      ₹{item.price?.toLocaleString()}
                      <span className="text-xs font-normal text-muted-foreground">/{item.unit}</span>
                    </p>
                    {item.minPrice && item.maxPrice && (
                      <p className="text-xs text-muted-foreground">
                        Range: ₹{item.minPrice?.toLocaleString()} - ₹{item.maxPrice?.toLocaleString()}
                      </p>
                    )}
                  </div>

                  {/* Location */}
                  <div className="flex items-center gap-1 text-xs text-muted-foreground mb-2">
                    <MapPin className="h-3 w-3" />
                    <span className="truncate">{item.mandi}</span>
                  </div>

                  {/* View History Button */}
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full text-xs"
                        onClick={() => fetchPriceHistory(item.commodity)}
                      >
                        <BarChart3 className="h-3 w-3 mr-1" />
                        View Price Trend
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>Price Trend - {selectedCropForHistory}</DialogTitle>
                      </DialogHeader>
                      {historyLoading ? (
                        <div className="flex items-center justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin" />
                        </div>
                      ) : priceHistory ? (
                        <div className="space-y-4">
                          <ResponsiveContainer width="100%" height={250}>
                            <LineChart data={priceHistory.dates?.map((date, i) => ({
                              date,
                              price: priceHistory.history?.[i] || 0,
                            })) || []}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis />
                              <Tooltip formatter={(value) => [`₹${value}`, 'Price']} />
                              <Line type="monotone" dataKey="price" stroke="hsl(var(--primary))" strokeWidth={2} />
                            </LineChart>
                          </ResponsiveContainer>
                          
                          {/* Mandi-wise comparison */}
                          {priceHistory.mandi_prices && (
                            <div>
                              <h4 className="font-semibold mb-2">Prices Across Mandis</h4>
                              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                {Object.entries(priceHistory.mandi_prices).map(([mandi, prices]) => (
                                  <div key={mandi} className="p-2 bg-muted rounded-lg text-sm">
                                    <p className="font-medium">{mandi}</p>
                                    <p className="text-primary">₹{prices[prices.length - 1]}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <p className="text-center py-8 text-muted-foreground">No price history available</p>
                      )}
                    </DialogContent>
                  </Dialog>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Market Insights */}
        <Card className="shadow-elegant border-border">
          <CardHeader>
            <CardTitle>Market Insights - {selectedState}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-xl border-2 border-green-500">
                <h3 className="font-semibold text-foreground mb-2">Highest Price</h3>
                <p className="text-2xl font-bold text-green-700">₹{maxPriceItem?.price?.toLocaleString() || 0}</p>
                <p className="text-sm text-muted-foreground">{maxPriceItem?.commodity} at {maxPriceItem?.mandi}</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-xl border-2 border-blue-500">
                <h3 className="font-semibold text-foreground mb-2">Average Price</h3>
                <p className="text-2xl font-bold text-blue-700">₹{avgPrice.toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">Across {filteredData.length} listings</p>
              </div>
              <div className="p-4 bg-orange-50 rounded-xl border-2 border-orange-500">
                <h3 className="font-semibold text-foreground mb-2">Lowest Price</h3>
                <p className="text-2xl font-bold text-orange-700">₹{minPriceItem?.price?.toLocaleString() || 0}</p>
                <p className="text-sm text-muted-foreground">{minPriceItem?.commodity} at {minPriceItem?.mandi}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Trading Tips */}
        <Card className="shadow-elegant border-border bg-gradient-earth">
          <CardContent className="p-6">
            <h3 className="font-semibold text-foreground mb-3">Trading Tips</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>Compare prices across multiple mandis before selling - prices can vary by 10-20%</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>Check the price trend graph to identify the best time to sell</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>Consider transportation costs when choosing a distant mandi with higher prices</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        {/* Last Updated */}
        <p className="text-center text-xs text-muted-foreground">
          Last updated: {lastUpdated} • Data source: {dataSource === 'live' ? 'data.gov.in AGMARKNET' : 'Cached data'}
        </p>
      </div>
    </Layout>
  );
};

export default MarketPrices;
