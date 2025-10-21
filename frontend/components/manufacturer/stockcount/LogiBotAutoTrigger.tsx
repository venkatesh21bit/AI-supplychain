/**
 * LOGI-BOT Auto-Trigger Hook
 * Automatically monitors stock levels and triggers LOGI-BOT workflows when critical thresholds are reached
 */

import { useEffect, useRef } from 'react';
import { API_URL, fetchWithAuth } from '@/utils/auth_fn';
import { StockItem } from './data';

interface LogiBotTriggerConfig {
  criticalThreshold: number;
  checkInterval: number;
  enabled: boolean;
}

const DEFAULT_CONFIG: LogiBotTriggerConfig = {
  criticalThreshold: 10,
  checkInterval: 5000, // 5 seconds
  enabled: true
};

export const useLogiBotAutoTrigger = (stockData: StockItem[], config: LogiBotTriggerConfig = DEFAULT_CONFIG) => {
  const previousStockRef = useRef<Map<string, number>>(new Map());
  const triggeredProductsRef = useRef<Set<string>>(new Set());
  const lastCheckRef = useRef<number>(0);

  useEffect(() => {
    if (!config.enabled || !stockData.length) return;

    const now = Date.now();
    
    // Throttle checks to prevent spam
    if (now - lastCheckRef.current < config.checkInterval) return;
    lastCheckRef.current = now;

    const checkAndTriggerAlerts = async () => {
      const companyId = localStorage.getItem('company_id');
      if (!companyId) {
        console.warn('No company ID found for LOGI-BOT triggers');
        return;
      }

      for (const stock of stockData) {
        const { productName, available } = stock;
        const previousStock = previousStockRef.current.get(productName);
        
        // Update previous stock tracking
        previousStockRef.current.set(productName, available);

        // Check if stock is critically low
        const isCriticallyLow = available <= config.criticalThreshold;
        const hasDecreased = previousStock !== undefined && available < previousStock;
        const alreadyTriggered = triggeredProductsRef.current.has(productName);

        if (isCriticallyLow && !alreadyTriggered) {
          console.log(`🚨 LOGI-BOT: Critical stock detected for ${productName} (${available} units)`);
          
          try {
            // Get product ID from backend
            const productsResponse = await fetchWithAuth(`${API_URL}/products/?company=${companyId}`);
            if (!productsResponse.ok) throw new Error('Failed to fetch products');
            
            const products = await productsResponse.json();
            const product = Array.isArray(products) 
              ? products.find(p => p.name === productName)
              : null;

            if (!product) {
              console.warn(`Product ${productName} not found in backend`);
              continue;
            }

            // Trigger LOGI-BOT inventory check
            const triggerResponse = await fetchWithAuth(`${API_URL}/agent/check-inventory/`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                product_id: product.product_id,
                company_id: parseInt(companyId)
              })
            });

            if (triggerResponse.ok) {
              const result = await triggerResponse.json();
              console.log(`✅ LOGI-BOT workflow triggered for ${productName}:`, {
                alertId: result.alert_id,
                executionId: result.execution_id,
                status: result.status
              });

              // Mark as triggered to prevent duplicate alerts
              triggeredProductsRef.current.add(productName);

              // Show user notification
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('🤖 LOGI-BOT Alert', {
                  body: `Critical stock alert triggered for ${productName} (${available} units)`,
                  icon: '/favicon.ico',
                  tag: `logibot-${productName}`
                });
              }

              // Optional: Show in-app notification
              dispatchCustomEvent('logibot-alert-triggered', {
                productName,
                available,
                alertId: result.alert_id,
                executionId: result.execution_id
              });

            } else {
              const error = await triggerResponse.text();
              console.error(`❌ Failed to trigger LOGI-BOT for ${productName}:`, error);
            }

          } catch (error) {
            console.error(`❌ Error triggering LOGI-BOT for ${productName}:`, error);
          }
        }

        // Reset trigger status if stock is replenished above threshold
        if (available > config.criticalThreshold && alreadyTriggered) {
          console.log(`✅ Stock replenished for ${productName}, clearing trigger flag`);
          triggeredProductsRef.current.delete(productName);
        }
      }
    };

    checkAndTriggerAlerts();
  }, [stockData, config]);

  // Request notification permission on first use
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        console.log('Notification permission:', permission);
      });
    }
  }, []);

  return {
    triggeredProducts: Array.from(triggeredProductsRef.current),
    resetTrigger: (productName: string) => {
      triggeredProductsRef.current.delete(productName);
    },
    resetAllTriggers: () => {
      triggeredProductsRef.current.clear();
    }
  };
};

// Helper function to dispatch custom events
function dispatchCustomEvent(eventName: string, detail: any) {
  const event = new CustomEvent(eventName, { detail });
  window.dispatchEvent(event);
}

// React component hook to listen for LOGI-BOT events
export const useLogiBotEventListener = () => {
  useEffect(() => {
    const handleAlert = (event: CustomEvent) => {
      console.log('🤖 LOGI-BOT Alert Event:', event.detail);
      // Handle the alert event (show toast, update UI, etc.)
    };

    window.addEventListener('logibot-alert-triggered', handleAlert as EventListener);
    
    return () => {
      window.removeEventListener('logibot-alert-triggered', handleAlert as EventListener);
    };
  }, []);
};