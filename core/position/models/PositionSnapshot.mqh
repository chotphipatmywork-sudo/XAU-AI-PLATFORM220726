//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionSnapshot.mqh                                   |
//| Layer   : Core / Position / Models                               |
//| Version : 1.1.0                                                  |
//| Purpose : Position Snapshot                                      |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_MODELS_POSITIONSNAPSHOT_MQH
#define CORE_POSITION_MODELS_POSITIONSNAPSHOT_MQH

class CPositionSnapshot
{
public:

   bool   Valid;

   ulong  Ticket;

   string Symbol;

   double Volume;

   double OpenPrice;

   double StopLoss;

   double TakeProfit;

   double Profit;

public:

   CPositionSnapshot()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      Valid      = false;

      Ticket     = 0;

      Symbol     = "";

      Volume     = 0.0;

      OpenPrice  = 0.0;

      StopLoss   = 0.0;

      TakeProfit = 0.0;

      Profit     = 0.0;
   }
};

#endif