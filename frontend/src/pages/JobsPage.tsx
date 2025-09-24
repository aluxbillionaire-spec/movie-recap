import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

const JobsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Processing Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">Jobs monitoring page - Coming soon</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default JobsPage;