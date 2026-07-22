//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionChecker.mqh                                    |
//| Layer   : Core / Execution                                       |
//| Version : 2.0.0                                                  |
//| Purpose : Position Checker                                       |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_POSITIONCHECKER_MQH
#define CORE_EXECUTION_POSITIONCHECKER_MQH

class CPositionChecker
{
public:

   //--------------------------------------------------
   // Check position by symbol
   //--------------------------------------------------

   bool HasOpenPosition(
      const string symbol) const
   {
      return PositionSelect(symbol);
   }

   //--------------------------------------------------
   // Total positions
   //--------------------------------------------------

   int TotalPositions() const
   {
      return PositionsTotal();
   }

   //--------------------------------------------------
   // Check BUY position
   //--------------------------------------------------

   bool HasBuyPosition(
      const string symbol) const
   {
      if(!PositionSelect(symbol))
         return false;

      return ((ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE)
               == POSITION_TYPE_BUY);
   }

   //--------------------------------------------------
   // Check SELL position
   //--------------------------------------------------

   bool HasSellPosition(
      const string symbol) const
   {
      if(!PositionSelect(symbol))
         return false;

      return ((ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE)
               == POSITION_TYPE_SELL);
   }

   //--------------------------------------------------
   // Position Volume
   //--------------------------------------------------

   double GetVolume(
      const string symbol) const
   {
      if(!PositionSelect(symbol))
         return 0.0;

      return PositionGetDouble(POSITION_VOLUME);
   }

};

#endif