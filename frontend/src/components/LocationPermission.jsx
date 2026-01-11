import React, { useState, useEffect, createContext, useContext } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { MapPin, Navigation, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';

// API endpoint
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Context for location data
const LocationContext = createContext(null);

export const useLocation = () => useContext(LocationContext);

export const LocationProvider = ({ children }) => {
  const [location, setLocation] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [permissionStatus, setPermissionStatus] = useState('prompt'); // 'granted', 'denied', 'prompt'

  // Check if we've already asked for permission
  useEffect(() => {
    const hasAsked = localStorage.getItem('locationPermissionAsked');
    const savedLocation = localStorage.getItem('farmerLocation');
    
    if (savedLocation) {
      try {
        setLocation(JSON.parse(savedLocation));
      } catch (e) {
        console.error('Error parsing saved location:', e);
      }
    }
    
    // Check browser permission status
    if ('permissions' in navigator) {
      navigator.permissions.query({ name: 'geolocation' }).then((result) => {
        setPermissionStatus(result.state);
        
        // If already granted, get location automatically
        if (result.state === 'granted') {
          getCurrentLocation();
        } else if (!hasAsked && result.state === 'prompt') {
          // Show popup on first visit
          setTimeout(() => setShowPopup(true), 2000);
        }
        
        // Listen for permission changes
        result.onchange = () => {
          setPermissionStatus(result.state);
        };
      });
    } else if (!hasAsked) {
      // For browsers that don't support permissions API
      setTimeout(() => setShowPopup(true), 2000);
    }
  }, []);

  // Get current location
  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser');
      toast.error('Geolocation not supported');
      return;
    }

    setIsLoading(true);
    
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const newLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date().toISOString()
        };
        
        setLocation(newLocation);
        setLocationError(null);
        setIsLoading(false);
        localStorage.setItem('farmerLocation', JSON.stringify(newLocation));
        localStorage.setItem('locationPermissionAsked', 'true');
        
        // Send to backend
        try {
          const farmerId = localStorage.getItem('farmerId') || `FARMER-${Date.now()}`;
          localStorage.setItem('farmerId', farmerId);
          
          await fetch(`${API_BASE}/farmer/location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              farmer_id: farmerId,
              latitude: newLocation.latitude,
              longitude: newLocation.longitude,
              accuracy: newLocation.accuracy,
              timestamp: newLocation.timestamp
            })
          });
          
          toast.success('Location saved successfully!');
        } catch (error) {
          console.error('Error saving location:', error);
        }
        
        setShowPopup(false);
      },
      (error) => {
        setIsLoading(false);
        let errorMessage = 'Unable to get your location';
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location permission denied';
            setPermissionStatus('denied');
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out';
            break;
          default:
            break;
        }
        
        setLocationError(errorMessage);
        toast.error(errorMessage);
        localStorage.setItem('locationPermissionAsked', 'true');
        setShowPopup(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
      }
    );
  };

  // Watch location changes
  const startWatchingLocation = () => {
    if (!navigator.geolocation) return null;
    
    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        const newLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date().toISOString()
        };
        setLocation(newLocation);
        localStorage.setItem('farmerLocation', JSON.stringify(newLocation));
      },
      (error) => console.error('Watch location error:', error),
      { enableHighAccuracy: true, maximumAge: 60000 }
    );
    
    return watchId;
  };

  const handleAllowLocation = () => {
    getCurrentLocation();
  };

  const handleDenyLocation = () => {
    localStorage.setItem('locationPermissionAsked', 'true');
    setShowPopup(false);
    toast.info('You can enable location access later in Settings');
  };

  const resetLocationPermission = () => {
    localStorage.removeItem('locationPermissionAsked');
    localStorage.removeItem('farmerLocation');
    setLocation(null);
    setShowPopup(true);
  };

  return (
    <LocationContext.Provider value={{
      location,
      locationError,
      isLoading,
      permissionStatus,
      getCurrentLocation,
      startWatchingLocation,
      resetLocationPermission
    }}>
      {children}
      
      {/* Location Permission Popup */}
      <Dialog open={showPopup} onOpenChange={setShowPopup}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-green-600" />
              Enable Location Access
            </DialogTitle>
            <DialogDescription className="text-left pt-2">
              <div className="space-y-3">
                <p>
                  Kisan.JI uses your location to provide personalized farming assistance:
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li><strong>Weather Updates</strong> - Get accurate local weather forecasts</li>
                  <li><strong>Crop Recommendations</strong> - Based on your local climate</li>
                  <li><strong>Disease Alerts</strong> - Get warned when pests/diseases are detected near you</li>
                  <li><strong>Market Prices</strong> - Find nearby mandis and their prices</li>
                </ul>
                <p className="text-xs text-muted-foreground">
                  Your location data is stored securely and only used to improve your farming experience.
                </p>
              </div>
            </DialogDescription>
          </DialogHeader>
          
          <DialogFooter className="flex gap-2 sm:gap-0">
            <Button variant="outline" onClick={handleDenyLocation} disabled={isLoading}>
              <XCircle className="h-4 w-4 mr-2" />
              Not Now
            </Button>
            <Button onClick={handleAllowLocation} disabled={isLoading} className="bg-green-600 hover:bg-green-700">
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Getting Location...
                </>
              ) : (
                <>
                  <Navigation className="h-4 w-4 mr-2" />
                  Allow Location
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </LocationContext.Provider>
  );
};

// Small location indicator component
export const LocationIndicator = () => {
  const { location, isLoading, getCurrentLocation, permissionStatus } = useLocation() || {};
  
  if (!location && permissionStatus !== 'granted') {
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={getCurrentLocation}
        className="text-muted-foreground hover:text-foreground"
      >
        <MapPin className="h-4 w-4 mr-1" />
        Enable Location
      </Button>
    );
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 mr-1 animate-spin" />
        Getting location...
      </div>
    );
  }
  
  if (location) {
    return (
      <div className="flex items-center text-sm text-green-600">
        <CheckCircle className="h-4 w-4 mr-1" />
        Location Active
      </div>
    );
  }
  
  return null;
};

export default LocationProvider;
