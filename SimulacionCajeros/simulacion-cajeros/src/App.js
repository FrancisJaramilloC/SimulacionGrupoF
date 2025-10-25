import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Plus, Minus, Clock, Users, ShoppingCart } from 'lucide-react';

const SupermarketSimulation = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState(1000);
  const [currentTime, setCurrentTime] = useState(0);
  
  // Configuración inicial
  const [numNormalCashiers, setNumNormalCashiers] = useState(2);
  const [hasExpressCashier, setHasExpressCashier] = useState(true);
  
  // Configuración de clientes por caja (editable en el código)
  const [customersPerNormalCashier, setCustomersPerNormalCashier] = useState([5, 4]); // [Caja1, Caja2, ...]
  const [customersInExpress, setCustomersInExpress] = useState(6);
  
  // Estado de las cajas
  const [cashiers, setCashiers] = useState([]);
  const [simulationLog, setSimulationLog] = useState([]);
  const [statistics, setStatistics] = useState({
    totalCustomersServed: 0,
    averageWaitTime: 0,
    fastestCashier: null
  });

  // Tipos de cajero
  const CASHIER_TYPES = {
    EXPERT: { name: 'Experto', scanTime: 5, color: 'bg-green-100' },
    BEGINNER: { name: 'Principiante', scanTime: 9, color: 'bg-yellow-100' }
  };

  // Inicializar cajas
  const initializeCashiers = () => {
    const newCashiers = [];
    
    // Cajas normales
    for (let i = 0; i < numNormalCashiers; i++) {
      const isExpert = Math.random() > 0.5;
      const type = isExpert ? CASHIER_TYPES.EXPERT : CASHIER_TYPES.BEGINNER;
      const numCustomers = customersPerNormalCashier[i] || 3; // Por defecto 3 si no está definido
      newCashiers.push({
        id: i + 1,
        type: 'normal',
        expertise: type,
        queue: generateQueue(numCustomers),
        currentCustomer: null,
        timeRemaining: 0,
        totalTimeSpent: 0,
        customersServed: 0
      });
    }
    
    // Caja express
    if (hasExpressCashier) {
      const isExpert = Math.random() > 0.5;
      const type = isExpert ? CASHIER_TYPES.EXPERT : CASHIER_TYPES.BEGINNER;
      newCashiers.push({
        id: numNormalCashiers + 1,
        type: 'express',
        expertise: type,
        queue: generateQueue(customersInExpress, true),
        currentCustomer: null,
        timeRemaining: 0,
        totalTimeSpent: 0,
        customersServed: 0
      });
    }
    
    setCashiers(newCashiers);
    setCurrentTime(0);
    setSimulationLog([]);
    addLog('Simulación inicializada');
  };

  // Generar cola de clientes
  const generateQueue = (numPeople, isExpress = false) => {
    const queue = [];
    for (let i = 0; i < numPeople; i++) {
      const maxItems = isExpress ? 10 : 50;
      const minItems = isExpress ? 1 : 1;
      queue.push({
        id: Math.random().toString(36).substr(2, 9),
        items: Math.floor(Math.random() * (maxItems - minItems + 1)) + minItems,
        paymentTime: Math.floor(Math.random() * 16) + 15,
        arrivalTime: currentTime
      });
    }
    return queue;
  };

  // Agregar log
  const addLog = (message) => {
    setSimulationLog(prev => [...prev, { time: currentTime, message }].slice(-10));
  };

  // Calcular tiempo total para un cliente
  const calculateCustomerTime = (customer, scanTime) => {
    return (customer.items * scanTime) + customer.paymentTime;
  };

  // Calcular tiempo estimado de una caja
  const calculateCashierTime = (cashier) => {
    let totalTime = cashier.timeRemaining;
    cashier.queue.forEach(customer => {
      totalTime += calculateCustomerTime(customer, cashier.expertise.scanTime);
    });
    return totalTime;
  };

  // Simular paso de tiempo
  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      setCurrentTime(prev => prev + 1);
      
      setCashiers(prevCashiers => {
        const newCashiers = prevCashiers.map(cashier => {
          const newCashier = { ...cashier };
          
          // Si no hay cliente actual, tomar uno de la cola
          if (!newCashier.currentCustomer && newCashier.queue.length > 0) {
            newCashier.currentCustomer = newCashier.queue[0];
            newCashier.queue = newCashier.queue.slice(1);
            newCashier.timeRemaining = calculateCustomerTime(
              newCashier.currentCustomer,
              newCashier.expertise.scanTime
            );
            addLog(`Caja ${newCashier.id} (${newCashier.type}): Atendiendo cliente con ${newCashier.currentCustomer.items} artículos`);
          }
          
          // Si hay cliente, reducir tiempo
          if (newCashier.currentCustomer && newCashier.timeRemaining > 0) {
            newCashier.timeRemaining -= 1;
            newCashier.totalTimeSpent += 1;
            
            // Cliente terminó
            if (newCashier.timeRemaining <= 0) {
              const waitTime = currentTime - newCashier.currentCustomer.arrivalTime;
              addLog(`Caja ${newCashier.id}: Cliente completado (esperó ${waitTime}s)`);
              newCashier.customersServed += 1;
              newCashier.currentCustomer = null;
            }
          }
          
          return newCashier;
        });
        
        // Verificar si terminó la simulación
        const allEmpty = newCashiers.every(c => 
          c.queue.length === 0 && !c.currentCustomer
        );
        
        if (allEmpty) {
          setIsRunning(false);
          addLog('¡Simulación completada!');
          calculateStatistics(newCashiers);
        }
        
        return newCashiers;
      });
    }, speed);

    return () => clearInterval(interval);
  }, [isRunning, speed, currentTime]);

  // Calcular estadísticas
  const calculateStatistics = (cashiers) => {
    const totalServed = cashiers.reduce((sum, c) => sum + c.customersServed, 0);
    const avgTime = cashiers.reduce((sum, c) => sum + c.totalTimeSpent, 0) / cashiers.length;
    const fastest = cashiers.reduce((prev, curr) => 
      curr.totalTimeSpent < prev.totalTimeSpent ? curr : prev
    );
    
    setStatistics({
      totalCustomersServed: totalServed,
      averageWaitTime: Math.round(avgTime),
      fastestCashier: fastest
    });
  };

  // Inicializar al montar
  useEffect(() => {
    initializeCashiers();
  }, []);

  // Determinar mejor caja para nuevo cliente
  const getBestCashier = () => {
    if (cashiers.length === 0) return null;
    return cashiers.reduce((best, current) => {
      const currentTime = calculateCashierTime(current);
      const bestTime = calculateCashierTime(best);
      return currentTime < bestTime ? current : best;
    });
  };

  const bestCashier = getBestCashier();

  return (
    <div className="w-full h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6 overflow-auto">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🏪 Simulación de Cajeros de Supermercado
          </h1>
          <p className="text-gray-600">Determina qué caja es más eficiente</p>
        </div>

        {/* Controles */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex flex-wrap gap-4 items-center justify-between">
              <div className="flex gap-2">
                <button
                  onClick={() => setIsRunning(!isRunning)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                >
                  {isRunning ? <Pause size={20} /> : <Play size={20} />}
                  {isRunning ? 'Pausar' : 'Iniciar'}
                </button>
                <button
                  onClick={initializeCashiers}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
                >
                  <RotateCcw size={20} />
                  Reiniciar
                </button>
              </div>

              <div className="flex items-center gap-2">
                <Clock size={20} className="text-gray-600" />
                <span className="font-bold text-lg">{currentTime}s</span>
              </div>
            </div>
            
            {/* Configuración de clientes */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-bold text-gray-700 mb-3">⚙️ Configuración de Clientes (editable en código)</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array.from({ length: numNormalCashiers }).map((_, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 min-w-24">Caja Normal {i + 1}:</label>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={customersPerNormalCashier[i] || 0}
                      onChange={(e) => {
                        const newCustomers = [...customersPerNormalCashier];
                        newCustomers[i] = parseInt(e.target.value) || 0;
                        setCustomersPerNormalCashier(newCustomers);
                      }}
                      disabled={isRunning}
                      className="w-20 px-2 py-1 border border-gray-300 rounded text-center"
                    />
                    <span className="text-xs text-gray-500">clientes</span>
                  </div>
                ))}
                {hasExpressCashier && (
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 min-w-24">Caja Express:</label>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={customersInExpress}
                      onChange={(e) => setCustomersInExpress(parseInt(e.target.value) || 0)}
                      disabled={isRunning}
                      className="w-20 px-2 py-1 border border-gray-300 rounded text-center"
                    />
                    <span className="text-xs text-gray-500">clientes</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Recomendación */}
        {bestCashier && (
          <div className="bg-green-100 border-2 border-green-400 rounded-lg p-4 mb-6">
            <h3 className="font-bold text-green-800 mb-2">💡 Recomendación para nuevo cliente:</h3>
            <p className="text-green-700">
              La Caja {bestCashier.id} ({bestCashier.type === 'express' ? 'Express' : 'Normal'}) 
              es la más rápida con un tiempo estimado de <strong>{calculateCashierTime(bestCashier)}s</strong>
              {' '}(Cajero {bestCashier.expertise.name})
            </p>
          </div>
        )}

        {/* Cajas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {cashiers.map(cashier => (
            <div
              key={cashier.id}
              className={`${
                cashier.type === 'express' 
                  ? 'bg-gradient-to-br from-purple-100 to-pink-100 border-purple-400' 
                  : 'bg-white border-gray-300'
              } border-2 rounded-lg shadow-lg p-4 ${
                bestCashier?.id === cashier.id ? 'ring-4 ring-green-400' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xl font-bold">
                  {cashier.type === 'express' ? '⚡ ' : '🏪 '}
                  Caja {cashier.id}
                </h3>
                <div className="flex flex-col items-end gap-1">
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                    cashier.expertise.name === 'Experto' 
                      ? 'bg-green-500 text-white' 
                      : 'bg-yellow-500 text-white'
                  }`}>
                    {cashier.expertise.name === 'Experto' ? '⭐ ' : '📚 '}
                    {cashier.expertise.name}
                  </span>
                  <span className="text-xs text-gray-600">
                    {cashier.expertise.scanTime}s/artículo
                  </span>
                </div>
              </div>

              <div className="text-sm text-gray-600 mb-3 space-y-1">
                <div className="flex items-center gap-2">
                  <Users size={16} />
                  <span>En fila: {cashier.queue.length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock size={16} />
                  <span>Tiempo estimado: {calculateCashierTime(cashier)}s</span>
                </div>
                <div className="flex items-center gap-2">
                  <ShoppingCart size={16} />
                  <span>Atendidos: {cashier.customersServed}</span>
                </div>
              </div>

              {/* Cliente actual */}
              {cashier.currentCustomer && (
                <div className="bg-blue-100 border-2 border-blue-400 rounded-lg p-3 mb-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold">👤 Atendiendo</span>
                    <span className="text-xs bg-blue-200 px-2 py-1 rounded">
                      {cashier.timeRemaining}s restantes
                    </span>
                  </div>
                  <div className="text-xs text-gray-700 mt-1">
                    {cashier.currentCustomer.items} artículos
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2 mt-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          100 - (cashier.timeRemaining / 
                          calculateCustomerTime(cashier.currentCustomer, cashier.expertise.scanTime) * 100)
                        }%`
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Cola */}
              <div className="space-y-2">
                {cashier.queue.slice(0, 5).map((customer, idx) => (
                  <div
                    key={customer.id}
                    className="bg-gray-100 rounded p-2 text-xs flex items-center justify-between"
                  >
                    <span>👤 Cliente {idx + 1}</span>
                    <span className="font-bold">{customer.items} items</span>
                  </div>
                ))}
                {cashier.queue.length > 5 && (
                  <div className="text-xs text-center text-gray-500">
                    +{cashier.queue.length - 5} más...
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Estadísticas y Log */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Estadísticas */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4">📊 Estadísticas</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Clientes atendidos:</span>
                <span className="font-bold">{statistics.totalCustomersServed}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tiempo promedio por caja:</span>
                <span className="font-bold">{statistics.averageWaitTime}s</span>
              </div>
              {statistics.fastestCashier && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Caja más eficiente:</span>
                  <span className="font-bold">
                    Caja {statistics.fastestCashier.id} 
                    ({statistics.fastestCashier.type === 'express' ? 'Express' : 'Normal'})
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Log */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4">📋 Registro de eventos</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {simulationLog.map((log, idx) => (
                <div key={idx} className="text-sm border-l-2 border-blue-400 pl-3 py-1">
                  <span className="text-gray-500 text-xs">[{log.time}s]</span>{' '}
                  <span className="text-gray-700">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupermarketSimulation;