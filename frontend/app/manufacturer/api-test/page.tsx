/**
 * Simple test component to verify LOGI-BOT API endpoints
 */

"use client";

import React, { useState } from 'react';
import { API_URL, fetchWithAuth, getAuthToken } from '@/utils/auth_fn';

export default function LogiBotApiTester() {
  const [results, setResults] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const testEndpoints = async () => {
    setLoading(true);
    const token = getAuthToken();
    
    console.log('Current token:', token ? token.substring(0, 50) + '...' : 'No token');
    
    try {
      const endpoints = [
        { name: 'Agent Status', url: `${API_URL}/agent/status/` },
        { name: 'Agent Alerts', url: `${API_URL}/agent/alerts/` },
        { name: 'Agent Executions', url: `${API_URL}/agent/executions/` }
      ];

      const testResults: any = {};
      
      for (const endpoint of endpoints) {
        try {
          const response = await fetchWithAuth(endpoint.url);
          testResults[endpoint.name] = {
            status: response.status,
            ok: response.ok,
            data: response.ok ? await response.json() : await response.text()
          };
        } catch (error) {
          testResults[endpoint.name] = {
            status: 'ERROR',
            error: error instanceof Error ? error.message : String(error)
          };
        }
      }
      
      setResults(testResults);
    } catch (error) {
      console.error('Test error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-900 text-white min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">LOGI-BOT API Tester</h1>
        
        <button
          onClick={testEndpoints}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 mb-6"
        >
          {loading ? 'Testing...' : 'Test API Endpoints'}
        </button>

        {Object.keys(results).length > 0 && (
          <div className="space-y-4">
            {Object.entries(results).map(([name, result]: [string, any]) => (
              <div key={name} className="bg-gray-800 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-blue-400 mb-2">{name}</h3>
                <div className="space-y-2">
                  <div className={`text-sm ${result.ok ? 'text-green-400' : 'text-red-400'}`}>
                    Status: {result.status} {result.ok ? '✅' : '❌'}
                  </div>
                  {result.error && (
                    <div className="text-red-400 text-sm">
                      Error: {result.error}
                    </div>
                  )}
                  {result.data && (
                    <div className="bg-gray-700 p-3 rounded text-xs overflow-auto max-h-40">
                      <pre>{JSON.stringify(result.data, null, 2)}</pre>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 bg-gray-800 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-400 mb-2">Current Authentication</h3>
          <div className="text-sm space-y-1">
            <div>Token exists: {getAuthToken() ? '✅' : '❌'}</div>
            <div>Company ID: {localStorage.getItem('company_id') || 'Not set'}</div>
            <div>User: {localStorage.getItem('username') || 'Not set'}</div>
          </div>
        </div>
      </div>
    </div>
  );
}