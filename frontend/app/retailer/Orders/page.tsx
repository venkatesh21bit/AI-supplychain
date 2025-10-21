"use client";
import React, { useEffect, useState } from 'react';
import { fetchStockFromAPI, fetchOrdersFromAPI, ORDERS } from '../../../components/retailer/data/mockData';


const OrdersTab = () => {
  const [orders, setOrders] = useState(ORDERS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await fetchStockFromAPI();
        await fetchOrdersFromAPI();
        setOrders([...ORDERS]); // Force re-render with new data
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-xl">Loading orders...</div>
      </div>
    );
  }
  

  return (
    <>
      
      <div className="min-h-screen bg-black text-white">
        {/* Header */}
        <header className="p-4 border-b border-gray-800">
          <div className="flex items-center justify-between max-w-[1600px] mx-auto">
            <div className="text-xl font-bold">Store Name</div>
          </div>
        </header>

        {/* Main Content */}
        <main className="p-8 max-w-[1600px] mx-auto">
          <h2 className="text-xl font-bold mb-4">Recent Orders</h2>
          <div className="space-y-4">
            {orders.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                No orders found. Please check your connection or try again later.
              </div>
            ) : (
              orders.map(order => (
                <div key={order.id} className="bg-gray-900 p-4 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-bold">{order.id}</h3>
                      <p className="text-gray-400">{order.date}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">${order.total}</p>
                      <p className="text-gray-400">{order.status}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </main>
      </div>
    </>
  );
};

export default OrdersTab;