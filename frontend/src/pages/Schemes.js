import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, ExternalLink, Bell, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import apiService from '@/services/api';

const Schemes = () => {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);

  // Default schemes data (fallback + enhancement from API)
  const defaultSchemes = [
    {
      title: 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
      category: 'Income Support',
      amount: '₹6,000/year',
      description: 'Direct income support of ₹2,000 per installment to all landholding farmer families.',
      eligibility: 'All landholding farmers',
      benefits: [
        'Three installments of ₹2,000 each',
        'Direct bank transfer',
        'No upper limit on land size',
      ],
      status: 'Active',
      isNew: false,
      link: 'https://pmkisan.gov.in/',
    },
    {
      title: 'Pradhan Mantri Fasal Bima Yojana',
      category: 'Crop Insurance',
      amount: 'Varies',
      description: 'Comprehensive crop insurance scheme covering pre-sowing to post-harvest losses.',
      eligibility: 'All farmers growing notified crops',
      benefits: [
        'Coverage for natural calamities',
        'Low premium rates',
        'Quick claim settlement',
      ],
      status: 'Active',
      isNew: false,
      link: 'https://pmfby.gov.in/',
    },
    {
      title: 'Kisan Credit Card (KCC)',
      category: 'Credit',
      amount: 'Up to ₹3 lakh',
      description: 'Provides adequate and timely credit support to farmers for cultivation and other needs.',
      eligibility: 'All farmers',
      benefits: [
        'Low interest rates (7% p.a.)',
        'Interest subvention of 3%',
        'Insurance coverage',
      ],
      status: 'Active',
      isNew: false,
      link: 'https://www.india.gov.in/',
    },
    {
      title: 'PM Kusum Yojana',
      category: 'Solar Energy',
      amount: 'Subsidy up to 60%',
      description: 'Solar pump installation scheme for farmers to reduce diesel dependency.',
      eligibility: 'Individual farmers, groups, cooperatives',
      benefits: [
        'Subsidy on solar pumps',
        'Extra income from selling power',
        'Environmental benefits',
      ],
      status: 'Active',
      isNew: true,
      link: 'https://mnre.gov.in/solar/schemes/',
    },
    {
      title: 'Pradhan Mantri Krishi Sinchayee Yojana',
      category: 'Irrigation',
      amount: 'Varies by component',
      description: 'Per Drop More Crop - promotes micro-irrigation for efficient water use.',
      eligibility: 'All farmers',
      benefits: [
        'Subsidy on drip irrigation',
        'Sprinkler system support',
        'Water conservation',
      ],
      status: 'Active',
      isNew: false,
      link: 'https://pmksy.gov.in/',
    },
    {
      title: 'National Mission on Sustainable Agriculture',
      category: 'Sustainability',
      amount: 'Component-based',
      description: 'Promotes sustainable farming practices and climate-resilient agriculture.',
      eligibility: 'All farmers',
      benefits: [
        'Soil health management',
        'Organic farming support',
        'Training programs',
      ],
      status: 'Active',
      isNew: false,
      link: 'https://nmsa.dac.gov.in/',
    },
  ];

  // Fetch schemes from API on mount
  useEffect(() => {
    const fetchSchemes = async () => {
      try {
        setLoading(true);
        const apiSchemes = await apiService.getSchemes();
        
        // Transform API schemes to match frontend format
        const transformedSchemes = apiSchemes.map((scheme, index) => ({
          title: scheme.scheme_name,
          category: 'Government Scheme',
          amount: 'Varies',
          description: scheme.description,
          eligibility: 'All eligible farmers',
          benefits: ['Check official website for details'],
          status: 'Active',
          isNew: index === 0,
          link: '#',
        }));
        
        // Combine API schemes with default schemes
        setSchemes([...transformedSchemes, ...defaultSchemes]);
      } catch (error) {
        console.error('Error fetching schemes:', error);
        // Use default schemes on error
        setSchemes(defaultSchemes);
      } finally {
        setLoading(false);
      }
    };

    // eslint-disable-next-line react-hooks/exhaustive-deps
    fetchSchemes();
  }, []);

  const categoryColors = {
    'Income Support': 'bg-green-500',
    'Crop Insurance': 'bg-blue-500',
    'Credit': 'bg-purple-500',
    'Solar Energy': 'bg-orange-500',
    'Irrigation': 'bg-cyan-500',
    'Sustainability': 'bg-emerald-500',
    'Government Scheme': 'bg-indigo-500',
  };

  const handleApply = (scheme) => {
    toast.success(`Redirecting to ${scheme.title} application portal`);
    // In production, this would navigate to the actual scheme website
  };

  const handleNotify = (scheme) => {
    toast.success(`You will be notified about updates for ${scheme.title}`);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading schemes...</span>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="bg-primary/10 p-3 rounded-2xl">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Government Schemes</h1>
            <p className="text-muted-foreground">Browse and apply for agricultural schemes and benefits</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid sm:grid-cols-3 gap-4">
          <Card className="shadow-elegant border-border">
            <CardContent className="p-6 text-center">
              <p className="text-3xl font-bold text-primary">{schemes.length}</p>
              <p className="text-sm text-muted-foreground mt-1">Total Schemes</p>
            </CardContent>
          </Card>
          <Card className="shadow-elegant border-border">
            <CardContent className="p-6 text-center">
              <p className="text-3xl font-bold text-green-600">{schemes.filter(s => s.status === 'Active').length}</p>
              <p className="text-sm text-muted-foreground mt-1">Active Schemes</p>
            </CardContent>
          </Card>
          <Card className="shadow-elegant border-border">
            <CardContent className="p-6 text-center">
              <p className="text-3xl font-bold text-orange-600">{schemes.filter(s => s.isNew).length}</p>
              <p className="text-sm text-muted-foreground mt-1">New Schemes</p>
            </CardContent>
          </Card>
        </div>

        {/* Schemes Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {schemes.map((scheme, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="shadow-elegant border-border hover:shadow-lg transition-all h-full flex flex-col">
                <CardHeader>
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <Badge className={categoryColors[scheme.category]}>
                        {scheme.category}
                      </Badge>
                      {scheme.isNew && (
                        <Badge variant="destructive" className="animate-pulse-soft">
                          NEW
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-lg leading-tight">{scheme.title}</CardTitle>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-primary">{scheme.amount}</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4 flex-1 flex flex-col">
                  <p className="text-sm text-muted-foreground leading-relaxed">{scheme.description}</p>

                  <div className="space-y-2">
                    <div className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <p className="text-xs text-muted-foreground">
                        <span className="font-medium text-foreground">Eligibility:</span> {scheme.eligibility}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-semibold text-foreground">Key Benefits:</p>
                    <ul className="space-y-1">
                      {scheme.benefits.map((benefit, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-xs text-muted-foreground">
                          <div className="w-1 h-1 bg-primary rounded-full mt-1.5 flex-shrink-0"></div>
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex items-center gap-2 pt-2 mt-auto">
                    {scheme.status === 'Active' ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-orange-600" />
                    )}
                    <span className="text-xs font-medium text-muted-foreground">{scheme.status}</span>
                  </div>

                  <div className="flex gap-2 mt-4">
                    <Button
                      onClick={() => handleApply(scheme)}
                      className="flex-1 gradient-primary"
                      size="sm"
                    >
                      <ExternalLink className="mr-2 h-3 w-3" />
                      Apply
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleNotify(scheme)}
                    >
                      <Bell className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Help Section */}
        <Card className="shadow-elegant border-border bg-gradient-earth">
          <CardContent className="p-6">
            <h3 className="font-semibold text-foreground mb-3">Need Help with Applications?</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Visit your nearest Common Service Centre (CSC) or contact the helpline numbers below:
            </p>
            <div className="grid sm:grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-primary rounded-full"></div>
                <span className="text-muted-foreground">
                  PM-KISAN Helpline: <span className="font-semibold text-foreground">011-24300606</span>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-primary rounded-full"></div>
                <span className="text-muted-foreground">
                  Kisan Call Centre: <span className="font-semibold text-foreground">1800-180-1551</span>
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Schemes;
