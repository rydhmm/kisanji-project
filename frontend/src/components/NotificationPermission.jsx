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
import { Bell, BellOff, Loader2, CheckCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

// API endpoint
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Context for notifications
const NotificationContext = createContext(null);

export const useNotifications = () => useContext(NotificationContext);

export const NotificationProvider = ({ children }) => {
  const [permission, setPermission] = useState('default'); // 'default', 'granted', 'denied'
  const [showPopup, setShowPopup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);

  // Check notification permission on mount
  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission);
      
      const hasAsked = localStorage.getItem('notificationPermissionAsked');
      
      if (!hasAsked && Notification.permission === 'default') {
        // Show popup after a delay
        setTimeout(() => setShowPopup(true), 5000);
      }
      
      // If granted, start polling for notifications
      if (Notification.permission === 'granted') {
        startNotificationPolling();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Request notification permission
  const requestPermission = async () => {
    if (!('Notification' in window)) {
      toast.error('Your browser does not support notifications');
      return false;
    }

    setIsLoading(true);
    
    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      localStorage.setItem('notificationPermissionAsked', 'true');
      
      if (result === 'granted') {
        toast.success('Notifications enabled!');
        
        // Show a test notification
        new Notification('🌾 Kisan.JI', {
          body: 'You will now receive alerts about crop diseases and market updates!',
          icon: '/favicon.ico',
          tag: 'welcome'
        });
        
        // Update preferences on server
        const farmerId = localStorage.getItem('farmerId');
        if (farmerId) {
          await fetch(`${API_BASE}/farmer/notification-preferences`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              farmer_id: farmerId,
              push_enabled: true
            })
          });
        }
        
        startNotificationPolling();
        setShowPopup(false);
        return true;
      } else {
        toast.info('Notifications disabled. You can enable them later in settings.');
        setShowPopup(false);
        return false;
      }
    } catch (error) {
      console.error('Notification permission error:', error);
      toast.error('Failed to enable notifications');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Start polling for notifications
  const startNotificationPolling = () => {
    const farmerId = localStorage.getItem('farmerId');
    if (!farmerId) return;

    // Initial fetch
    fetchNotifications(farmerId);
    
    // Poll every 30 seconds
    const interval = setInterval(() => {
      fetchNotifications(farmerId);
    }, 30000);
    
    return () => clearInterval(interval);
  };

  // Fetch notifications from server
  const fetchNotifications = async (farmerId) => {
    try {
      const response = await fetch(
        `${API_BASE}/farmer/notifications/${farmerId}?unread_only=true&limit=20`
      );
      
      if (response.ok) {
        const data = await response.json();
        const newNotifications = data.notifications || [];
        
        // Check for new notifications
        const currentIds = new Set(notifications.map(n => n.id));
        const newOnes = newNotifications.filter(n => !currentIds.has(n.id));
        
        // Show browser notification for new alerts
        if (permission === 'granted' && newOnes.length > 0) {
          newOnes.forEach(notif => {
            if (notif.type === 'DISEASE_ALERT') {
              showBrowserNotification(notif);
            }
          });
        }
        
        setNotifications(newNotifications);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  // Show browser notification
  const showBrowserNotification = (notif) => {
    if (permission !== 'granted') return;
    
    const notification = new Notification(notif.title, {
      body: notif.message?.substring(0, 100) + '...',
      icon: '/favicon.ico',
      tag: notif.id,
      requireInteraction: notif.priority === 1,
      data: notif.data
    });
    
    notification.onclick = () => {
      window.focus();
      // Navigate to alerts page or show alert details
      notification.close();
    };
  };

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    const farmerId = localStorage.getItem('farmerId');
    if (!farmerId) return;
    
    try {
      await fetch(
        `${API_BASE}/farmer/notifications/${farmerId}/read/${notificationId}`,
        { method: 'POST' }
      );
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    const farmerId = localStorage.getItem('farmerId');
    if (!farmerId) return;
    
    try {
      await fetch(
        `${API_BASE}/farmer/notifications/${farmerId}/read-all`,
        { method: 'POST' }
      );
      
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
      toast.success('All notifications marked as read');
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const handleAllowNotifications = () => {
    requestPermission();
  };

  const handleDenyNotifications = () => {
    localStorage.setItem('notificationPermissionAsked', 'true');
    setShowPopup(false);
    toast.info('You can enable notifications later in Settings');
  };

  return (
    <NotificationContext.Provider value={{
      permission,
      notifications,
      unreadCount,
      requestPermission,
      markAsRead,
      markAllAsRead,
      fetchNotifications
    }}>
      {children}
      
      {/* Notification Permission Popup */}
      <Dialog open={showPopup} onOpenChange={setShowPopup}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-amber-500" />
              Enable Notifications
            </DialogTitle>
            <DialogDescription className="text-left pt-2">
              <div className="space-y-3">
                <p>
                  Stay informed about important updates for your farm:
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li><strong>Disease Alerts</strong> - Get warned when pests or diseases are detected near your farm</li>
                  <li><strong>Weather Warnings</strong> - Be notified of extreme weather conditions</li>
                  <li><strong>Market Updates</strong> - Price changes for your crops</li>
                  <li><strong>Community Updates</strong> - Responses to your questions</li>
                </ul>
                <div className="flex items-center gap-2 p-3 bg-amber-50 rounded-lg border border-amber-200">
                  <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0" />
                  <p className="text-xs text-amber-800">
                    Disease alerts from nearby farmers can help you take preventive action before problems spread to your farm!
                  </p>
                </div>
              </div>
            </DialogDescription>
          </DialogHeader>
          
          <DialogFooter className="flex gap-2 sm:gap-0">
            <Button variant="outline" onClick={handleDenyNotifications} disabled={isLoading}>
              <BellOff className="h-4 w-4 mr-2" />
              Not Now
            </Button>
            <Button onClick={handleAllowNotifications} disabled={isLoading} className="bg-amber-500 hover:bg-amber-600">
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Enabling...
                </>
              ) : (
                <>
                  <Bell className="h-4 w-4 mr-2" />
                  Enable Notifications
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </NotificationContext.Provider>
  );
};

// Notification bell indicator component
export const NotificationBell = ({ onClick }) => {
  const { unreadCount, permission } = useNotifications() || {};
  
  if (permission !== 'granted') {
    return (
      <Button variant="ghost" size="icon" className="relative" onClick={onClick}>
        <BellOff className="h-5 w-5 text-muted-foreground" />
      </Button>
    );
  }
  
  return (
    <Button variant="ghost" size="icon" className="relative" onClick={onClick}>
      <Bell className="h-5 w-5" />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </Button>
  );
};

// Notification list component
export const NotificationList = () => {
  const { notifications, markAsRead, markAllAsRead, unreadCount } = useNotifications() || {};
  
  if (!notifications || notifications.length === 0) {
    return (
      <div className="p-4 text-center text-muted-foreground">
        <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No notifications</p>
      </div>
    );
  }
  
  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'HIGH': return 'border-l-red-500 bg-red-50';
      case 'MEDIUM': return 'border-l-amber-500 bg-amber-50';
      case 'LOW': return 'border-l-green-500 bg-green-50';
      default: return 'border-l-gray-300';
    }
  };
  
  return (
    <div className="max-h-[400px] overflow-y-auto">
      {unreadCount > 0 && (
        <div className="p-2 border-b flex justify-end">
          <Button variant="ghost" size="sm" onClick={markAllAsRead}>
            Mark all as read
          </Button>
        </div>
      )}
      
      {notifications.map((notif) => (
        <div
          key={notif.id}
          className={`p-3 border-b border-l-4 cursor-pointer hover:bg-gray-50 transition-colors
            ${notif.read ? 'opacity-60' : ''} 
            ${getRiskColor(notif.data?.risk_level)}`}
          onClick={() => !notif.read && markAsRead(notif.id)}
        >
          <div className="flex justify-between items-start">
            <h4 className="font-medium text-sm">{notif.title}</h4>
            {!notif.read && (
              <span className="w-2 h-2 rounded-full bg-blue-500 mt-1.5" />
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {notif.message}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {new Date(notif.created_at).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
};

export default NotificationProvider;
