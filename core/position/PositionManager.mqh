//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionManager.mqh                                    |
//| Layer   : Core / Position                                        |
//| Version : 3.0.0                                                  |
//| Purpose : Central Position Manager                               |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_POSITIONMANAGER_MQH
#define CORE_POSITION_POSITIONMANAGER_MQH

#include "PositionTracker.mqh"
#include "PositionLifecycle.mqh"
#include "PositionCloser.mqh"
#include "PositionModifier.mqh"

#include "models/PositionSnapshot.mqh"

//--------------------------------------------------

class CPositionManager
{
private:

   CPositionTracker   m_tracker;
   CPositionLifecycle m_lifecycle;
   CPositionCloser    m_closer;
   CPositionModifier  m_modifier;

public:

   //--------------------------------------------------

   bool HasPosition(const string symbol)
   {
      return PositionSelect(symbol);
   }

   //--------------------------------------------------

   int TotalPositions()
   {
      return PositionsTotal();
   }

   //--------------------------------------------------

   bool GetSnapshot(
      const string symbol,
      CPositionSnapshot &snapshot)
   {
      return m_tracker.Capture(symbol, snapshot);
   }

   //--------------------------------------------------

   bool Update(
      const string symbol,
      CPositionSnapshot &snapshot)
   {
      return m_lifecycle.Process(symbol, snapshot);
   }

   //--------------------------------------------------

   bool Modify(
      const string symbol,
      const double stopLoss,
      const double takeProfit)
   {
      return m_modifier.Modify(
         symbol,
         stopLoss,
         takeProfit);
   }

   //--------------------------------------------------

   bool ClosePosition(const string symbol)
   {
      return m_closer.Close(symbol);
   }

   //--------------------------------------------------

   bool CloseAll()
   {
      return m_closer.CloseAll();
   }

};

#endif