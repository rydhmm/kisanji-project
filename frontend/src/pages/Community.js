import { useState } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Users, Heart, MessageCircle, Share2, Send } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const Community = () => {
  const [newPost, setNewPost] = useState('');
  const [posts, setPosts] = useState([
    {
      id: 1,
      author: 'Ramesh Kumar',
      location: 'Punjab',
      time: '2 hours ago',
      content: 'Just harvested wheat this season. Got excellent yield of 48 quintals per hectare! Thanks to the weather advisory from this app.',
      likes: 45,
      comments: 12,
      liked: false,
    },
    {
      id: 2,
      author: 'Suresh Patil',
      location: 'Maharashtra',
      time: '5 hours ago',
      content: 'Anyone facing pest issues in tomato crops? I noticed white flies on my plants. Need suggestions for organic treatment.',
      likes: 28,
      comments: 18,
      liked: false,
    },
    {
      id: 3,
      author: 'Vijay Singh',
      location: 'Uttar Pradesh',
      time: '1 day ago',
      content: 'Market prices for rice are looking good this week. Sold my produce at ₹2,850 per quintal in Lucknow mandi.',
      likes: 67,
      comments: 24,
      liked: true,
    },
    {
      id: 4,
      author: 'Lakshmi Devi',
      location: 'Tamil Nadu',
      time: '1 day ago',
      content: 'Started using drip irrigation system recommended by agricultural officer. Seeing 30% water savings already!',
      likes: 89,
      comments: 31,
      liked: false,
    },
  ]);

  const handlePost = () => {
    if (newPost.trim()) {
      const post = {
        id: Date.now(),
        author: 'You',
        location: 'Your Location',
        time: 'Just now',
        content: newPost,
        likes: 0,
        comments: 0,
        liked: false,
      };
      setPosts([post, ...posts]);
      setNewPost('');
      toast.success('Post shared with community!');
    }
  };

  const handleLike = (postId) => {
    setPosts(posts.map(post => {
      if (post.id === postId) {
        return {
          ...post,
          liked: !post.liked,
          likes: post.liked ? post.likes - 1 : post.likes + 1,
        };
      }
      return post;
    }));
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="bg-primary/10 p-3 rounded-2xl">
            <Users className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Farmer Community</h1>
            <p className="text-muted-foreground">Connect, share, and learn from fellow farmers</p>
          </div>
        </div>

        {/* Create Post */}
        <Card className="shadow-elegant border-border">
          <CardContent className="p-6">
            <Textarea
              placeholder="Share your farming experience, tips, or ask questions..."
              className="min-h-24 mb-4"
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
            />
            <div className="flex justify-end">
              <Button onClick={handlePost} className="gradient-primary" disabled={!newPost.trim()}>
                <Send className="mr-2 h-4 w-4" />
                Share Post
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Community Feed */}
        <div className="space-y-4">
          {posts.map((post, index) => (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="shadow-elegant border-border hover:shadow-lg transition-all">
                <CardHeader className="pb-3">
                  <div className="flex items-start gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback className="bg-primary text-primary-foreground font-semibold">
                        {post.author.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-foreground">{post.author}</p>
                          <p className="text-xs text-muted-foreground">{post.location} • {post.time}</p>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          Verified Farmer
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-foreground leading-relaxed mb-4">{post.content}</p>
                  
                  <div className="flex items-center gap-4 pt-3 border-t border-border">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleLike(post.id)}
                      className={post.liked ? 'text-red-500' : 'text-muted-foreground'}
                    >
                      <Heart className={`mr-2 h-4 w-4 ${post.liked ? 'fill-current' : ''}`} />
                      {post.likes}
                    </Button>
                    <Button variant="ghost" size="sm" className="text-muted-foreground">
                      <MessageCircle className="mr-2 h-4 w-4" />
                      {post.comments}
                    </Button>
                    <Button variant="ghost" size="sm" className="text-muted-foreground ml-auto">
                      <Share2 className="mr-2 h-4 w-4" />
                      Share
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Community Guidelines */}
        <Card className="shadow-elegant border-border bg-gradient-earth">
          <CardContent className="p-6">
            <h3 className="font-semibold text-foreground mb-3">Community Guidelines</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>Be respectful and supportive to fellow farmers</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>Share genuine experiences and verified information</span>
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2"></div>
                <span>Avoid spam and promotional content</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Community;
