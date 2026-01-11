import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { User, MapPin, Phone, Mail, Globe, Volume2, History, Settings } from 'lucide-react';
import { toast } from 'sonner';

const Profile = () => {
  const { user, updateUser } = useAuth();
  const { t, language, changeLanguage, availableLanguages } = useLanguage();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    phone: user?.phone || '',
    email: user?.email || '',
    village: user?.village || '',
  });
  const [voiceEnabled, setVoiceEnabled] = useState(user?.voiceEnabled || false);

  const handleSave = () => {
    updateUser({ ...formData, voiceEnabled });
    setEditing(false);
    toast.success('Profile updated successfully!');
  };

  const diseaseHistory = [
    { date: 'Jan 15, 2025', crop: 'Wheat', disease: 'Leaf Rust', severity: 'Moderate' },
    { date: 'Dec 28, 2024', crop: 'Rice', disease: 'Blast', severity: 'Mild' },
    { date: 'Dec 10, 2024', crop: 'Tomato', disease: 'Early Blight', severity: 'Severe' },
  ];

  const advisoryHistory = [
    { date: 'Jan 18, 2025', type: 'Crop Recommendation', result: 'Wheat - 92% match' },
    { date: 'Jan 10, 2025', type: 'Weather Advisory', result: 'Good spraying conditions' },
    { date: 'Jan 5, 2025', type: 'Market Price', result: 'Best price: ₹2,150/quintal' },
  ];

  const languageNames = {
    en: 'English',
    hi: 'हिंदी',
    mr: 'मराठी',
  };

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="bg-primary/10 p-3 rounded-2xl">
            <User className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">My Profile</h1>
            <p className="text-muted-foreground">Manage your account and preferences</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="shadow-elegant border-border">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Profile Information</CardTitle>
                <Button
                  variant={editing ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => (editing ? handleSave() : setEditing(true))}
                >
                  {editing ? 'Save' : 'Edit'}
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">
                    <User className="inline h-4 w-4 mr-2" />
                    Full Name
                  </Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    disabled={!editing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">
                    <Phone className="inline h-4 w-4 mr-2" />
                    Phone Number
                  </Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    disabled={!editing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">
                    <Mail className="inline h-4 w-4 mr-2" />
                    Email (Optional)
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    disabled={!editing}
                    placeholder="your@email.com"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="village">
                    <MapPin className="inline h-4 w-4 mr-2" />
                    Village/Location
                  </Label>
                  <Input
                    id="village"
                    value={formData.village}
                    onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                    disabled={!editing}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Disease History */}
            <Card className="shadow-elegant border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History className="h-5 w-5" />
                  Disease Detection History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {diseaseHistory.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <div>
                        <p className="font-medium text-foreground">{item.disease}</p>
                        <p className="text-xs text-muted-foreground">
                          {item.crop} • {item.date}
                        </p>
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded-full ${
                          item.severity === 'Severe'
                            ? 'bg-red-100 text-red-700'
                            : item.severity === 'Moderate'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-green-100 text-green-700'
                        }`}
                      >
                        {item.severity}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Advisory History */}
            <Card className="shadow-elegant border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History className="h-5 w-5" />
                  Advisory History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {advisoryHistory.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <div>
                        <p className="font-medium text-foreground">{item.type}</p>
                        <p className="text-xs text-muted-foreground">{item.date}</p>
                      </div>
                      <p className="text-sm text-muted-foreground">{item.result}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Settings & Preferences */}
          <div className="space-y-6">
            <Card className="shadow-elegant border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Preferences
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Language */}
                <div className="space-y-3">
                  <Label>
                    <Globe className="inline h-4 w-4 mr-2" />
                    Language
                  </Label>
                  <div className="space-y-2">
                    {availableLanguages.map((lang) => (
                      <Button
                        key={lang}
                        variant={language === lang ? 'default' : 'outline'}
                        className="w-full"
                        onClick={() => {
                          changeLanguage(lang);
                          toast.success(`Language changed to ${languageNames[lang]}`);
                        }}
                      >
                        {languageNames[lang]}
                      </Button>
                    ))}
                  </div>
                </div>

                <Separator />

                {/* Voice Settings */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <Label className="flex items-center gap-2">
                        <Volume2 className="h-4 w-4" />
                        Voice Assistant
                      </Label>
                      <p className="text-xs text-muted-foreground">Enable voice input/output</p>
                    </div>
                    <Switch
                      checked={voiceEnabled}
                      onCheckedChange={(checked) => {
                        setVoiceEnabled(checked);
                        updateUser({ voiceEnabled: checked });
                        toast.success(
                          checked ? 'Voice assistant enabled' : 'Voice assistant disabled'
                        );
                      }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stats Card */}
            <Card className="shadow-elegant border-border gradient-primary text-primary-foreground">
              <CardContent className="p-6">
                <h3 className="font-semibold mb-4">Your Activity</h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-3xl font-bold">15</p>
                    <p className="text-sm opacity-90">Crop Recommendations</p>
                  </div>
                  <div>
                    <p className="text-3xl font-bold">8</p>
                    <p className="text-sm opacity-90">Disease Detections</p>
                  </div>
                  <div>
                    <p className="text-3xl font-bold">23</p>
                    <p className="text-sm opacity-90">Community Posts</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Profile;
