import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Bug, Upload, Loader2, CheckCircle, AlertCircle, Leaf, FlaskConical, Shield, Camera, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import api from '@/services/api';

const PestDetection = () => {
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState('general');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [detecting, setDetecting] = useState(false);
  const [result, setResult] = useState(null);
  const [step, setStep] = useState(1);
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [loadingModels, setLoadingModels] = useState(true);

  // Load available models on mount
  useEffect(() => {
    loadAvailableModels();
    loadDetectionHistory();
  }, []);

  const loadAvailableModels = async () => {
    setLoadingModels(true);
    try {
      const response = await api.getDetectionModels();
      setAvailableModels(response.crops || []);
      
      // Set default to first available model
      if (response.crops && response.crops.length > 0) {
        const firstAvailable = response.crops.find(c => c.available) || response.crops[0];
        setSelectedCrop(firstAvailable.id);
      }
    } catch (error) {
      console.error('Error loading models:', error);
      // Fallback models
      setAvailableModels([
        { id: 'cotton', name: 'Cotton', available: true, diseases: ['Bacterial Blight', 'Curl Virus', 'Fusarium Wilt', 'Healthy'] },
        { id: 'corn', name: 'Corn', available: true, diseases: ['Blight', 'Common Rust', 'Gray Leaf Spot', 'Healthy'] },
        { id: 'sugarcane', name: 'Sugarcane', available: true, diseases: ['Mosaic', 'Red Rot', 'Rust', 'Healthy'] },
        { id: 'wheat', name: 'Wheat', available: true, diseases: ['Brown Rust', 'Healthy', 'Yellow Rust'] },
        { id: 'rice', name: 'Rice', available: true, diseases: ['Blast', 'Blight', 'Tungro'] },
        { id: 'general', name: 'General Plant Scan', available: true, diseases: [] },
        { id: 'pest', name: 'Pest Detection 🐛', available: true, diseases: [] }
      ]);
    } finally {
      setLoadingModels(false);
    }
  };

  const loadDetectionHistory = async () => {
    try {
      const response = await api.getDetectionHistory(10);
      setDetectionHistory(response.history || []);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('Image too large. Maximum size is 10MB.');
        return;
      }

      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result);
        setResult(null); // Clear previous result
        toast.success('Image uploaded successfully');
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDetection = async () => {
    if (!uploadedImage || !imageFile) {
      toast.error('Please upload an image first');
      return;
    }

    setDetecting(true);
    setStep(1);
    setResult(null);

    // Simulate progress steps
    const progressInterval = setInterval(() => {
      setStep(prev => (prev < 3 ? prev + 1 : prev));
    }, 800);

    try {
      // Call actual API
      const response = await api.analyzeImage(imageFile, selectedCrop);
      
      clearInterval(progressInterval);
      setStep(4);

      if (response.success) {
        setResult({
          disease: response.disease,
          confidence: response.confidence,
          severity: response.severity || 'Unknown',
          description: response.description || `Detected ${response.disease} in your ${selectedCrop} crop.`,
          crop_type: response.crop_type || selectedCrop,
          treatments: response.treatments || [],
          preventions: response.preventions || []
        });
        toast.success('Analysis complete!');
        loadDetectionHistory(); // Refresh history
      } else {
        toast.error(response.error || 'Detection failed');
      }
    } catch (error) {
      clearInterval(progressInterval);
      console.error('Detection error:', error);
      toast.error(error.message || 'Detection failed. Please try again.');
    } finally {
      setDetecting(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'moderate': case 'moderate to high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'low': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'none': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getSelectedModel = () => {
    return availableModels.find(m => m.id === selectedCrop);
  };

  const detectionSteps = [
    { id: 1, label: 'Loading Model', icon: Loader2 },
    { id: 2, label: 'Analyzing Image', icon: Loader2 },
    { id: 3, label: 'Detecting Disease', icon: Loader2 },
    { id: 4, label: 'Complete', icon: CheckCircle },
  ];

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Enhanced Header */}
        <motion.div 
          className="flex items-center justify-between"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-4">
            <motion.div 
              className="bg-gradient-to-br from-red-500/20 to-orange-500/20 p-4 rounded-2xl border border-red-500/20 shadow-lg shadow-red-500/20"
              whileHover={{ scale: 1.1, rotate: 10 }}
              transition={{ type: 'spring' }}
            >
              <Bug className="h-10 w-10 text-red-400" />
            </motion.div>
            <div>
              <h1 className="text-4xl font-bold text-white">AI Disease Detection</h1>
              <p className="text-gray-400 mt-1">Multi-crop disease detection with ONNX & YOLO models</p>
            </div>
          </div>
          <motion.div 
            className="text-right hidden md:block glass-card px-4 py-3 rounded-xl border border-white/10"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <p className="text-emerald-400 font-semibold">{availableModels.filter(m => m.available).length} models available</p>
            <p className="text-xs text-gray-500">Cotton · Corn · Rice · Wheat · Sugarcane</p>
          </motion.div>
        </motion.div>

        <div className="grid lg:grid-cols-5 gap-6">
          {/* Left: Upload Section */}
          <motion.div 
            className="lg:col-span-2 space-y-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            {/* Model Selection */}
            <Card className="glass-card border-white/10 shadow-xl">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2 text-white">
                  <Leaf className="h-4 w-4 text-emerald-400" />
                  Select Crop / Detection Model
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={selectedCrop} onValueChange={setSelectedCrop} disabled={loadingModels}>
                  <SelectTrigger className="bg-white/5 border-white/10 text-white">
                    <SelectValue placeholder={loadingModels ? "Loading models..." : "Choose crop"} />
                  </SelectTrigger>
                  <SelectContent className="glass border-white/10">
                    {availableModels.map((model) => (
                      <SelectItem 
                        key={model.id} 
                        value={model.id}
                        disabled={!model.available}
                        className="hover:bg-white/10"
                      >
                        <div className="flex items-center gap-2">
                          <span>{model.name}</span>
                          {!model.available && (
                            <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30 text-xs">Unavailable</Badge>
                          )}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {/* Show diseases for selected model */}
                {getSelectedModel()?.diseases?.length > 0 && (
                  <div className="mt-3 p-3 bg-muted/50 rounded-lg">
                    <p className="text-xs text-muted-foreground mb-2">Detectable diseases:</p>
                    <div className="flex flex-wrap gap-1">
                      {getSelectedModel().diseases.map((disease, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {disease}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Image Upload */}
            <Card className="shadow-elegant border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Camera className="h-4 w-4" />
                  Upload Crop Image
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    id="crop-image"
                  />
                  <label htmlFor="crop-image" className="cursor-pointer block">
                    {uploadedImage ? (
                      <div className="relative">
                        <img src={uploadedImage} alt="Uploaded crop" className="max-h-48 mx-auto rounded-lg mb-3 shadow-md" />
                        <Badge className="absolute top-2 right-2 bg-green-500">
                          <CheckCircle className="h-3 w-3 mr-1" /> Uploaded
                        </Badge>
                      </div>
                    ) : (
                      <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    )}
                    <p className="text-sm font-medium text-foreground">
                      {uploadedImage ? 'Click to change image' : 'Click to upload image'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">JPG, PNG (Max 10MB)</p>
                  </label>
                </div>
                <Button
                  onClick={handleDetection}
                  disabled={!uploadedImage || detecting}
                  className="w-full mt-4 gradient-primary"
                  size="lg"
                >
                  {detecting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Detecting...
                    </>
                  ) : (
                    'Detect Disease'
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Detection Progress */}
            {detecting && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Card className="shadow-elegant border-border">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      {detectionSteps.map((stepItem) => {
                        const Icon = stepItem.icon;
                        const isActive = step === stepItem.id;
                        const isCompleted = step > stepItem.id;
                        return (
                          <div key={stepItem.id} className="flex items-center gap-3">
                            <div
                              className={`p-2 rounded-full ${
                                isCompleted
                                  ? 'bg-primary text-primary-foreground'
                                  : isActive
                                  ? 'bg-primary/20 text-primary'
                                  : 'bg-muted text-muted-foreground'
                              }`}
                            >
                              <Icon className={`h-4 w-4 ${isActive ? 'animate-spin' : ''}`} />
                            </div>
                            <span
                              className={`text-sm ${
                                isActive || isCompleted ? 'text-foreground font-medium' : 'text-muted-foreground'
                              }`}
                            >
                              {stepItem.label}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                    <Progress value={(step / 4) * 100} className="mt-4" />
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </motion.div>

          {/* Right: Results Section */}
          <div className="lg:col-span-3">
            {result ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                {/* Detection Result */}
                <Card className="shadow-elegant border-primary">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-2xl font-bold text-foreground">{result.disease}</h3>
                          {result.crop_type && (
                            <Badge variant="outline" className="capitalize">
                              <Leaf className="h-3 w-3 mr-1" />
                              {result.crop_type}
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{result.description}</p>
                      </div>
                      <Badge className="bg-primary text-primary-foreground text-lg px-4 py-2">
                        {result.confidence?.toFixed(1) || result.confidence}%
                      </Badge>
                    </div>
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm ${getSeverityColor(result.severity)}`}>
                      <AlertCircle className="h-4 w-4" />
                      Severity: {result.severity}
                    </div>
                  </CardContent>
                </Card>

                {/* Treatment Recommendations */}
                {result.treatments && result.treatments.length > 0 && (
                  <Card className="shadow-elegant border-border">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <FlaskConical className="h-5 w-5 text-primary" />
                        Treatment Recommendations
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {result.treatments.map((treatment, index) => (
                        <div key={index} className="p-4 bg-muted rounded-lg">
                          <p className="font-medium text-foreground">{treatment.name}</p>
                          <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                            <p className="text-muted-foreground">
                              Dosage: <span className="text-foreground font-medium">{treatment.dosage}</span>
                            </p>
                            <p className="text-muted-foreground">
                              Timing: <span className="text-foreground font-medium">{treatment.timing}</span>
                            </p>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Prevention Tips */}
                {result.preventions && result.preventions.length > 0 && (
                  <Card className="shadow-elegant border-border">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5 text-green-600" />
                        Prevention Tips
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {result.preventions.map((tip, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                            <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                            <span>{tip}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Healthy Plant Message */}
                {result.disease?.toLowerCase().includes('healthy') && (
                  <Card className="shadow-elegant border-green-500 bg-green-50 dark:bg-green-900/20">
                    <CardContent className="p-6 text-center">
                      <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                      <h3 className="text-xl font-bold text-green-700 dark:text-green-400 mb-2">
                        Your {result.crop_type || 'crop'} looks healthy! 🌱
                      </h3>
                      <p className="text-green-600 dark:text-green-300">
                        No diseases detected. Keep up the good agricultural practices!
                      </p>
                    </CardContent>
                  </Card>
                )}
              </motion.div>
            ) : (
              <Card className="shadow-elegant border-border h-full">
                <CardContent className="p-12 text-center flex flex-col items-center justify-center h-full">
                  <Bug className="h-20 w-20 mb-6 text-muted-foreground" />
                  <h3 className="text-xl font-semibold text-foreground mb-2">No Detection Yet</h3>
                  <p className="text-muted-foreground max-w-md">
                    Upload a crop image and click 'Detect Disease' to get AI-powered disease identification and treatment recommendations.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Detection History */}
        {detectionHistory.length > 0 && (
          <Card className="shadow-elegant border-border mt-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <RefreshCw className="h-5 w-5" />
                Recent Detection History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                {detectionHistory.slice(0, 4).map((item, index) => (
                  <div key={index} className="p-4 bg-muted rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant="outline" className="capitalize">
                        {item.crop_type}
                      </Badge>
                      <Badge className={getSeverityColor(item.severity)}>
                        {item.confidence?.toFixed(0)}%
                      </Badge>
                    </div>
                    <p className="font-medium text-sm text-foreground">{item.disease}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default PestDetection;
