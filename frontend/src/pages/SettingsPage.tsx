import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">Settings page - Coming soon</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsPage;