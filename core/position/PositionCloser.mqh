//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionCloser.mqh                                     |
//| Layer   : Core / Position                                        |
//| Version : 1.0.0                                                  |
//| Purpose : Position Close Utility                                 |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_POSITIONCLOSER_MQH
#define CORE_POSITION_POSITIONCLOSER_MQH

#include <Trade/Trade.mqh>

//--------------------------------------------------

class CPositionCloser
{
private:

   CTrade m_trade;

public:

   //--------------------------------------------------

   bool Close(const string symbol)
   {
      if(!PositionSelect(symbol))
         return false;

      return m_trade.PositionClose(symbol);
   }

   //--------------------------------------------------

   bool CloseByTicket(const ulong ticket)
   {
      if(!PositionSelectByTicket(ticket))
         return false;

      string symbol =
         PositionGetString(POSITION_SYMBOL);

      return m_trade.PositionClose(symbol);
   }

   //--------------------------------------------------

   bool CloseAll()
   {
      bool success = true;

      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         ulong ticket = PositionGetTicket(i);

         if(ticket == 0)
            continue;

         if(!PositionSelectByTicket(ticket))
            continue;

         string symbol =
            PositionGetString(POSITION_SYMBOL);

         if(!m_trade.PositionClose(symbol))
            success = false;
      }

      return success;
   }

};

#endif