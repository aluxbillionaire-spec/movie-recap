import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

const UploadsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>File Uploads</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">File uploads page - Coming soon</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default UploadsPage;