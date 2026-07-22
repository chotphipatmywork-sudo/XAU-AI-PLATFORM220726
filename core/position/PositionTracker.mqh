//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionTracker.mqh                                    |
//| Layer   : Core / Position                                        |
//| Version : 1.0.0                                                  |
//| Purpose : Track Current Position                                 |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_POSITIONTRACKER_MQH
#define CORE_POSITION_POSITIONTRACKER_MQH

#include <Trade/PositionInfo.mqh>

#include "models/PositionSnapshot.mqh"

//--------------------------------------------------

class CPositionTracker
{
private:

   CPositionInfo m_position;

public:

   //--------------------------------------------------

   bool Capture(
      const string symbol,
      CPositionSnapshot &snapshot)
   {
      snapshot.Reset();

      if(!m_position.Select(symbol))
         return false;

      snapshot.Valid      = true;
      snapshot.Symbol     = symbol;
      snapshot.Ticket     = m_position.Ticket();
      snapshot.Volume     = m_position.Volume();
      snapshot.OpenPrice  = m_position.PriceOpen();
      snapshot.StopLoss   = m_position.StopLoss();
      snapshot.TakeProfit = m_position.TakeProfit();
      snapshot.Profit     = m_position.Profit();

      return true;
   }
};

#endif