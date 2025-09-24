import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { CheckCircle, AlertCircle, Activity, Globe, Users } from 'lucide-react';
import Button from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import LanguageSelector from '../components/ui/LanguageSelector';

interface TestResult {
  name: string;
  status: 'pass' | 'fail' | 'running';
  message: string;
  details?: any;
}

const TestPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [tests, setTests] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const runTests = async () => {
    setIsRunning(true);
    const testResults: TestResult[] = [];

    // Test 1: API Health Check
    testResults.push({
      name: 'API Health Check',
      status: 'running',
      message: 'Checking API health...'
    });
    setTests([...testResults]);

    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      testResults[testResults.length - 1] = {
        name: 'API Health Check',
        status: response.ok ? 'pass' : 'fail',
        message: response.ok ? 'API is healthy and responding' : 'API health check failed',
        details: data
      };
    } catch (error) {
      testResults[testResults.length - 1] = {
        name: 'API Health Check',
        status: 'fail',
        message: 'Failed to connect to API',
        details: error
      };
    }

    // Test 2: Multi-tenant Detection
    testResults.push({
      name: 'Multi-tenant Detection',
      status: 'running',
      message: 'Testing tenant detection...'
    });
    setTests([...testResults]);

    try {
      const response = await fetch('/api/v1/tenant-info', {
        headers: { 'X-Tenant-ID': 'customer1' }
      });
      const data = await response.json();
      testResults[testResults.length - 1] = {
        name: 'Multi-tenant Detection',
        status: data.detected_tenant === 'customer1' ? 'pass' : 'fail',
        message: data.detected_tenant === 'customer1' 
          ? 'Tenant detection working correctly' 
          : 'Tenant detection failed',
        details: data
      };
    } catch (error) {
      testResults[testResults.length - 1] = {
        name: 'Multi-tenant Detection',
        status: 'fail',
        message: 'Failed to test tenant detection',
        details: error
      };
    }

    // Test 3: Internationalization
    testResults.push({
      name: 'Internationalization (i18n)',
      status: 'running',
      message: 'Testing i18n functionality...'
    });
    setTests([...testResults]);

    try {
      const response = await fetch('/api/v1/i18n/test');
      const data = await response.json();
      testResults[testResults.length - 1] = {
        name: 'Internationalization (i18n)',
        status: data.supported_languages && data.supported_languages.length > 0 ? 'pass' : 'fail',
        message: data.supported_languages 
          ? `i18n working with ${data.supported_languages.length} languages` 
          : 'i18n test failed',
        details: data
      };
    } catch (error) {
      testResults[testResults.length - 1] = {
        name: 'Internationalization (i18n)',
        status: 'fail',
        message: 'Failed to test i18n',
        details: error
      };
    }

    // Test 4: Analytics Endpoints
    testResults.push({
      name: 'Analytics Endpoints',
      status: 'running',
      message: 'Testing analytics endpoints...'
    });
    setTests([...testResults]);

    try {
      const response = await fetch('/api/v1/analytics/global/metrics');
      const data = await response.json();
      testResults[testResults.length - 1] = {
        name: 'Analytics Endpoints',
        status: data.total_tenants !== undefined ? 'pass' : 'fail',
        message: data.total_tenants !== undefined 
          ? 'Analytics endpoints working correctly' 
          : 'Analytics endpoints failed',
        details: data
      };
    } catch (error) {
      testResults[testResults.length - 1] = {
        name: 'Analytics Endpoints',
        status: 'fail',
        message: 'Failed to test analytics endpoints',
        details: error
      };
    }

    // Test 5: Tenant-specific Metrics
    testResults.push({
      name: 'Tenant-specific Metrics',
      status: 'running',
      message: 'Testing tenant-specific metrics...'
    });
    setTests([...testResults]);

    try {
      const response = await fetch('/api/v1/tenants/customer1/metrics');
      const data = await response.json();
      testResults[testResults.length - 1] = {
        name: 'Tenant-specific Metrics',
        status: data.tenant_id === 'customer1' ? 'pass' : 'fail',
        message: data.tenant_id === 'customer1' 
          ? 'Tenant-specific metrics working correctly' 
          : 'Tenant-specific metrics failed',
        details: data
      };
    } catch (error) {
      testResults[testResults.length - 1] = {
        name: 'Tenant-specific Metrics',
        status: 'fail',
        message: 'Failed to test tenant-specific metrics',
        details: error
      };
    }

    setTests(testResults);
    setIsRunning(false);
  };

  useEffect(() => {
    runTests();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'fail':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-yellow-500 animate-spin" />;
    }
  };

  const passedTests = tests.filter(t => t.status === 'pass').length;
  const totalTests = tests.length;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {t('app.name')} - Global Deployment Test Suite
            </h1>
            <p className="text-gray-600 mt-2">
              Testing multi-tenant, i18n, security, and analytics functionality
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <LanguageSelector />
            <Button onClick={runTests} disabled={isRunning}>
              {isRunning ? 'Running Tests...' : 'Run Tests Again'}
            </Button>
          </div>
        </div>

        {/* Test Results Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Test Results Summary</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{totalTests}</div>
                <div className="text-sm text-blue-800">Total Tests</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{passedTests}</div>
                <div className="text-sm text-green-800">Passed</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{totalTests - passedTests}</div>
                <div className="text-sm text-red-800">Failed</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0}%
                </div>
                <div className="text-sm text-purple-800">Success Rate</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Individual Test Results */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {tests.map((test, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  {getStatusIcon(test.status)}
                  <span>{test.name}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className={`mb-3 ${
                  test.status === 'pass' ? 'text-green-700' : 
                  test.status === 'fail' ? 'text-red-700' : 'text-yellow-700'
                }`}>
                  {test.message}
                </p>
                {test.details && (
                  <details className="mt-3">
                    <summary className="cursor-pointer text-sm font-medium text-gray-600">
                      View Details
                    </summary>
                    <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-x-auto">
                      {JSON.stringify(test.details, null, 2)}
                    </pre>
                  </details>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Language Test Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="w-5 h-5" />
              <span>Language Test</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { code: 'en', name: 'English' },
                { code: 'es', name: 'Español' },
                { code: 'fr', name: 'Français' },
                { code: 'de', name: 'Deutsch' },
                { code: 'zh', name: '中文' },
                { code: 'ar', name: 'العربية' }
              ].map((lang) => (
                <Button
                  key={lang.code}
                  variant={i18n.language === lang.code ? 'primary' : 'outline'}
                  onClick={() => i18n.changeLanguage(lang.code)}
                  className="text-sm"
                >
                  {lang.name}
                </Button>
              ))}
            </div>
            <div className="mt-4 p-4 bg-gray-50 rounded">
              <h3 className="font-medium mb-2">Current Language Test:</h3>
              <p><strong>Welcome:</strong> {t('app.welcome')}</p>
              <p><strong>Dashboard:</strong> {t('navigation.dashboard')}</p>
              <p><strong>Projects:</strong> {t('navigation.projects')}</p>
              <p><strong>Settings:</strong> {t('navigation.settings')}</p>
            </div>
          </CardContent>
        </Card>

        {/* Tenant Test Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="w-5 h-5" />
              <span>Multi-Tenant Test</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Test different tenant contexts by changing the X-Tenant-ID header.
            </p>
            <div className="space-y-2">
              <Button
                onClick={() => {
                  fetch('/api/v1/tenant-info', {
                    headers: { 'X-Tenant-ID': 'default' }
                  })
                  .then(r => r.json())
                  .then(data => alert(JSON.stringify(data, null, 2)));
                }}
                variant="outline"
              >
                Test Default Tenant
              </Button>
              <Button
                onClick={() => {
                  fetch('/api/v1/tenant-info', {
                    headers: { 'X-Tenant-ID': 'customer1' }
                  })
                  .then(r => r.json())
                  .then(data => alert(JSON.stringify(data, null, 2)));
                }}
                variant="outline"
              >
                Test Customer1 Tenant
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TestPage;