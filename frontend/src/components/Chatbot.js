import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageCircle, Send, Mic, X, Volume2, Loader2, MicOff } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/services/api';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am Kisan.JI AI Assistant powered by Gemini. Ask me anything about farming, crops, weather, or government schemes!',
    },
  ]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const { language } = useLanguage();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Text-based chat using Gemini API
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      const result = await api.voiceChat(
        currentInput,
        language || 'en',
        localStorage.getItem('userId')
      );

      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: result.response,
        language: result.language
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      // Fallback responses when API fails
      const fallbackResponses = [
        'Based on your location, I recommend planting wheat this season for optimal yield.',
        'The weather forecast shows good conditions for spraying in the next 2 days.',
        'Current market prices in your nearest mandi show rice at ₹2,100 per quintal.',
        'For pest control, I suggest using neem-based organic pesticides.',
        'You may be eligible for the PM-KISAN scheme. Visit your nearest CSC for registration.',
      ];
      const randomResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
      setMessages((prev) => [...prev, { role: 'assistant', content: randomResponse }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Start voice recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processVoiceInput(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsListening(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  // Stop voice recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsListening(false);
    }
  };

  // Process recorded audio with backend
  const processVoiceInput = async (audioBlob) => {
    setIsProcessing(true);
    
    try {
      // First transcribe using API service
      const transcribeResult = await api.transcribeAudio(
        audioBlob, 
        localStorage.getItem('userId')
      );

      if (transcribeResult.success && transcribeResult.text) {
        const transcribedText = transcribeResult.text;
        const detectedLang = transcribeResult.language || language;
        
        // Add user message
        setMessages((prev) => [...prev, { 
          role: 'user', 
          content: transcribedText,
          isVoice: true,
          language: detectedLang
        }]);

        // Get AI response
        const chatResult = await api.voiceChat(
          transcribedText,
          detectedLang,
          localStorage.getItem('userId')
        );

        setMessages((prev) => [...prev, { 
          role: 'assistant', 
          content: chatResult.response,
          language: chatResult.language
        }]);
      }
    } catch (error) {
      console.error('Voice processing error:', error);
      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I had trouble understanding. Please try speaking again or type your question.'
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  // Toggle voice recording
  const handleVoiceInput = () => {
    if (isListening) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // Text-to-speech for responses
  const speakResponse = (text, lang) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Map language codes to speech synthesis language
      const langMap = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'mr': 'mr-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'bn': 'bn-IN',
        'gu': 'gu-IN',
        'kn': 'kn-IN',
        'ml': 'ml-IN',
        'pa': 'pa-IN'
      };
      
      utterance.lang = langMap[lang] || langMap[language] || 'en-US';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <Button
              onClick={() => setIsOpen(true)}
              size="lg"
              className="gradient-primary h-14 w-14 rounded-full shadow-glow hover:shadow-lg transition-all"
            >
              <MessageCircle className="h-6 w-6" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-6 right-6 z-50 w-full max-w-md"
          >
            <Card className="shadow-2xl border-border overflow-hidden">
              {/* Header */}
              <div className="gradient-primary p-4 text-primary-foreground">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="bg-white/20 p-2 rounded-lg">
                      <MessageCircle className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold">AI Assistant</h3>
                      <p className="text-xs opacity-90">Always here to help</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setIsOpen(false)}
                    className="text-primary-foreground hover:bg-white/20"
                  >
                    <X className="h-5 w-5" />
                  </Button>
                </div>
              </div>

              {/* Messages */}
              <ScrollArea className="h-96 p-4 bg-background">
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-foreground'
                        }`}
                      >
                        {message.isVoice && (
                          <div className="flex items-center gap-1 text-xs opacity-70 mb-1">
                            <Mic className="h-3 w-3" />
                            <span>Voice message</span>
                          </div>
                        )}
                        <p className="text-sm leading-relaxed">{message.content}</p>
                        {message.role === 'assistant' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="mt-2 h-6 px-2 text-xs"
                            onClick={() => speakResponse(message.content, message.language)}
                          >
                            <Volume2 className="h-3 w-3 mr-1" />
                            Listen
                          </Button>
                        )}
                      </div>
                    </motion.div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              {/* Input */}
              <div className="p-4 bg-card border-t border-border">
                {/* Recording/Processing indicator */}
                {(isListening || isProcessing) && (
                  <div className="mb-3 flex items-center justify-center gap-2 text-sm">
                    {isListening && (
                      <>
                        <span className="relative flex h-3 w-3">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                        </span>
                        <span className="text-red-500 font-medium">Listening... Click mic to stop</span>
                      </>
                    )}
                    {isProcessing && (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin text-primary" />
                        <span className="text-primary">Processing voice...</span>
                      </>
                    )}
                  </div>
                )}
                
                <div className="flex items-center gap-2">
                  <Button
                    variant={isListening ? 'destructive' : 'outline'}
                    size="icon"
                    onClick={handleVoiceInput}
                    disabled={isProcessing}
                    className={isListening ? 'animate-pulse' : ''}
                    title={isListening ? 'Stop recording' : 'Start voice input'}
                  >
                    {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  </Button>
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder={isListening ? 'Listening...' : 'Type your question...'}
                    className="flex-1"
                    disabled={isListening || isProcessing}
                  />
                  <Button
                    onClick={handleSend}
                    size="icon"
                    className="gradient-primary"
                    disabled={!input.trim() || isLoading || isListening || isProcessing}
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Chatbot;
