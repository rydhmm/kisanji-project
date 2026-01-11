import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

// Glassmorphism Card with animated border
export const GlassCard = ({ 
  children, 
  className, 
  hover = true,
  glow = false,
  variant = 'default',
  ...props 
}) => {
  const variants = {
    default: 'bg-black/40 border-white/10',
    emerald: 'bg-emerald-950/40 border-emerald-500/20',
    blue: 'bg-blue-950/40 border-blue-500/20',
    amber: 'bg-amber-950/40 border-amber-500/20',
    red: 'bg-red-950/40 border-red-500/20',
    purple: 'bg-purple-950/40 border-purple-500/20',
  };

  const glowColors = {
    default: 'shadow-white/5',
    emerald: 'shadow-emerald-500/20',
    blue: 'shadow-blue-500/20',
    amber: 'shadow-amber-500/20',
    red: 'shadow-red-500/20',
    purple: 'shadow-purple-500/20',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={hover ? { scale: 1.02, y: -5 } : {}}
      className={cn(
        'relative rounded-2xl border backdrop-blur-xl overflow-hidden',
        'transition-all duration-500',
        variants[variant],
        glow && `shadow-2xl ${glowColors[variant]}`,
        hover && 'hover:border-white/20 hover:shadow-xl',
        className
      )}
      {...props}
    >
      {/* Animated gradient border effect */}
      <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500">
        <div className="absolute inset-[-2px] bg-gradient-to-r from-emerald-500/20 via-blue-500/20 to-purple-500/20 rounded-2xl blur-sm" />
      </div>
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
};

// Animated stat card with icon
export const StatCard = ({ 
  icon: Icon, 
  label, 
  value, 
  change, 
  changeType = 'neutral',
  variant = 'default' 
}) => {
  const changeColors = {
    positive: 'text-emerald-400 bg-emerald-500/20',
    negative: 'text-red-400 bg-red-500/20',
    neutral: 'text-gray-400 bg-gray-500/20'
  };

  return (
    <GlassCard variant={variant} className="p-6">
      <div className="flex items-start justify-between">
        <div className="p-3 rounded-xl bg-white/10">
          <Icon className="w-6 h-6 text-white" />
        </div>
        {change && (
          <span className={cn(
            'text-xs font-medium px-2 py-1 rounded-full',
            changeColors[changeType]
          )}>
            {change}
          </span>
        )}
      </div>
      <div className="mt-4">
        <motion.h3 
          className="text-3xl font-bold text-white"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
        >
          {value}
        </motion.h3>
        <p className="text-sm text-gray-400 mt-1">{label}</p>
      </div>
    </GlassCard>
  );
};

// Animated section header
export const SectionHeader = ({ 
  icon: Icon, 
  title, 
  subtitle,
  action 
}) => (
  <motion.div 
    className="flex items-center justify-between mb-6"
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ duration: 0.5 }}
  >
    <div className="flex items-center gap-3">
      {Icon && (
        <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500/20 to-blue-500/20 border border-white/10">
          <Icon className="w-5 h-5 text-white" />
        </div>
      )}
      <div>
        <h2 className="text-xl font-bold text-white">{title}</h2>
        {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
      </div>
    </div>
    {action}
  </motion.div>
);

// Animated page title
export const PageTitle = ({ 
  icon: Icon, 
  title, 
  description,
  badge
}) => (
  <motion.div 
    className="mb-8"
    initial={{ opacity: 0, y: -30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, type: 'spring' }}
  >
    <div className="flex items-center gap-4 mb-2">
      {Icon && (
        <motion.div 
          className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500/30 to-emerald-600/30 border border-emerald-500/30 shadow-lg shadow-emerald-500/20"
          whileHover={{ rotate: 10, scale: 1.1 }}
          transition={{ type: 'spring', stiffness: 300 }}
        >
          <Icon className="w-8 h-8 text-emerald-400" />
        </motion.div>
      )}
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl md:text-4xl font-bold text-white drop-shadow-lg">
            {title}
          </h1>
          {badge && (
            <span className="px-3 py-1 text-xs font-medium bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30">
              {badge}
            </span>
          )}
        </div>
        {description && (
          <p className="text-gray-400 mt-1 text-lg">{description}</p>
        )}
      </div>
    </div>
  </motion.div>
);

// Animated loading spinner
export const LoadingSpinner = ({ size = 'md', className }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <motion.div
        className={cn(
          'border-2 border-white/20 border-t-emerald-500 rounded-full',
          sizes[size]
        )}
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  );
};

// Animated button with glow effect
export const GlowButton = ({ 
  children, 
  className, 
  variant = 'primary',
  size = 'md',
  ...props 
}) => {
  const variants = {
    primary: 'from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 shadow-emerald-500/30',
    secondary: 'from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700 shadow-gray-500/20',
    danger: 'from-red-500 to-red-600 hover:from-red-400 hover:to-red-500 shadow-red-500/30',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={cn(
        'relative font-semibold rounded-xl text-white shadow-lg',
        'bg-gradient-to-r transition-all duration-300',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      <span className="relative z-10">{children}</span>
    </motion.button>
  );
};

// Floating animation wrapper
export const FloatingElement = ({ children, delay = 0 }) => (
  <motion.div
    animate={{ y: [0, -10, 0] }}
    transition={{
      duration: 3,
      repeat: Infinity,
      delay,
      ease: 'easeInOut'
    }}
  >
    {children}
  </motion.div>
);

// Staggered list container
export const StaggeredList = ({ children, className }) => (
  <motion.div
    className={className}
    initial="hidden"
    animate="visible"
    variants={{
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          staggerChildren: 0.1
        }
      }
    }}
  >
    {children}
  </motion.div>
);

// Staggered list item
export const StaggeredItem = ({ children, className }) => (
  <motion.div
    className={className}
    variants={{
      hidden: { opacity: 0, y: 20 },
      visible: { opacity: 1, y: 0 }
    }}
  >
    {children}
  </motion.div>
);

export default GlassCard;
