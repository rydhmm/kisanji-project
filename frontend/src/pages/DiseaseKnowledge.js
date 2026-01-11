import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { BookOpen, Bug, Leaf, Droplets, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import apiService from '@/services/api';

const DiseaseKnowledge = () => {
  const [selectedCrop, setSelectedCrop] = useState('all');
  const [crops, setCrops] = useState(['all']);
  const [diseases, setDiseases] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch disease collections and crops on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch disease collections to get crop list
        const collections = await apiService.getDiseaseCollections();
        const cropList = ['all', ...collections.map(c => c.crop_type.toLowerCase())];
        setCrops(cropList);
        
        // Fetch all diseases
        const allDiseases = await apiService.getAllDiseases();
        setDiseases(allDiseases);
      } catch (error) {
        console.error('Error fetching disease data:', error);
        // Fallback data
        setCrops(['all', 'wheat', 'rice', 'tomato', 'potato', 'cotton', 'maize']);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter diseases based on selected crop
  const filteredDiseases = selectedCrop === 'all' 
    ? diseases 
    : diseases.filter(d => d.crop_name?.toLowerCase() === selectedCrop.toLowerCase() || 
                          d.crop_type?.toLowerCase() === selectedCrop.toLowerCase());

  // Group diseases by type (for demo purposes, we'll categorize based on disease name patterns)
  const categorizedDiseases = {
    fungicide: filteredDiseases.filter(d => 
      d.disease_name?.toLowerCase().includes('rust') ||
      d.disease_name?.toLowerCase().includes('blight') ||
      d.disease_name?.toLowerCase().includes('mildew') ||
      d.disease_name?.toLowerCase().includes('rot') ||
      d.disease_name?.toLowerCase().includes('spot') ||
      d.disease_name?.toLowerCase().includes('wilt')
    ),
    insecticide: filteredDiseases.filter(d => 
      d.disease_name?.toLowerCase().includes('borer') ||
      d.disease_name?.toLowerCase().includes('aphid') ||
      d.disease_name?.toLowerCase().includes('curl')
    ),
    bacterial: filteredDiseases.filter(d => 
      d.disease_name?.toLowerCase().includes('mosaic') ||
      d.disease_name?.toLowerCase().includes('virus') ||
      !d.disease_name?.toLowerCase().includes('rust') &&
      !d.disease_name?.toLowerCase().includes('blight') &&
      !d.disease_name?.toLowerCase().includes('mildew')
    ).slice(0, 5),
  };

  // If no categorization works, distribute diseases
  if (categorizedDiseases.fungicide.length === 0 && categorizedDiseases.insecticide.length === 0) {
    const third = Math.ceil(filteredDiseases.length / 3);
    categorizedDiseases.fungicide = filteredDiseases.slice(0, third);
    categorizedDiseases.insecticide = filteredDiseases.slice(third, third * 2);
    categorizedDiseases.bacterial = filteredDiseases.slice(third * 2);
  }

  // Helper function to render disease card
  const DiseaseCard = ({ disease, index, badgeColor, badgeText }) => (
    <motion.div
      key={index}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card className="shadow-elegant border-border hover:shadow-lg transition-all overflow-hidden">
        <img
          src={disease.disease_image_url?.[0] || 'https://images.pexels.com/photos/265216/pexels-photo-265216.jpeg'}
          alt={disease.disease_name}
          className="w-full h-48 object-cover"
          onError={(e) => { e.target.src = 'https://images.pexels.com/photos/265216/pexels-photo-265216.jpeg'; }}
        />
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl">{disease.disease_name}</CardTitle>
              <p className="text-sm text-muted-foreground italic mt-1">
                {disease.crop_name || disease.crop_type}
              </p>
            </div>
            <Badge className={badgeColor}>{badgeText}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold text-sm text-foreground mb-2">Crop</h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {disease.crop_name || disease.crop_type}
            </p>
          </div>
          {disease.disease_image_url?.length > 1 && (
            <div className="bg-primary/10 p-4 rounded-lg">
              <h4 className="font-semibold text-sm text-foreground mb-2">Additional Images</h4>
              <p className="text-sm text-muted-foreground">{disease.disease_image_url.length} images available</p>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading disease database...</span>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-primary/10 p-3 rounded-2xl">
              <BookOpen className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Disease Knowledge Base</h1>
              <p className="text-muted-foreground">Comprehensive crop disease information from database ({diseases.length} diseases)</p>
            </div>
          </div>

          {/* Crop Selector */}
          <Select value={selectedCrop} onValueChange={setSelectedCrop}>
            <SelectTrigger className="w-full sm:w-64">
              <SelectValue placeholder="Select crop" />
            </SelectTrigger>
            <SelectContent>
              {crops.map((crop) => (
                <SelectItem key={crop} value={crop}>
                  {crop.charAt(0).toUpperCase() + crop.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Disease Categories */}
        <Tabs defaultValue="fungicide" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="fungicide" className="flex items-center gap-2">
              <Leaf className="h-4 w-4" />
              <span className="hidden sm:inline">Fungal ({categorizedDiseases.fungicide.length})</span>
              <span className="sm:hidden">Fungal</span>
            </TabsTrigger>
            <TabsTrigger value="insecticide" className="flex items-center gap-2">
              <Bug className="h-4 w-4" />
              <span className="hidden sm:inline">Insect ({categorizedDiseases.insecticide.length})</span>
              <span className="sm:hidden">Insect</span>
            </TabsTrigger>
            <TabsTrigger value="bacterial" className="flex items-center gap-2">
              <Droplets className="h-4 w-4" />
              <span className="hidden sm:inline">Other ({categorizedDiseases.bacterial.length})</span>
              <span className="sm:hidden">Other</span>
            </TabsTrigger>
          </TabsList>

          {/* Fungal Diseases */}
          <TabsContent value="fungicide" className="space-y-4">
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {categorizedDiseases.fungicide.map((disease, index) => (
                <DiseaseCard key={index} disease={disease} index={index} badgeColor="bg-green-500" badgeText="Fungal" />
              ))}
            </div>
            {categorizedDiseases.fungicide.length === 0 && (
              <p className="text-center text-muted-foreground py-8">No fungal diseases found for this crop</p>
            )}
          </TabsContent>

          {/* Insect Diseases */}
          <TabsContent value="insecticide" className="space-y-4">
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {categorizedDiseases.insecticide.map((disease, index) => (
                <DiseaseCard key={index} disease={disease} index={index} badgeColor="bg-orange-500" badgeText="Insect" />
              ))}
            </div>
            {categorizedDiseases.insecticide.length === 0 && (
              <p className="text-center text-muted-foreground py-8">No insect diseases found for this crop</p>
            )}
          </TabsContent>

          {/* Other Diseases */}
          <TabsContent value="bacterial" className="space-y-4">
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {categorizedDiseases.bacterial.map((disease, index) => (
                <DiseaseCard key={index} disease={disease} index={index} badgeColor="bg-blue-500" badgeText="Other" />
              ))}
            </div>
            {categorizedDiseases.bacterial.length === 0 && (
              <p className="text-center text-muted-foreground py-8">No other diseases found for this crop</p>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default DiseaseKnowledge;
