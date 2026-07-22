//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeExitManager.mqh                                   |
//| Layer   : Core / Trade                                           |
//| Version : 1.0.0                                                  |
//| Purpose : Trade Exit Manager                                     |
//+------------------------------------------------------------------+

#ifndef CORE_TRADE_TRADEEXITMANAGER_MQH
#define CORE_TRADE_TRADEEXITMANAGER_MQH

#include "../position/PositionCloser.mqh"
#include "models/TradeState.mqh"

//--------------------------------------------------

class CTradeExitManager
{
private:

   CPositionCloser m_closer;

public:

   //--------------------------------------------------

   bool Exit(
      const string symbol)
   {
      return m_closer.Close(symbol);
   }

   //--------------------------------------------------

   bool Exit(
      CTradeState &state)
   {
      if(!state.Active)
         return false;

      if(!m_closer.Close(state.Symbol))
         return false;

      state.State  = TRADE_STATE_CLOSED;
      state.Active = false;

      return true;
   }

   //--------------------------------------------------

   bool EmergencyExit(
      CTradeState &state)
   {
      return Exit(state);
   }

   //--------------------------------------------------

   bool ExitAll()
   {
      return m_closer.CloseAll();
   }

};

#endif