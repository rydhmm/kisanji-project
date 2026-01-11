import { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

const translations = {
  en: {
    // Navigation
    dashboard: 'Dashboard',
    cropRecommendation: 'Crop Recommendation',
    weather: 'Weather Forecast',
    marketPrices: 'Market Prices',
    pestDetection: 'Pest Detection',
    community: 'Community',
    profile: 'Profile',
    schemes: 'Govt Schemes',
    calculators: 'Calculators',
    expertContact: 'Expert Contact',
    diseaseKnowledge: 'Disease Info',
    // Common
    welcome: 'Welcome',
    logout: 'Logout',
    login: 'Login',
    register: 'Register',
    submit: 'Submit',
    cancel: 'Cancel',
    save: 'Save',
    search: 'Search',
    // Dashboard
    goodMorning: 'Good Morning',
    todayWeather: "Today's Weather",
    sprayCondition: 'Spray Condition',
    quickTools: 'Quick Tools',
    features: 'Features',
  },
  hi: {
    // Navigation
    dashboard: 'डैशबोर्ड',
    cropRecommendation: 'फसल सिफारिश',
    weather: 'मौसम पूर्वानुमान',
    marketPrices: 'बाजार मूल्य',
    pestDetection: 'कीट पहचान',
    community: 'समुदाय',
    profile: 'प्रोफाइल',
    schemes: 'सरकारी योजनाएं',
    calculators: 'कैलकुलेटर',
    expertContact: 'विशेषज्ञ संपर्क',
    diseaseKnowledge: 'रोग जानकारी',
    // Common
    welcome: 'स्वागत है',
    logout: 'लॉगआउट',
    login: 'लॉगिन',
    register: 'रजिस्टर करें',
    submit: 'जमा करें',
    cancel: 'रद्द करें',
    save: 'सहेजें',
    search: 'खोजें',
    // Dashboard
    goodMorning: 'सुप्रभात',
    todayWeather: 'आज का मौसम',
    sprayCondition: 'स्प्रे स्थिति',
    quickTools: 'त्वरित उपकरण',
    features: 'सुविधाएं',
  },
  mr: {
    // Navigation
    dashboard: 'डॅशबोर्ड',
    cropRecommendation: 'पीक शिफारस',
    weather: 'हवामान अंदाज',
    marketPrices: 'बाजार किंमती',
    pestDetection: 'कीटक ओळख',
    community: 'समुदाय',
    profile: 'प्रोफाइल',
    schemes: 'सरकारी योजना',
    calculators: 'कॅल्क्युलेटर',
    expertContact: 'तज्ञ संपर्क',
    diseaseKnowledge: 'रोग माहिती',
    // Common
    welcome: 'स्वागत आहे',
    logout: 'बाहेर पडा',
    login: 'लॉगिन',
    register: 'नोंदणी करा',
    submit: 'सबमिट करा',
    cancel: 'रद्द करा',
    save: 'जतन करा',
    search: 'शोधा',
    // Dashboard
    goodMorning: 'सुप्रभात',
    todayWeather: 'आजचे हवामान',
    sprayCondition: 'फवारणी स्थिती',
    quickTools: 'जलद साधने',
    features: 'वैशिष्ट्ये',
  },
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');

  useEffect(() => {
    const storedLang = localStorage.getItem('agri_language');
    if (storedLang && translations[storedLang]) {
      setLanguage(storedLang);
    }
  }, []);

  const changeLanguage = (lang) => {
    if (translations[lang]) {
      setLanguage(lang);
      localStorage.setItem('agri_language', lang);
    }
  };

  const t = (key) => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, changeLanguage, t, availableLanguages: Object.keys(translations) }}>
      {children}
    </LanguageContext.Provider>
  );
};
