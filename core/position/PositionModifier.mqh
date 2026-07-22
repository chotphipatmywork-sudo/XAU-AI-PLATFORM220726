//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionModifier.mqh                                   |
//| Layer   : Core / Position                                        |
//| Version : 1.0.0                                                  |
//| Purpose : Position Modify Utility                                |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_POSITIONMODIFIER_MQH
#define CORE_POSITION_POSITIONMODIFIER_MQH

#include <Trade/Trade.mqh>

//--------------------------------------------------

class CPositionModifier
{
private:

   CTrade m_trade;

public:

   //--------------------------------------------------

   bool Modify(
      const string symbol,
      const double stopLoss,
      const double takeProfit)
   {
      if(!PositionSelect(symbol))
         return false;

      return m_trade.PositionModify(
         symbol,
         stopLoss,
         takeProfit);
   }

   //--------------------------------------------------

   bool ModifyByTicket(
      const ulong ticket,
      const double stopLoss,
      const double takeProfit)
   {
      if(!PositionSelectByTicket(ticket))
         return false;

      string symbol =
         PositionGetString(POSITION_SYMBOL);

      return m_trade.PositionModify(
         symbol,
         stopLoss,
         takeProfit);
   }

   //--------------------------------------------------

   bool UpdateStopLoss(
      const string symbol,
      const double stopLoss)
   {
      if(!PositionSelect(symbol))
         return false;

      double takeProfit =
         PositionGetDouble(POSITION_TP);

      return m_trade.PositionModify(
         symbol,
         stopLoss,
         takeProfit);
   }

   //--------------------------------------------------

   bool UpdateTakeProfit(
      const string symbol,
      const double takeProfit)
   {
      if(!PositionSelect(symbol))
         return false;

      double stopLoss =
         PositionGetDouble(POSITION_SL);

      return m_trade.PositionModify(
         symbol,
         stopLoss,
         takeProfit);
   }
};

#endif