import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Phone, Mail, MapPin, Video, Clock, Globe } from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const ExpertContact = () => {
  const contacts = [
    {
      category: 'Government Helpline',
      contacts: [
        {
          name: 'Kisan Call Centre',
          type: 'Toll-Free Helpline',
          phone: '1800-180-1551',
          availability: '24x7',
          description: 'Expert advice on crop cultivation, pest management, and farming practices',
          languages: ['Hindi', 'English', 'Regional'],
        },
        {
          name: 'PM-KISAN Helpdesk',
          type: 'Support',
          phone: '011-24300606',
          email: 'pmkisan-ict@gov.in',
          availability: 'Mon-Fri, 9 AM - 6 PM',
          description: 'Assistance with PM-KISAN scheme registration and queries',
          languages: ['Hindi', 'English'],
        },
      ],
    },
    {
      category: 'Agriculture Officers',
      contacts: [
        {
          name: 'District Agriculture Officer',
          type: 'Government Office',
          phone: '0120-XXXXXXX',
          email: 'dao@agriculture.gov.in',
          address: 'District Agriculture Office, Your District',
          availability: 'Mon-Fri, 10 AM - 5 PM',
          description: 'Technical guidance, soil testing, subsidy schemes',
          languages: ['Hindi', 'English', 'Local'],
        },
        {
          name: 'Block Development Officer',
          type: 'Government Office',
          phone: '0120-XXXXXXX',
          address: 'Block Office, Your Block',
          availability: 'Mon-Sat, 10 AM - 4 PM',
          description: 'Rural development schemes, farmer registration',
          languages: ['Hindi', 'Local'],
        },
      ],
    },
    {
      category: 'PM Kisan Sewa Kendra',
      contacts: [
        {
          name: 'Common Service Centre (CSC)',
          type: 'Service Center',
          phone: '1800-121-3468',
          email: 'helpdesk@csc.gov.in',
          website: 'https://www.csc.gov.in',
          availability: 'Mon-Sat, 9 AM - 6 PM',
          description: 'Digital services, scheme applications, documentation support',
          languages: ['Hindi', 'English', 'Regional'],
        },
      ],
    },
    {
      category: 'Admin Contact',
      contacts: [
        {
          name: 'Smart Agri Support',
          type: 'Platform Support',
          phone: '1800-XXX-XXXX',
          email: 'support@smartagri.in',
          availability: 'Mon-Fri, 9 AM - 7 PM',
          description: 'Technical support for app features and queries',
          languages: ['Hindi', 'English', 'Marathi'],
        },
      ],
    },
  ];

  const handleCall = (phone) => {
    toast.success(`Calling ${phone}`);
    window.location.href = `tel:${phone}`;
  };

  const handleEmail = (email) => {
    toast.success(`Opening email client`);
    window.location.href = `mailto:${email}`;
  };

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="bg-primary/10 p-3 rounded-2xl">
            <Phone className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Expert Contact</h1>
            <p className="text-muted-foreground">Get in touch with agricultural experts and support services</p>
          </div>
        </div>

        {/* Introductory Video */}
        <Card className="shadow-elegant border-border gradient-sky">
          <CardContent className="p-8 text-center">
            <div className="bg-card/80 backdrop-blur-sm p-12 rounded-2xl inline-block">
              <Video className="h-16 w-16 mx-auto mb-4 text-accent" />
              <h3 className="text-xl font-semibold text-foreground mb-2">How to Use Contact Services</h3>
              <p className="text-sm text-muted-foreground mb-4 max-w-md mx-auto">
                Watch this video to learn how to effectively reach out to agricultural experts and get the support you need.
              </p>
              <Button variant="outline" className="bg-card">
                <Video className="mr-2 h-4 w-4" />
                Watch Tutorial
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Contact Sections */}
        <div className="space-y-6">
          {contacts.map((section, sectionIndex) => (
            <div key={sectionIndex} className="space-y-4">
              <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                <div className="w-1 h-6 bg-primary rounded-full"></div>
                {section.category}
              </h2>
              
              <div className="grid gap-4">
                {section.contacts.map((contact, contactIndex) => (
                  <motion.div
                    key={contactIndex}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: (sectionIndex * 0.1) + (contactIndex * 0.05) }}
                  >
                    <Card className="shadow-elegant border-border hover:shadow-lg transition-all">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg">{contact.name}</CardTitle>
                            <Badge variant="outline" className="mt-2">
                              {contact.type}
                            </Badge>
                          </div>
                          {contact.availability && (
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <Clock className="h-4 w-4" />
                              <span>{contact.availability}</span>
                            </div>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <p className="text-sm text-muted-foreground leading-relaxed">
                          {contact.description}
                        </p>

                        {/* Contact Details */}
                        <div className="space-y-3">
                          {contact.phone && (
                            <div className="flex items-center gap-3">
                              <div className="bg-primary/10 p-2 rounded-lg">
                                <Phone className="h-4 w-4 text-primary" />
                              </div>
                              <div className="flex-1">
                                <p className="text-xs text-muted-foreground">Phone</p>
                                <p className="text-sm font-semibold text-foreground">{contact.phone}</p>
                              </div>
                              <Button
                                size="sm"
                                onClick={() => handleCall(contact.phone)}
                                className="gradient-primary"
                              >
                                Call Now
                              </Button>
                            </div>
                          )}

                          {contact.email && (
                            <div className="flex items-center gap-3">
                              <div className="bg-primary/10 p-2 rounded-lg">
                                <Mail className="h-4 w-4 text-primary" />
                              </div>
                              <div className="flex-1">
                                <p className="text-xs text-muted-foreground">Email</p>
                                <p className="text-sm font-semibold text-foreground">{contact.email}</p>
                              </div>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleEmail(contact.email)}
                              >
                                Send Email
                              </Button>
                            </div>
                          )}

                          {contact.address && (
                            <div className="flex items-start gap-3">
                              <div className="bg-primary/10 p-2 rounded-lg">
                                <MapPin className="h-4 w-4 text-primary" />
                              </div>
                              <div className="flex-1">
                                <p className="text-xs text-muted-foreground">Address</p>
                                <p className="text-sm font-semibold text-foreground">{contact.address}</p>
                              </div>
                            </div>
                          )}

                          {contact.website && (
                            <div className="flex items-center gap-3">
                              <div className="bg-primary/10 p-2 rounded-lg">
                                <Globe className="h-4 w-4 text-primary" />
                              </div>
                              <div className="flex-1">
                                <p className="text-xs text-muted-foreground">Website</p>
                                <p className="text-sm font-semibold text-foreground">{contact.website}</p>
                              </div>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => window.open(contact.website, '_blank')}
                              >
                                Visit
                              </Button>
                            </div>
                          )}
                        </div>

                        {/* Languages */}
                        {contact.languages && (
                          <div>
                            <p className="text-xs text-muted-foreground mb-2">Languages Available:</p>
                            <div className="flex flex-wrap gap-2">
                              {contact.languages.map((lang, idx) => (
                                <Badge key={idx} variant="secondary" className="text-xs">
                                  {lang}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Emergency Notice */}
        <Card className="shadow-elegant border-primary bg-gradient-earth">
          <CardContent className="p-6">
            <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
              <Phone className="h-5 w-5 text-primary" />
              Important Notice
            </h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>For emergency agricultural issues, contact Kisan Call Centre at 1800-180-1551 (available 24x7)</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>Keep your land records and Aadhaar card ready when contacting government offices</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>Visit CSC for document scanning and digital application submission</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default ExpertContact;
