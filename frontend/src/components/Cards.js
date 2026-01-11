import { Card, CardContent } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

export const FeatureCard = ({ icon: Icon, title, description, onClick, gradient = false }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.03, y: -8 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.3, type: 'spring' }}
    >
      <Card
        className={`cursor-pointer glass-card border-white/10 hover:border-emerald-500/30 transition-all duration-300 group overflow-hidden ${
          gradient ? 'bg-gradient-to-br from-emerald-600/30 to-cyan-600/30' : ''
        }`}
        onClick={onClick}
      >
        <CardContent className="p-6 relative">
          {/* Hover glow effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/0 to-cyan-500/0 group-hover:from-emerald-500/10 group-hover:to-cyan-500/10 transition-all duration-300" />
          
          <div className="flex items-start gap-4 relative z-10">
            <motion.div
              className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 border border-emerald-500/20 group-hover:shadow-lg group-hover:shadow-emerald-500/20 transition-all"
              whileHover={{ rotate: 5 }}
            >
              <Icon className="h-6 w-6 text-emerald-400" />
            </motion.div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg mb-2 text-white group-hover:text-emerald-300 transition-colors">{title}</h3>
              <p className="text-sm leading-relaxed text-gray-400 group-hover:text-gray-300 transition-colors">
                {description}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export const WeatherCard = ({ day, temp, condition, icon: Icon }) => {
  return (
    <motion.div whileHover={{ y: -5 }} transition={{ duration: 0.2 }}>
      <Card className="glass border-white/10 hover:border-blue-500/30 transition-all">
        <CardContent className="p-4 text-center">
          <p className="text-sm font-medium text-gray-400 mb-2">{day}</p>
          <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 p-3 rounded-xl inline-block mb-2">
            <Icon className="h-7 w-7 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-white mb-1">{temp}°C</p>
          <p className="text-xs text-gray-500">{condition}</p>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export const QuickToolCard = ({ icon: Icon, label, onClick }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -5 }}
      whileTap={{ scale: 0.95 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className="cursor-pointer glass-card border-white/10 hover:border-teal-500/30 transition-all group"
        onClick={onClick}
      >
        <CardContent className="p-6 text-center">
          <div className="bg-gradient-to-br from-teal-500/20 to-cyan-500/20 p-4 rounded-2xl inline-block mb-3 group-hover:shadow-lg group-hover:shadow-teal-500/20 transition-all">
            <Icon className="h-7 w-7 text-teal-400" />
          </div>
          <p className="font-medium text-sm text-white group-hover:text-teal-300 transition-colors">{label}</p>
        </CardContent>
      </Card>
    </motion.div>
  );
};
