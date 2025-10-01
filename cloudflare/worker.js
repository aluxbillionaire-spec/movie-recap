/**
 * Movie Recap Service - Cloudflare Worker
 * Handles dynamic API endpoints for the static frontend
 */

// Simple in-memory cache for demo purposes
const cache = new Map();

// Worker environment variables (set in Cloudflare dashboard)
const DEFAULT_BACKEND_URL = 'https://api.movierecap.com'; // Replace with your actual backend

/**
 * Main Worker request handler
 */
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  // CORS headers for all responses
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Tenant-ID',
    'Access-Control-Max-Age': '86400',
  };

  // Handle CORS preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, { 
      status: 200, 
      headers: corsHeaders 
    });
  }

  try {
    // Route API requests
    if (path.startsWith('/api/')) {
      return await handleApiRequest(request, corsHeaders);
    }

    // Health check endpoint
    if (path === '/health') {
      return new Response(JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        worker: 'movie-recap-worker',
        version: '1.0.0'
      }), {
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }

    // Default response for non-API requests
    return new Response('Movie Recap Worker is running', {
      headers: corsHeaders
    });

  } catch (error) {
    return new Response(JSON.stringify({
      error: 'Internal Server Error',
      message: error.message,
      timestamp: new Date().toISOString()
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
}

/**
 * Handle API requests
 */
async function handleApiRequest(request, corsHeaders) {
  const url = new URL(request.url);
  const path = url.pathname;

  // Example: Mock tenant info endpoint
  if (path === '/api/v1/tenant-info') {
    return await handleTenantInfo(request, corsHeaders);
  }

  // Example: Mock analytics endpoint
  if (path === '/api/v1/analytics/global/metrics') {
    return await handleGlobalMetrics(request, corsHeaders);
  }

  // Example: Mock health endpoint
  if (path === '/api/v1/health') {
    return await handleHealthCheck(request, corsHeaders);
  }

  // Proxy to backend (if configured)
  if (typeof BACKEND_URL !== 'undefined') {
    return await proxyToBackend(request, corsHeaders);
  }

  // Default API response
  return new Response(JSON.stringify({
    error: 'Not Found',
    message: 'API endpoint not found',
    available_endpoints: [
      '/api/v1/health',
      '/api/v1/tenant-info',
      '/api/v1/analytics/global/metrics'
    ]
  }), {
    status: 404,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders
    }
  });
}

/**
 * Mock tenant information endpoint
 */
async function handleTenantInfo(request, corsHeaders) {
  const tenantId = request.headers.get('X-Tenant-ID') || 'default';
  
  const tenantInfo = {
    tenant_id: tenantId,
    name: 'Movie Recap Service',
    plan: 'free',
    features: [
      'video_upload',
      'script_processing',
      'multi_language',
      '4k_upscaling'
    ],
    limits: {
      upload_size_mb: 100,
      monthly_quota: 10,
      storage_gb: 1
    },
    settings: {
      default_language: 'en',
      theme: 'dark',
      notifications: true
    },
    created_at: '2024-01-01T00:00:00Z',
    last_active: new Date().toISOString()
  };

  return new Response(JSON.stringify(tenantInfo), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=300',
      ...corsHeaders
    }
  });
}

/**
 * Mock global analytics endpoint
 */
async function handleGlobalMetrics(request, corsHeaders) {
  const metrics = {
    total_users: 1250,
    active_users_24h: 89,
    total_projects: 4567,
    videos_processed: 12834,
    storage_used_gb: 1567.8,
    processing_queue: 23,
    regions: {
      'us-east': { users: 456, latency_ms: 45 },
      'europe': { users: 334, latency_ms: 52 },
      'asia-pacific': { users: 287, latency_ms: 67 },
      'others': { users: 173, latency_ms: 78 }
    },
    languages: {
      en: 45.2,
      es: 18.7,
      fr: 12.3,
      de: 8.9,
      pt: 6.1,
      it: 4.2,
      others: 4.6
    },
    timestamp: new Date().toISOString()
  };

  return new Response(JSON.stringify(metrics), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=60',
      ...corsHeaders
    }
  });
}

/**
 * Health check endpoint
 */
async function handleHealthCheck(request, corsHeaders) {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    checks: {
      worker: 'ok',
      memory: 'ok',
      cpu: 'ok'
    },
    version: '1.0.0',
    uptime: Date.now()
  };

  return new Response(JSON.stringify(health), {
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders
    }
  });
}

/**
 * Proxy requests to backend server
 */
async function proxyToBackend(request, corsHeaders) {
  const url = new URL(request.url);
  const backendUrl = (typeof BACKEND_URL !== 'undefined' ? BACKEND_URL : DEFAULT_BACKEND_URL) + url.pathname + url.search;
  
  const modifiedRequest = new Request(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined
  });

  try {
    const response = await fetch(modifiedRequest);
    
    // Modify response headers to include CORS
    const modifiedResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers),
        ...corsHeaders
      }
    });

    return modifiedResponse;
  } catch (error) {
    return new Response(JSON.stringify({
      error: 'Backend Unavailable',
      message: 'Unable to connect to backend service',
      timestamp: new Date().toISOString()
    }), {
      status: 502,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
}