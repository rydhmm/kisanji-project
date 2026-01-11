import { useState, useEffect, createContext, useContext } from 'react';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// Page-specific image configurations
const pageBackgrounds = {
  '/': {
    images: ['/images/1i.png', '/images/7i.jpg', '/images/9i.png', '/images/12i.png'],
    overlay: 'from-black/70 via-black/50 to-black/70',
    accent: 'emerald'
  },
  '/crop-recommendation': {
    images: ['/images/7i.jpg', '/images/10i.jpg', '/images/15.jpeg'],
    overlay: 'from-emerald-950/80 via-black/60 to-emerald-950/80',
    accent: 'green'
  },
  '/weather': {
    images: ['/images/12i.png', '/images/16.jpeg', '/images/18.jpeg'],
    overlay: 'from-blue-950/80 via-black/60 to-blue-950/80',
    accent: 'blue'
  },
  '/market-prices': {
    images: ['/images/10i.jpg', '/images/13.jpeg', '/images/17.jpeg'],
    overlay: 'from-amber-950/80 via-black/60 to-amber-950/80',
    accent: 'amber'
  },
  '/pest-detection': {
    images: ['/images/8i.jpg', '/images/11.jpeg', '/images/15.jpeg'],
    overlay: 'from-red-950/80 via-black/60 to-red-950/80',
    accent: 'red'
  },
  '/disease-knowledge': {
    images: ['/images/8i.jpg', '/images/16.jpeg', '/images/18.jpeg'],
    overlay: 'from-purple-950/80 via-black/60 to-purple-950/80',
    accent: 'purple'
  },
  '/community': {
    images: ['/images/10i.jpg', '/images/7i.jpg', '/images/1i.png'],
    overlay: 'from-cyan-950/80 via-black/60 to-cyan-950/80',
    accent: 'cyan'
  },
  '/schemes': {
    images: ['/images/9i.png', '/images/13.jpeg', '/images/17.jpeg'],
    overlay: 'from-indigo-950/80 via-black/60 to-indigo-950/80',
    accent: 'indigo'
  },
  '/calculators': {
    images: ['/images/12i.png', '/images/15.jpeg', '/images/7i.jpg'],
    overlay: 'from-teal-950/80 via-black/60 to-teal-950/80',
    accent: 'teal'
  },
  '/expert-contact': {
    images: ['/images/10i.jpg', '/images/1i.png', '/images/16.jpeg'],
    overlay: 'from-orange-950/80 via-black/60 to-orange-950/80',
    accent: 'orange'
  },
  '/profile': {
    images: ['/images/9i.png', '/images/18.jpeg', '/images/11.jpeg'],
    overlay: 'from-slate-950/80 via-black/60 to-slate-950/80',
    accent: 'slate'
  },
  '/auth': {
    images: ['/images/1i.png', '/images/7i.jpg', '/images/12i.png'],
    overlay: 'from-black/80 via-black/60 to-emerald-950/80',
    accent: 'emerald'
  }
};

const defaultConfig = {
  images: ['/images/1i.png', '/images/7i.jpg', '/images/9i.png'],
  overlay: 'from-black/70 via-black/50 to-black/70',
  accent: 'emerald'
};

const BackgroundContext = createContext();

export const useBackground = () => useContext(BackgroundContext);

export const BackgroundProvider = ({ children }) => {
  const location = useLocation();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);
  
  const config = pageBackgrounds[location.pathname] || defaultConfig;
  const images = config.images;
  
  // Change image every 8 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % images.length);
    }, 8000);
    
    return () => clearInterval(interval);
  }, [images.length, location.pathname]);
  
  // Reset index when page changes
  useEffect(() => {
    setCurrentImageIndex(0);
    setIsLoaded(false);
  }, [location.pathname]);

  return (
    <BackgroundContext.Provider value={{ config, currentImageIndex }}>
      <div className="fixed inset-0 z-0 overflow-hidden">
        {/* Background Images with Crossfade */}
        <AnimatePresence mode="sync">
          <motion.div
            key={`${location.pathname}-${currentImageIndex}`}
            initial={{ opacity: 0, scale: 1.1 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
            className="absolute inset-0"
          >
            <img
              src={images[currentImageIndex]}
              alt="Background"
              className="w-full h-full object-cover"
              onLoad={() => setIsLoaded(true)}
            />
          </motion.div>
        </AnimatePresence>
        
        {/* Gradient Overlay */}
        <div className={`absolute inset-0 bg-gradient-to-br ${config.overlay}`} />
        
        {/* Animated Particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-white/20 rounded-full"
              initial={{
                x: Math.random() * window.innerWidth,
                y: window.innerHeight + 10,
                opacity: 0
              }}
              animate={{
                y: -10,
                opacity: [0, 0.5, 0],
              }}
              transition={{
                duration: Math.random() * 10 + 10,
                repeat: Infinity,
                delay: Math.random() * 5,
                ease: "linear"
              }}
            />
          ))}
        </div>
        
        {/* Subtle Grain Texture */}
        <div 
          className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`
          }}
        />
        
        {/* Bottom Vignette */}
        <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/50 to-transparent" />
      </div>
      
      {/* Content Container */}
      <div className="relative z-10">
        {children}
      </div>
    </BackgroundContext.Provider>
  );
};

export default BackgroundProvider;
