//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeManager.mqh                                       |
//| Layer   : Core / Execution                                       |
//| Version : 4.0.0                                                  |
//| Purpose : Trade Manager                                          |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_TRADEMANAGER_MQH
#define CORE_EXECUTION_TRADEMANAGER_MQH

#include "models/ExecutionContext.mqh"
#include "models/ExecutionResult.mqh"

#include "TradeExecutor.mqh"
#include "PositionChecker.mqh"

//--------------------------------------------------
// Trade Manager
//--------------------------------------------------

class CTradeManager
{
private:

   CTradeExecutor   m_executor;
   CPositionChecker m_position;

public:

   //--------------------------------------------------
   // Execute Trade
   //--------------------------------------------------

   bool Execute(
      const CExecutionContext &context,
      CExecutionResult &result)
   {
      //--------------------------------------------------
      // Validate Symbol
      //--------------------------------------------------

      if(context.Symbol == "")
      {
         result.Success = false;
         result.Status  = EXECUTION_REJECTED;
         result.Message = "Invalid symbol.";

         return false;
      }

      //--------------------------------------------------
      // Existing Position
      //--------------------------------------------------

      if(m_position.HasOpenPosition(context.Symbol))
      {
         result.Success = false;
         result.Status  = EXECUTION_REJECTED;
         result.Message = "Position already exists.";

         return false;
      }

      //--------------------------------------------------
      // Execute
      //--------------------------------------------------

      return m_executor.Execute(result);
   }

   //--------------------------------------------------

   bool HasPosition(
      const string symbol) const
   {
      return m_position.HasOpenPosition(symbol);
   }

};

#endif