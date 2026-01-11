import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Calculator, Droplets, Sprout, Loader2, IndianRupee, Leaf, FlaskConical, Bug, AlertTriangle, Search } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';

const Calculators = () => {
  // Crop data from API
  const [cropCategories, setCropCategories] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loadingCrops, setLoadingCrops] = useState(true);
  
  // Pesticide data from API
  const [pesticideTypes, setPesticideTypes] = useState({});
  const [selectedPestType, setSelectedPestType] = useState('Insecticide');
  const [pesticideCrops, setPesticideCrops] = useState([]);
  const [selectedPesticide, setSelectedPesticide] = useState(null);
  const [pesticidePests, setPesticidePests] = useState([]);
  const [loadingPesticides, setLoadingPesticides] = useState(true);
  const [pesticideSearch, setPesticideSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  
  const [fertilizerData, setFertilizerData] = useState({
    crop: '',
    quantity: '',
  });
  const [pesticideData, setPesticideData] = useState({
    pesticide_id: '',
    crop: '',
    pest: '',
    area: '',
    area_unit: 'hectare',
    pump_capacity: '16',
  });
  const [farmingData, setFarmingData] = useState({
    landSize: '',
    crop: 'wheat',
    expectedYield: '',
  });

  const [results, setResults] = useState({
    fertilizer: null,
    pesticide: null,
    farming: null,
  });
  
  const [calculating, setCalculating] = useState(false);
  const [calculatingPesticide, setCalculatingPesticide] = useState(false);

  // Load crops from API on mount
  useEffect(() => {
    loadCrops();
    loadPesticideData();
  }, []);
  
  const loadCrops = async () => {
    setLoadingCrops(true);
    try {
      const response = await api.get('/fertilizer/crops');
      setCropCategories(response.data.categories || {});
      // Set default category
      const categories = Object.keys(response.data.categories || {});
      if (categories.length > 0) {
        setSelectedCategory(categories[0]);
        const firstCrop = response.data.categories[categories[0]]?.[0];
        if (firstCrop) {
          setFertilizerData(prev => ({ ...prev, crop: firstCrop.id }));
        }
      }
    } catch (error) {
      console.error('Error loading crops:', error);
      // Set fallback data
      setCropCategories({
        cereal: [
          { id: 'wheat', name: 'Wheat' },
          { id: 'rice', name: 'Rice (Paddy)' },
          { id: 'maize', name: 'Maize (Corn)' },
        ],
        vegetable: [
          { id: 'tomato', name: 'Tomato' },
          { id: 'potato', name: 'Potato' },
          { id: 'onion', name: 'Onion' },
        ],
        fruit: [
          { id: 'mango', name: 'Mango' },
          { id: 'banana', name: 'Banana' },
        ]
      });
      setSelectedCategory('cereal');
      setFertilizerData(prev => ({ ...prev, crop: 'wheat' }));
    } finally {
      setLoadingCrops(false);
    }
  };

  // Load pesticide data
  const loadPesticideData = async () => {
    setLoadingPesticides(true);
    try {
      const [typesRes, cropsRes] = await Promise.all([
        api.get('/pesticide/types'),
        api.get('/pesticide/crops')
      ]);
      
      setPesticideTypes(typesRes.data.types || {});
      setPesticideCrops(cropsRes.data.crops || []);
      
      // Set default pesticide from first type
      const firstType = Object.keys(typesRes.data.types || {})[0];
      if (firstType) {
        setSelectedPestType(firstType);
        const firstPesticide = typesRes.data.types[firstType]?.[0];
        if (firstPesticide) {
          setSelectedPesticide(firstPesticide);
          setPesticideData(prev => ({ 
            ...prev, 
            pesticide_id: firstPesticide.id,
            crop: firstPesticide.crops?.[0] || ''
          }));
        }
      }
    } catch (error) {
      console.error('Error loading pesticides:', error);
      // Fallback data
      setPesticideTypes({
        Insecticide: [{ id: 'imidacloprid', name: 'Imidacloprid 17.8% SL', crops: ['Rice', 'Cotton'] }],
        Fungicide: [{ id: 'tricyclazole', name: 'Tricyclazole 75% WP', crops: ['Rice', 'Wheat'] }],
      });
      setPesticideCrops(['Rice', 'Cotton', 'Wheat', 'Tomato', 'Mango']);
    } finally {
      setLoadingPesticides(false);
    }
  };

  // Search pesticides
  const searchPesticides = async (query) => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    try {
      const response = await api.get(`/pesticide/search?q=${encodeURIComponent(query)}`);
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  // Load pests for selected pesticide and crop
  const loadPestsForPesticide = async (pesticideId, crop) => {
    try {
      const url = crop 
        ? `/pesticide/${pesticideId}/pests?crop=${encodeURIComponent(crop)}`
        : `/pesticide/${pesticideId}/pests`;
      const response = await api.get(url);
      setPesticidePests(response.data.pests || []);
      
      // Auto-select first pest
      if (response.data.pests?.length > 0) {
        setPesticideData(prev => ({ ...prev, pest: response.data.pests[0].pest }));
      }
    } catch (error) {
      console.error('Error loading pests:', error);
    }
  };

  // Calculate pesticide requirements
  const calculatePesticide = async () => {
    if (!pesticideData.pesticide_id || !pesticideData.crop || !pesticideData.pest || !pesticideData.area) {
      toast.error('Please fill in all required fields');
      return;
    }

    setCalculatingPesticide(true);
    try {
      const response = await api.post('/pesticide/calculate', {
        pesticide_id: pesticideData.pesticide_id,
        crop: pesticideData.crop,
        pest: pesticideData.pest,
        area: parseFloat(pesticideData.area),
        area_unit: pesticideData.area_unit,
        pump_capacity: parseFloat(pesticideData.pump_capacity) || 16
      });

      if (response.data.success) {
        setResults(prev => ({ ...prev, pesticide: response.data }));
        toast.success('Spray requirements calculated!');
      }
    } catch (error) {
      console.error('Calculation error:', error);
      toast.error(error.message || 'Calculation failed');
    } finally {
      setCalculatingPesticide(false);
    }
  };

  const calculateFertilizer = async () => {
    if (!fertilizerData.crop || !fertilizerData.quantity) {
      toast.error('Please select a crop and enter quantity');
      return;
    }

    setCalculating(true);
    try {
      const response = await api.post('/fertilizer/calculate', {
        crop: fertilizerData.crop,
        quantity: parseFloat(fertilizerData.quantity)
      });

      if (response.data.success) {
        setResults({
          ...results,
          fertilizer: response.data,
        });
        toast.success('Fertilizer requirements calculated!');
      }
    } catch (error) {
      console.error('Calculation error:', error);
      toast.error(error.response?.data?.detail || 'Calculation failed');
      
      // Fallback calculation
      const area = parseFloat(fertilizerData.quantity);
      setResults({
        ...results,
        fertilizer: {
          crop: { name: fertilizerData.crop },
          unit_type: 'hectare',
          nutrients: {
            total_kg: {
              N: (area * 120).toFixed(2),
              P: (area * 60).toFixed(2),
              K: (area * 40).toFixed(2),
            }
          },
          fertilizers: {
            Urea: (area * 260).toFixed(2),
            DAP: (area * 130).toFixed(2),
            MOP: (area * 67).toFixed(2),
          },
          costs: {
            Urea: (area * 260 * 6).toFixed(2),
            DAP: (area * 130 * 25).toFixed(2),
            MOP: (area * 67 * 17).toFixed(2),
            TOTAL: (area * 260 * 6 + area * 130 * 25 + area * 67 * 17).toFixed(2),
          }
        },
      });
    } finally {
      setCalculating(false);
    }
  };

  const calculateFarming = () => {
    if (!farmingData.landSize || !farmingData.expectedYield) {
      toast.error('Please fill all fields');
      return;
    }

    const landSize = parseFloat(farmingData.landSize);
    const expectedYield = parseFloat(farmingData.expectedYield);
    const totalProduction = landSize * expectedYield;
    const estimatedIncome = totalProduction * 2100; // avg price per quintal
    const estimatedCost = landSize * 25000; // avg cost per hectare
    const profit = estimatedIncome - estimatedCost;

    setResults({
      ...results,
      farming: {
        production: totalProduction.toFixed(2),
        income: estimatedIncome.toFixed(2),
        cost: estimatedCost.toFixed(2),
        profit: profit.toFixed(2),
        profitMargin: ((profit / estimatedIncome) * 100).toFixed(2),
      },
    });
    toast.success('Farming economics calculated!');
  };

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="bg-primary/10 p-3 rounded-2xl">
            <Calculator className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Farming Calculators</h1>
            <p className="text-muted-foreground">Calculate fertilizer, pesticide, and farming economics</p>
          </div>
        </div>

        <Tabs defaultValue="fertilizer" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="fertilizer">Fertilizer</TabsTrigger>
            <TabsTrigger value="pesticide">Pesticide</TabsTrigger>
            <TabsTrigger value="farming">Farming</TabsTrigger>
          </TabsList>

          {/* Fertilizer Calculator */}
          <TabsContent value="fertilizer">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="shadow-elegant border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FlaskConical className="h-5 w-5 text-primary" />
                    Crop & Quantity
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {loadingCrops ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-6 w-6 animate-spin text-primary" />
                      <span className="ml-2">Loading crops...</span>
                    </div>
                  ) : (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="crop-category">Crop Category</Label>
                        <select
                          id="crop-category"
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          value={selectedCategory}
                          onChange={(e) => {
                            setSelectedCategory(e.target.value);
                            const firstCrop = cropCategories[e.target.value]?.[0];
                            if (firstCrop) {
                              setFertilizerData({ ...fertilizerData, crop: firstCrop.id });
                            }
                          }}
                        >
                          {Object.keys(cropCategories).map((category) => (
                            <option key={category} value={category}>
                              {category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="fert-crop">Select Crop</Label>
                        <select
                          id="fert-crop"
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          value={fertilizerData.crop}
                          onChange={(e) => setFertilizerData({ ...fertilizerData, crop: e.target.value })}
                        >
                          {(cropCategories[selectedCategory] || []).map((crop) => (
                            <option key={crop.id} value={crop.id}>
                              {crop.name}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="fert-quantity">Quantity (hectares / trees / plants)</Label>
                        <Input
                          id="fert-quantity"
                          type="number"
                          step="0.1"
                          min="0.1"
                          placeholder="e.g., 2.5 hectares or 100 trees"
                          value={fertilizerData.quantity}
                          onChange={(e) => setFertilizerData({ ...fertilizerData, quantity: e.target.value })}
                        />
                        <p className="text-xs text-muted-foreground">
                          Unit depends on crop type (cereals: hectares, fruits: trees, vegetables: plants)
                        </p>
                      </div>
                      <Button 
                        onClick={calculateFertilizer} 
                        className="w-full gradient-primary" 
                        size="lg"
                        disabled={calculating}
                      >
                        {calculating ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                            Calculating...
                          </>
                        ) : (
                          <>
                            <Calculator className="h-4 w-4 mr-2" />
                            Calculate Fertilizer
                          </>
                        )}
                      </Button>
                    </>
                  )}
                </CardContent>
              </Card>

              <Card className="shadow-elegant border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Leaf className="h-5 w-5 text-green-600" />
                    Nutrient Requirements
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {results.fertilizer ? (
                    <div className="space-y-4">
                      {/* Crop Info */}
                      <div className="p-3 bg-primary/5 rounded-lg border">
                        <p className="text-sm font-medium">{results.fertilizer.crop?.name || fertilizerData.crop}</p>
                        <p className="text-xs text-muted-foreground">
                          {fertilizerData.quantity} {results.fertilizer.unit_type || 'hectare'}(s)
                        </p>
                      </div>
                      
                      {/* NPK Requirements */}
                      <div className="grid grid-cols-3 gap-2">
                        <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-lg text-center">
                          <p className="text-xs text-muted-foreground">Nitrogen (N)</p>
                          <p className="text-lg font-bold text-blue-600">{results.fertilizer.nutrients?.total_kg?.N || 0} kg</p>
                        </div>
                        <div className="p-3 bg-orange-50 dark:bg-orange-950 rounded-lg text-center">
                          <p className="text-xs text-muted-foreground">Phosphorus (P)</p>
                          <p className="text-lg font-bold text-orange-600">{results.fertilizer.nutrients?.total_kg?.P || 0} kg</p>
                        </div>
                        <div className="p-3 bg-purple-50 dark:bg-purple-950 rounded-lg text-center">
                          <p className="text-xs text-muted-foreground">Potassium (K)</p>
                          <p className="text-lg font-bold text-purple-600">{results.fertilizer.nutrients?.total_kg?.K || 0} kg</p>
                        </div>
                      </div>
                      
                      {/* Fertilizer Recommendations */}
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Recommended Fertilizers</p>
                        {Object.entries(results.fertilizer.fertilizers || {}).map(([name, amount]) => (
                          amount > 0 && (
                            <div key={name} className="flex justify-between items-center p-2 bg-muted/50 rounded">
                              <span className="text-sm">{name.replace('_', ' ')}</span>
                              <span className="font-medium">{typeof amount === 'number' ? amount.toFixed(2) : amount} kg</span>
                            </div>
                          )
                        ))}
                      </div>
                      
                      {/* Cost Breakdown */}
                      {results.fertilizer.costs && (
                        <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg border-2 border-green-500">
                          <div className="flex items-center gap-2 mb-2">
                            <IndianRupee className="h-4 w-4 text-green-600" />
                            <p className="text-sm font-medium text-green-700 dark:text-green-400">Estimated Cost</p>
                          </div>
                          <p className="text-2xl font-bold text-green-700 dark:text-green-400">
                            ₹{results.fertilizer.costs.TOTAL || 0}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-64 text-muted-foreground">
                      <div className="text-center">
                        <Sprout className="h-12 w-12 mx-auto mb-3 opacity-50" />
                        <p>Select crop and enter quantity</p>
                        <p className="text-xs mt-1">Get NPK + micronutrient recommendations</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Pesticide Calculator */}
          <TabsContent value="pesticide">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="shadow-elegant border-border">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Droplets className="h-5 w-5" />
                    Pesticide Spray Calculator
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">99 pesticides · 21 crops · Precise dosage</p>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Search Pesticide */}
                  <div className="space-y-2">
                    <Label htmlFor="pesticide-search">Search Pesticide</Label>
                    <div className="relative">
                      <Input
                        id="pesticide-search"
                        type="text"
                        placeholder="Search by name (e.g., Imidacloprid)"
                        value={pesticideSearch}
                        onChange={(e) => {
                          setPesticideSearch(e.target.value);
                          searchPesticides(e.target.value);
                        }}
                      />
                      {searchResults.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-background border rounded-md shadow-lg max-h-48 overflow-y-auto">
                          {searchResults.map((result) => (
                            <div
                              key={result.id}
                              className="p-2 hover:bg-primary/10 cursor-pointer border-b last:border-b-0"
                              onClick={() => {
                                setSelectedPesticide(result);
                                setPesticideData(prev => ({ 
                                  ...prev, 
                                  pesticide_id: result.id,
                                  crop: result.crops?.[0] || ''
                                }));
                                setPesticideSearch(result.name);
                                setSearchResults([]);
                                if (result.crops?.[0]) {
                                  loadPestsForPesticide(result.id, result.crops[0]);
                                }
                              }}
                            >
                              <p className="font-medium text-sm">{result.name}</p>
                              <p className="text-xs text-muted-foreground">{result.type} · {result.crops?.length || 0} crops</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Pesticide Type */}
                  <div className="space-y-2">
                    <Label htmlFor="pest-type">Pesticide Type</Label>
                    <select
                      id="pest-type"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={selectedPestType}
                      onChange={(e) => {
                        setSelectedPestType(e.target.value);
                        // Reset selections
                        setSelectedPesticide(null);
                        setPesticideData(prev => ({ ...prev, pesticide_id: '', crop: '', pest: '' }));
                      }}
                    >
                      <option value="">Select Type</option>
                      {Object.keys(pesticideTypes).map((type) => (
                        <option key={type} value={type}>{type} ({pesticideTypes[type]?.length || 0})</option>
                      ))}
                    </select>
                  </div>

                  {/* Select Pesticide from Type */}
                  {selectedPestType && pesticideTypes[selectedPestType] && (
                    <div className="space-y-2">
                      <Label htmlFor="pesticide-select">Select Pesticide</Label>
                      <select
                        id="pesticide-select"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={pesticideData.pesticide_id}
                        onChange={(e) => {
                          const pesticide = pesticideTypes[selectedPestType].find(p => p.id === e.target.value);
                          if (pesticide) {
                            setSelectedPesticide(pesticide);
                            setPesticideData(prev => ({ 
                              ...prev, 
                              pesticide_id: pesticide.id,
                              crop: pesticide.crops?.[0] || ''
                            }));
                            if (pesticide.crops?.[0]) {
                              loadPestsForPesticide(pesticide.id, pesticide.crops[0]);
                            }
                          }
                        }}
                      >
                        <option value="">Select Pesticide</option>
                        {pesticideTypes[selectedPestType].map((p) => (
                          <option key={p.id} value={p.id}>{p.name}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Select Crop */}
                  {selectedPesticide && selectedPesticide.crops && (
                    <div className="space-y-2">
                      <Label htmlFor="pesticide-crop">Target Crop</Label>
                      <select
                        id="pesticide-crop"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={pesticideData.crop}
                        onChange={(e) => {
                          setPesticideData(prev => ({ ...prev, crop: e.target.value, pest: '' }));
                          loadPestsForPesticide(selectedPesticide.id, e.target.value);
                        }}
                      >
                        <option value="">Select Crop</option>
                        {selectedPesticide.crops.map((crop) => (
                          <option key={crop} value={crop}>{crop}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Select Pest */}
                  {pesticidePests.length > 0 && (
                    <div className="space-y-2">
                      <Label htmlFor="pesticide-pest">Target Pest/Disease</Label>
                      <select
                        id="pesticide-pest"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={pesticideData.pest}
                        onChange={(e) => setPesticideData(prev => ({ ...prev, pest: e.target.value }))}
                      >
                        <option value="">Select Pest/Disease</option>
                        {pesticidePests.map((pest) => (
                          <option key={pest.pest} value={pest.pest}>
                            {pest.pest} ({pest.dosage})
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Area Input */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="pest-area">Land Area</Label>
                      <Input
                        id="pest-area"
                        type="number"
                        step="0.1"
                        placeholder="e.g., 2.5"
                        value={pesticideData.area}
                        onChange={(e) => setPesticideData(prev => ({ ...prev, area: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="area-unit">Unit</Label>
                      <select
                        id="area-unit"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={pesticideData.area_unit}
                        onChange={(e) => setPesticideData(prev => ({ ...prev, area_unit: e.target.value }))}
                      >
                        <option value="hectare">Hectare</option>
                        <option value="acre">Acre</option>
                      </select>
                    </div>
                  </div>

                  {/* Pump Capacity */}
                  <div className="space-y-2">
                    <Label htmlFor="pump-capacity">Spray Pump Capacity (liters)</Label>
                    <Input
                      id="pump-capacity"
                      type="number"
                      step="1"
                      placeholder="e.g., 16"
                      value={pesticideData.pump_capacity}
                      onChange={(e) => setPesticideData(prev => ({ ...prev, pump_capacity: e.target.value }))}
                    />
                  </div>

                  <Button 
                    onClick={calculatePesticide} 
                    className="w-full gradient-primary" 
                    size="lg"
                    disabled={calculatingPesticide || !pesticideData.pesticide_id}
                  >
                    {calculatingPesticide ? 'Calculating...' : 'Calculate Spray Requirements'}
                  </Button>
                </CardContent>
              </Card>

              {/* Results Card */}
              <Card className="shadow-elegant border-border">
                <CardHeader>
                  <CardTitle>Spray Requirements</CardTitle>
                </CardHeader>
                <CardContent>
                  {results.pesticide && results.pesticide.success ? (
                    <div className="space-y-4">
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <p className="text-sm text-blue-600 font-medium">{results.pesticide.pesticide?.name}</p>
                        <p className="text-xs text-blue-500">{results.pesticide.target?.crop} · {results.pesticide.target?.pest}</p>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div className="p-4 bg-primary/10 rounded-lg">
                          <p className="text-xs text-muted-foreground">Total Product</p>
                          <p className="text-xl font-bold text-foreground">{results.pesticide.calculation?.total_product_ml} ml</p>
                        </div>
                        <div className="p-4 bg-primary/10 rounded-lg">
                          <p className="text-xs text-muted-foreground">Total Water</p>
                          <p className="text-xl font-bold text-foreground">{results.pesticide.calculation?.total_water_liters} L</p>
                        </div>
                        <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                          <p className="text-xs text-green-600">Pump Refills</p>
                          <p className="text-xl font-bold text-green-700">{results.pesticide.calculation?.pump_refills}</p>
                        </div>
                        <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                          <p className="text-xs text-amber-600">Per Refill</p>
                          <p className="text-xl font-bold text-amber-700">{results.pesticide.calculation?.dose_per_refill_ml} ml</p>
                        </div>
                      </div>

                      {results.pesticide.safety?.pre_harvest_interval_days && (
                        <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                          <p className="text-xs text-red-600">Pre-Harvest Interval (PHI)</p>
                          <p className="text-lg font-bold text-red-700">{results.pesticide.safety.pre_harvest_interval_days} days</p>
                          <p className="text-xs text-red-500">{results.pesticide.safety.message}</p>
                        </div>
                      )}

                      <div className="p-3 bg-muted/50 rounded-lg text-xs text-muted-foreground">
                        <p><strong>Area:</strong> {results.pesticide.input?.area} {results.pesticide.input?.area_unit}</p>
                        <p><strong>Dosage:</strong> {results.pesticide.dosage?.ml_per_hectare} ml/ha</p>
                        <p><strong>Water/ha:</strong> {results.pesticide.dosage?.water_liters_per_hectare} L/ha</p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-64 text-muted-foreground">
                      <div className="text-center">
                        <Droplets className="h-12 w-12 mx-auto mb-3 opacity-50" />
                        <p>Select pesticide and crop to calculate</p>
                        <p className="text-xs mt-2">99 pesticides available across 21 crops</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Farming Calculator */}
          <TabsContent value="farming">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="shadow-elegant border-border">
                <CardHeader>
                  <CardTitle>Input Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="land-size">Land Size (hectares)</Label>
                    <Input
                      id="land-size"
                      type="number"
                      step="0.1"
                      placeholder="e.g., 5"
                      value={farmingData.landSize}
                      onChange={(e) => setFarmingData({ ...farmingData, landSize: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="farm-crop">Crop</Label>
                    <select
                      id="farm-crop"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={farmingData.crop}
                      onChange={(e) => setFarmingData({ ...farmingData, crop: e.target.value })}
                    >
                      <option value="wheat">Wheat</option>
                      <option value="rice">Rice</option>
                      <option value="maize">Maize</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="expected-yield">Expected Yield (quintals/hectare)</Label>
                    <Input
                      id="expected-yield"
                      type="number"
                      step="0.1"
                      placeholder="e.g., 45"
                      value={farmingData.expectedYield}
                      onChange={(e) => setFarmingData({ ...farmingData, expectedYield: e.target.value })}
                    />
                  </div>
                  <Button onClick={calculateFarming} className="w-full gradient-primary" size="lg">
                    Calculate
                  </Button>
                </CardContent>
              </Card>

              <Card className="shadow-elegant border-border">
                <CardHeader>
                  <CardTitle>Estimated Economics</CardTitle>
                </CardHeader>
                <CardContent>
                  {results.farming ? (
                    <div className="space-y-4">
                      <div className="p-4 bg-primary/10 rounded-lg">
                        <p className="text-sm text-muted-foreground">Total Production</p>
                        <p className="text-2xl font-bold text-foreground">{results.farming.production} quintals</p>
                      </div>
                      <div className="p-4 bg-green-50 rounded-lg border-2 border-green-500">
                        <p className="text-sm text-muted-foreground">Estimated Income</p>
                        <p className="text-2xl font-bold text-green-700">₹{results.farming.income}</p>
                      </div>
                      <div className="p-4 bg-red-50 rounded-lg border-2 border-red-500">
                        <p className="text-sm text-muted-foreground">Estimated Cost</p>
                        <p className="text-2xl font-bold text-red-700">₹{results.farming.cost}</p>
                      </div>
                      <div className="p-4 bg-blue-50 rounded-lg border-2 border-blue-500">
                        <p className="text-sm text-muted-foreground">Net Profit</p>
                        <p className="text-2xl font-bold text-blue-700">₹{results.farming.profit}</p>
                        <p className="text-xs text-muted-foreground mt-1">Margin: {results.farming.profitMargin}%</p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-64 text-muted-foreground">
                      <div className="text-center">
                        <Calculator className="h-12 w-12 mx-auto mb-3 opacity-50" />
                        <p>Enter details to calculate</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default Calculators;
