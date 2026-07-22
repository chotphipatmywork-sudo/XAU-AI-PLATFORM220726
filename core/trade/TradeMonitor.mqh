//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeMonitor.mqh                                       |
//| Layer   : Core / Trade                                           |
//| Version : 1.0.1                                                  |
//| Purpose : Monitor Active Trade                                   |
//+------------------------------------------------------------------+

#ifndef CORE_TRADE_TRADEMONITOR_MQH
#define CORE_TRADE_TRADEMONITOR_MQH

#include "TradeStateMachine.mqh"

//--------------------------------------------------

class CTradeMonitor
{
private:

   CTradeStateMachine m_stateMachine;

public:

   //--------------------------------------------------

   void Reset()
   {
      m_stateMachine.Reset();
   }

   //--------------------------------------------------

   void Initialize(
      const ulong ticket,
      const string symbol,
      const double volume,
      const double entryPrice,
      const double stopLoss,
      const double takeProfit)
   {
      m_stateMachine.Initialize(
         ticket,
         symbol,
         volume,
         entryPrice,
         stopLoss,
         takeProfit);
   }

   //--------------------------------------------------

   void UpdateProfit(
      const double profit)
   {
      m_stateMachine.UpdateProfit(profit);
   }

   //--------------------------------------------------

   bool IsActive() const
   {
      return m_stateMachine.IsActive();
   }

   //--------------------------------------------------

   ENUM_TRADE_STATE GetState() const
   {
      return m_stateMachine.GetState();
   }

   //--------------------------------------------------

   CTradeState Snapshot() const
   {
      return m_stateMachine.GetSnapshot();
   }

};

#endif