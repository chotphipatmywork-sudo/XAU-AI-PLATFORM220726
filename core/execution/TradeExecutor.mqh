//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeExecutor.mqh                                      |
//| Layer   : Core / Execution                                       |
//| Version : 4.2.0                                                  |
//| Purpose : Execute Trade                                          |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_TRADEEXECUTOR_MQH
#define CORE_EXECUTION_TRADEEXECUTOR_MQH

#include <Trade/Trade.mqh>

#include "models/ExecutionResult.mqh"

//--------------------------------------------------

class CTradeExecutor
{
private:

   CTrade m_trade;

private:

   //--------------------------------------------------

   double NormalizeLot(double lot)
   {
      double minLot =
         SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);

      double maxLot =
         SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);

      double step =
         SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

      if(step > 0.0)
         lot = MathFloor(lot / step) * step;

      if(lot < minLot)
         lot = minLot;

      if(lot > maxLot)
         lot = maxLot;

      return lot;
   }

public:

   //--------------------------------------------------

   bool Execute(CExecutionResult &result)
   {
      if(!result.Success)
         return false;

      //--------------------------------------------------
      // Validate
      //--------------------------------------------------

      if(result.LotSize <= 0.0)
      {
         result.Success = false;
         result.Status  = EXECUTION_FAILED;
         result.Message = "Invalid lot size.";

         return false;
      }

      if(result.OrderType != ORDER_TYPE_BUY &&
         result.OrderType != ORDER_TYPE_SELL)
      {
         result.Success = false;
         result.Status  = EXECUTION_FAILED;
         result.Message = "Invalid order type.";

         return false;
      }

      //--------------------------------------------------
      // Prepare
      //--------------------------------------------------

      result.LotSize =
         NormalizeLot(result.LotSize);

      m_trade.SetExpertMagicNumber(
         result.MagicNumber);

      bool ok = false;

      //--------------------------------------------------
      // BUY
      //--------------------------------------------------

      if(result.OrderType == ORDER_TYPE_BUY)
      {
         ok =
            m_trade.Buy(
               result.LotSize,
               _Symbol,
               result.EntryPrice,
               result.StopLoss,
               result.TakeProfit,
               result.Comment);
      }
      //--------------------------------------------------
      // SELL
      //--------------------------------------------------
      else
      {
         ok =
            m_trade.Sell(
               result.LotSize,
               _Symbol,
               result.EntryPrice,
               result.StopLoss,
               result.TakeProfit,
               result.Comment);
      }

      //--------------------------------------------------
      // Result
      //--------------------------------------------------

      if(ok)
      {
         result.Ticket =
            m_trade.ResultOrder();

         result.Success = true;
         result.Status  = EXECUTION_SUCCESS;
         result.Message = "Order executed successfully.";
      }
      else
      {
         result.Success = false;
         result.Status  = EXECUTION_FAILED;
         result.Message =
            m_trade.ResultRetcodeDescription();
      }

      return ok;
   }

};

#endif