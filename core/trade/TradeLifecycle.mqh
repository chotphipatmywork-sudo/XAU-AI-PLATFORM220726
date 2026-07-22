//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeLifecycle.mqh                                     |
//| Layer   : Core / Trade                                           |
//| Version : 1.1.0                                                  |
//| Purpose : Trade Lifecycle Controller                             |
//+------------------------------------------------------------------+

#ifndef CORE_TRADE_TRADELIFECYCLE_MQH
#define CORE_TRADE_TRADELIFECYCLE_MQH

#include "TradeMonitor.mqh"
#include "TradeExitManager.mqh"
#include "TradeStateMachine.mqh"

#include "models/TradeState.mqh"

#include "../execution/models/ExecutionContext.mqh"
#include "../execution/models/ExecutionResult.mqh"

//--------------------------------------------------

class CTradeLifecycle
{
private:

   CTradeMonitor      m_monitor;

   CTradeExitManager  m_exit;

   CTradeStateMachine m_stateMachine;

public:

   //--------------------------------------------------

   void Initialize(
      const ulong ticket,
      const string symbol,
      const double volume,
      const double entryPrice,
      const double stopLoss,
      const double takeProfit)
   {
      m_monitor.Initialize(
         ticket,
         symbol,
         volume,
         entryPrice,
         stopLoss,
         takeProfit);

      m_stateMachine.Initialize(
         ticket,
         symbol,
         volume,
         entryPrice,
         stopLoss,
         takeProfit);
   }

   //--------------------------------------------------
   // Start Trade From Execution Result
   //--------------------------------------------------

   bool StartFromExecution(
      CExecutionContext &context,
      CExecutionResult &result)
   {
      if(!result.Success)
         return false;

      if(result.Ticket == 0)
         return false;

      if(context.Symbol == "")
         return false;


      Initialize(
         result.Ticket,
         context.Symbol,
         result.LotSize,
         result.EntryPrice,
         result.StopLoss,
         result.TakeProfit);


      return true;
   }

   //--------------------------------------------------

   void UpdateProfit(
      const double profit)
   {
      m_monitor.UpdateProfit(profit);
   }

   //--------------------------------------------------

   ENUM_TRADE_STATE State() const
   {
      return m_stateMachine.GetState();
   }

   //--------------------------------------------------

   bool IsActive() const
   {
      return m_monitor.IsActive();
   }

   //--------------------------------------------------

   bool ExitCurrentTrade()
   {
      CTradeState state =
         m_stateMachine.GetSnapshot();

      if(!m_exit.Exit(state))
         return false;

      m_stateMachine.Close();

      return true;
   }

   //--------------------------------------------------

   CTradeState Snapshot() const
   {
      return m_stateMachine.GetSnapshot();
   }

};

#endif