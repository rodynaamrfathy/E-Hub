import { useState } from 'react';
import { BarChart3, TrendingUp, Target, Award, Leaf, Zap, Droplets, Car, Home, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

export function SustainabilityDashboard() {
  const [selectedPeriod, setSelectedPeriod] = useState('month');

  const carbonData = {
    current: 2.4, // tons CO2 this month
    target: 3.0,
    lastMonth: 2.8,
    yearGoal: 30,
    yearProgress: 18.5
  };

  const achievements = [
    { id: 1, name: 'Plastic-Free Week', icon: '🌊', completed: true, points: 100 },
    { id: 2, name: 'Energy Saver', icon: '⚡', completed: true, points: 75 },
    { id: 3, name: 'Green Commuter', icon: '🚲', completed: false, points: 150 },
    { id: 4, name: 'Zero Waste Day', icon: '♻️', completed: true, points: 125 },
  ];

  const activities = [
    { date: 'Today', action: 'Used reusable water bottle', points: 10, category: 'waste' },
    { date: 'Yesterday', action: 'Biked to work (5 miles)', points: 25, category: 'transport' },
    { date: '2 days ago', action: 'Bought organic groceries', points: 15, category: 'consumption' },
    { date: '3 days ago', action: 'Installed LED bulbs', points: 30, category: 'energy' },
  ];

  const weeklyGoals = [
    { name: 'Reduce plastic use', progress: 80, target: '5 plastic-free days' },
    { name: 'Energy conservation', progress: 65, target: 'Save 15% electricity' },
    { name: 'Sustainable transport', progress: 40, target: '3 eco-friendly trips' },
    { name: 'Waste reduction', progress: 90, target: 'Recycle 90% of waste' },
  ];

  const stats = [
    {
      title: 'Carbon Footprint',
      value: `${carbonData.current} tons`,
      change: `-14% vs last month`,
      positive: true,
      icon: Leaf,
      color: 'text-green-600'
    },
    {
      title: 'Energy Saved',
      value: '127 kWh',
      change: '+23% this month',
      positive: true,
      icon: Zap,
      color: 'text-yellow-600'
    },
    {
      title: 'Water Conserved',
      value: '450L',
      change: '+18% this month',
      positive: true,
      icon: Droplets,
      color: 'text-blue-600'
    },
    {
      title: 'Eco Points',
      value: '1,247',
      change: '+156 this week',
      positive: true,
      icon: Award,
      color: 'text-purple-600'
    },
  ];

  const totalPoints = achievements.filter(a => a.completed).reduce((sum, a) => sum + a.points, 0) + 
                     activities.reduce((sum, a) => sum + a.points, 0);

  const level = Math.floor(totalPoints / 500) + 1;
  const pointsToNextLevel = (level * 500) - totalPoints;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Sustainability Dashboard</h1>
        <p className="text-gray-600">Track your environmental impact and progress</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className={`w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                </div>
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-600">{stat.title}</h3>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                  <p className={`text-sm mt-1 ${stat.positive ? 'text-green-600' : 'text-red-600'}`}>
                    {stat.change}
                  </p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-8">
          {/* Carbon Footprint Progress */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Leaf className="w-5 h-5 text-green-600" />
                <span>Carbon Footprint Goal</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Monthly Target: {carbonData.target} tons CO2</span>
                  <Badge variant={carbonData.current < carbonData.target ? "default" : "destructive"}>
                    {carbonData.current < carbonData.target ? 'On Track' : 'Over Target'}
                  </Badge>
                </div>
                <Progress 
                  value={(carbonData.current / carbonData.target) * 100} 
                  className="h-3"
                />
                <div className="flex justify-between text-sm">
                  <span className="text-green-600">Current: {carbonData.current} tons</span>
                  <span className="text-gray-500">Target: {carbonData.target} tons</span>
                </div>
                
                <div className="mt-6 pt-4 border-t">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Yearly Goal Progress</span>
                    <span className="text-sm">{carbonData.yearProgress}/{carbonData.yearGoal} tons</span>
                  </div>
                  <Progress 
                    value={(carbonData.yearProgress / carbonData.yearGoal) * 100} 
                    className="h-2"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Weekly Goals */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="w-5 h-5 text-blue-600" />
                <span>Weekly Goals</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {weeklyGoals.map((goal, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{goal.name}</span>
                      <span className="text-sm text-gray-600">{goal.progress}%</span>
                    </div>
                    <Progress value={goal.progress} className="h-2" />
                    <p className="text-xs text-gray-500">{goal.target}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activities */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                <span>Recent Activities</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activities.map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{activity.action}</p>
                      <p className="text-xs text-gray-500">{activity.date}</p>
                    </div>
                    <Badge variant="secondary" className="ml-2">
                      +{activity.points} pts
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-8">
          {/* Gamification Level */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Award className="w-5 h-5 text-yellow-600" />
                <span>Eco Level</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center space-y-4">
                <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto">
                  <span className="text-2xl font-bold text-white">{level}</span>
                </div>
                <div>
                  <h3 className="font-bold">Eco Warrior Level {level}</h3>
                  <p className="text-sm text-gray-600">{totalPoints} total points</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Next Level</span>
                    <span>{pointsToNextLevel} pts to go</span>
                  </div>
                  <Progress value={((totalPoints % 500) / 500) * 100} />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Achievements */}
          <Card>
            <CardHeader>
              <CardTitle>Achievements</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {achievements.map((achievement) => (
                  <div 
                    key={achievement.id}
                    className={`flex items-center space-x-3 p-3 rounded-lg border ${
                      achievement.completed ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <span className="text-xl">{achievement.icon}</span>
                    <div className="flex-1">
                      <p className={`font-medium ${achievement.completed ? 'text-green-800' : 'text-gray-600'}`}>
                        {achievement.name}
                      </p>
                      <p className="text-xs text-gray-500">{achievement.points} points</p>
                    </div>
                    {achievement.completed && (
                      <Badge variant="default" className="bg-green-600">
                        ✓
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Button className="w-full justify-start" variant="outline">
                  <Calendar className="w-4 h-4 mr-2" />
                  Log Today's Activities
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <TrendingUp className="w-4 h-4 mr-2" />
                  View Detailed Report
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Target className="w-4 h-4 mr-2" />
                  Set New Goal
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}