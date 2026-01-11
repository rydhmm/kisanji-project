// API Service for connecting frontend to backend
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api' 
    : 'https://kisanji-backend.onrender.com/api');

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Request failed' }));
        throw new Error(error.detail || error.message || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Generic HTTP methods for easy use
  async get(endpoint) {
    const data = await this.request(endpoint);
    return { data };
  }

  async post(endpoint, body) {
    const data = await this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return { data };
  }

  // Health Check
  async healthCheck() {
    return this.request('/health');
  }

  // =====================================
  // AUTH / USER APIs
  // =====================================
  
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(loginData) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(loginData),
    });
  }

  async getUsers() {
    return this.request('/users');
  }

  async getUser(userId) {
    return this.request(`/users/${userId}`);
  }

  async getFarmerProfile(userId) {
    return this.request(`/farmer-profile/${userId}`);
  }

  async saveFarmerProfile(profileData) {
    return this.request('/farmer-profile', {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
  }

  // =====================================
  // MARKET PRICES APIs
  // =====================================
  
  async getMarketPrices(filters = {}) {
    const params = new URLSearchParams();
    if (filters.crop_name) params.append('crop_name', filters.crop_name);
    if (filters.mandi_name) params.append('mandi_name', filters.mandi_name);
    
    const queryString = params.toString();
    return this.request(`/market-prices${queryString ? `?${queryString}` : ''}`);
  }

  async addMarketPrice(priceData) {
    return this.request('/market-prices', {
      method: 'POST',
      body: JSON.stringify(priceData),
    });
  }

  // =====================================
  // WEATHER APIs
  // =====================================
  
  async getWeather(villageId = null) {
    const params = villageId ? `?village_id=${villageId}` : '';
    return this.request(`/weather${params}`);
  }

  async addWeatherData(weatherData) {
    return this.request('/weather', {
      method: 'POST',
      body: JSON.stringify(weatherData),
    });
  }

  // Live Weather API (OpenWeatherMap)
  async getWeatherForecast(lat = 30.3165, lon = 78.0322, locationName = "Dehradun") {
    return this.request(`/weather/forecast?lat=${lat}&lon=${lon}&location_name=${encodeURIComponent(locationName)}`);
  }

  // =====================================
  // MANDI / LIVE MARKET PRICES APIs
  // =====================================

  async getMandiPrices(state = "Uttarakhand", limit = 20) {
    return this.request(`/mandi/prices?state=${encodeURIComponent(state)}&limit=${limit}`);
  }

  async getPriceHistory(crop) {
    return this.request(`/mandi/price-history/${encodeURIComponent(crop)}`);
  }

  // =====================================
  // CROP RECOMMENDATION API
  // =====================================

  async getCropRecommendation(lat = 30.3165, lon = 78.0322, soilType = "loamy", waterSource = "rainfall") {
    return this.request(`/crop-recommendation?lat=${lat}&lon=${lon}&soil_type=${soilType}&water_source=${waterSource}`);
  }

  // =====================================
  // SCHEMES APIs
  // =====================================
  
  async getSchemes() {
    return this.request('/schemes');
  }

  async addScheme(schemeData) {
    return this.request('/schemes', {
      method: 'POST',
      body: JSON.stringify(schemeData),
    });
  }

  // =====================================
  // VILLAGES APIs
  // =====================================
  
  async getVillages(filters = {}) {
    const params = new URLSearchParams();
    if (filters.state) params.append('state', filters.state);
    if (filters.district) params.append('district', filters.district);
    
    const queryString = params.toString();
    return this.request(`/villages${queryString ? `?${queryString}` : ''}`);
  }

  // =====================================
  // CROPS APIs
  // =====================================
  
  async getCrops(season = null) {
    const params = season ? `?season=${season}` : '';
    return this.request(`/crops${params}`);
  }

  async getGanMapping() {
    return this.request('/gan');
  }

  // =====================================
  // DISEASES APIs
  // =====================================
  
  async getAllDiseases() {
    return this.request('/diseases');
  }

  async getDiseasesByCrop(cropName) {
    return this.request(`/diseases/${encodeURIComponent(cropName)}`);
  }

  async getDiseaseCollections() {
    return this.request('/disease-collections');
  }

  // =====================================
  // DISEASE RESULTS APIs
  // =====================================
  
  async getDiseaseResults(farmerId = null) {
    const params = farmerId ? `?farmer_id=${farmerId}` : '';
    return this.request(`/disease-results${params}`);
  }

  async saveDiseaseResult(resultData) {
    return this.request('/disease-results', {
      method: 'POST',
      body: JSON.stringify(resultData),
    });
  }

  // =====================================
  // ADVISORIES APIs
  // =====================================
  
  async getAdvisories(farmerId = null) {
    const params = farmerId ? `?farmer_id=${farmerId}` : '';
    return this.request(`/advisories${params}`);
  }

  async addAdvisory(advisoryData) {
    return this.request('/advisories', {
      method: 'POST',
      body: JSON.stringify(advisoryData),
    });
  }

  // =====================================
  // FIELDS APIs
  // =====================================
  
  async getFields(farmerId = null) {
    const params = farmerId ? `?farmer_id=${farmerId}` : '';
    return this.request(`/fields${params}`);
  }

  // =====================================
  // CROP IMAGES APIs
  // =====================================
  
  async getCropImages(farmerId = null) {
    const params = farmerId ? `?farmer_id=${farmerId}` : '';
    return this.request(`/crop-images${params}`);
  }

  // =====================================
  // VOICE QUERIES APIs
  // =====================================
  
  async getVoiceQueries(farmerId = null) {
    const params = farmerId ? `?farmer_id=${farmerId}` : '';
    return this.request(`/voice-queries${params}`);
  }

  // =====================================
  // SCHEME NOTIFICATIONS APIs
  // =====================================
  
  async getSchemeNotifications() {
    return this.request('/scheme-notifications');
  }

  // =====================================
  // FERTILIZER CALCULATOR APIs
  // =====================================
  
  async getFertilizerCrops() {
    return this.request('/fertilizer/crops');
  }

  async getCropDetails(cropId) {
    return this.request(`/fertilizer/crop/${cropId}`);
  }

  async calculateFertilizer(crop, quantity) {
    return this.request('/fertilizer/calculate', {
      method: 'POST',
      body: JSON.stringify({ crop, quantity }),
    });
  }

  async getFertilizerList() {
    return this.request('/fertilizer/fertilizers');
  }

  async getFertilizerHistory() {
    return this.request('/fertilizer/history');
  }

  // =====================================
  // PESTICIDE CALCULATOR APIs
  // =====================================

  async getPesticideTypes() {
    return this.request('/pesticide/types');
  }

  async getAllPesticides() {
    return this.request('/pesticide/all');
  }

  async getPesticideCrops() {
    return this.request('/pesticide/crops');
  }

  async searchPesticides(query) {
    return this.request(`/pesticide/search?q=${encodeURIComponent(query)}`);
  }

  async getPesticidesForCrop(crop) {
    return this.request(`/pesticide/for-crop/${encodeURIComponent(crop)}`);
  }

  async getPesticideDetails(pesticideId) {
    return this.request(`/pesticide/${pesticideId}`);
  }

  async getPestsForPesticide(pesticideId, crop = null) {
    const url = crop 
      ? `/pesticide/${pesticideId}/pests?crop=${encodeURIComponent(crop)}`
      : `/pesticide/${pesticideId}/pests`;
    return this.request(url);
  }

  async calculatePesticide(data) {
    return this.request('/pesticide/calculate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPesticideHistory() {
    return this.request('/pesticide/history');
  }

  // =====================================
  // DISEASE DETECTION APIs
  // =====================================

  async getDetectionModels() {
    return this.request('/detection/models');
  }

  async analyzeImage(imageFile, cropType = 'general') {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('crop_type', cropType);

    const url = `${this.baseUrl}/detection/analyze`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData, // No Content-Type header - browser sets it automatically
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Analysis failed' }));
      throw new Error(error.detail || error.message);
    }

    return response.json();
  }

  async getDetectionHistory(limit = 20) {
    return this.request(`/detection/history?limit=${limit}`);
  }

  async getDiseaseInfo(diseaseName) {
    return this.request(`/detection/disease-info/${encodeURIComponent(diseaseName)}`);
  }

  // =====================================
  // VOICE CHAT APIs (with FormData support)
  // =====================================
  
  async voiceChat(message, language = 'en', farmerId = null) {
    return this.request('/voice/chat', {
      method: 'POST',
      body: JSON.stringify({ message, language, farmer_id: farmerId }),
    });
  }

  async transcribeAudio(audioBlob, farmerId = null) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    if (farmerId) formData.append('farmer_id', farmerId);

    const url = `${this.baseUrl}/voice/transcribe`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData, // No Content-Type header - browser sets it automatically with boundary
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Transcription failed' }));
      throw new Error(error.detail || error.message);
    }
    
    return response.json();
  }

  async voiceAsk(audioBlob, farmerId = null, generateAudio = false) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    if (farmerId) formData.append('farmer_id', farmerId);
    formData.append('generate_audio', generateAudio.toString());

    const url = `${this.baseUrl}/voice/ask`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Voice query failed' }));
      throw new Error(error.detail || error.message);
    }
    
    return response.json();
  }}

// Export a singleton instance
const apiService = new ApiService();
export default apiService;