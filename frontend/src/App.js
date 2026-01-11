import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import Dashboard from '@/pages/Dashboard';
import CropRecommendation from '@/pages/CropRecommendation';
import Weather from '@/pages/Weather';
import MarketPrices from '@/pages/MarketPrices';
import PestDetection from '@/pages/PestDetection';
import Community from '@/pages/Community';
import Profile from '@/pages/Profile';
import DiseaseKnowledge from '@/pages/DiseaseKnowledge';
import Schemes from '@/pages/Schemes';
import Calculators from '@/pages/Calculators';
import ExpertContact from '@/pages/ExpertContact';
import Auth from '@/pages/Auth';
import { LanguageProvider } from '@/contexts/LanguageContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { LocationProvider } from '@/components/LocationPermission';
import { NotificationProvider } from '@/components/NotificationPermission';
import { BackgroundProvider } from '@/components/BackgroundSlider';
import Chatbot from '@/components/Chatbot';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <LocationProvider>
          <NotificationProvider>
            <BrowserRouter>
              <BackgroundProvider>
                <div className="App min-h-screen">
                  <Routes>
                    <Route path="/auth" element={<Auth />} />
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/crop-recommendation" element={<CropRecommendation />} />
                    <Route path="/weather" element={<Weather />} />
                    <Route path="/market-prices" element={<MarketPrices />} />
                    <Route path="/pest-detection" element={<PestDetection />} />
                    <Route path="/community" element={<Community />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/disease-knowledge" element={<DiseaseKnowledge />} />
                    <Route path="/schemes" element={<Schemes />} />
                    <Route path="/calculators" element={<Calculators />} />
                    <Route path="/expert-contact" element={<ExpertContact />} />
                  </Routes>
                  <Chatbot />
                  <Toaster position="top-center" richColors />
                </div>
              </BackgroundProvider>
            </BrowserRouter>
          </NotificationProvider>
        </LocationProvider>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
