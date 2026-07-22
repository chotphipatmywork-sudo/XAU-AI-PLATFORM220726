//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeStateManager.mqh                                  |
//| Layer   : Core / Execution                                       |
//| Version : 2.0.0                                                  |
//| Purpose : Trade Position State Management                        |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_TRADESTATEMANAGER_MQH
#define CORE_EXECUTION_TRADESTATEMANAGER_MQH

//--------------------------------------------------
// Trade State Manager
//--------------------------------------------------

class CTradeStateManager
{
private:

   int m_maxPositions;

public:

   //--------------------------------------------------

   CTradeStateManager()
   {
      m_maxPositions = 1;
   }

   //--------------------------------------------------

   bool Initialize()
   {
      return true;
   }

   //--------------------------------------------------

   void Shutdown()
   {
   }

   //--------------------------------------------------

   void SetMaxPositions(
      const int value)
   {
      if(value > 0)
         m_maxPositions = value;
   }

   //--------------------------------------------------

   int PositionCount() const
   {
      return PositionsTotal();
   }

   //--------------------------------------------------

   bool HasPosition(
      const string symbol) const
   {
      return PositionSelect(symbol);
   }

   //--------------------------------------------------

   bool AllowNewTrade(
      const string symbol) const
   {
      if(PositionCount() >= m_maxPositions)
         return false;

      if(HasPosition(symbol))
         return false;

      return true;
   }

   //--------------------------------------------------

   bool IsMaxPositionReached() const
   {
      return (PositionCount() >= m_maxPositions);
   }

};

#endif