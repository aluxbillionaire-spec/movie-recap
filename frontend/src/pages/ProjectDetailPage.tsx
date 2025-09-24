import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

const ProjectDetailPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">Project detail page - Coming soon</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProjectDetailPage;