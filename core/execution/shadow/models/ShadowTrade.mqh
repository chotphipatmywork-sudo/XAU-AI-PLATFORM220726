//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowTrade.mqh                                        |
//| Layer   : Core / Execution / Shadow / Models                     |
//| Version : 1.0.0                                                  |
//| Purpose : Paper position state without broker ownership          |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_SHADOW_MODELS_SHADOWTRADE_MQH
#define CORE_EXECUTION_SHADOW_MODELS_SHADOWTRADE_MQH

class CShadowTrade
  {
public:
   ulong           Ticket;
   string          Symbol;
   ENUM_TIMEFRAMES Timeframe;
   ENUM_ORDER_TYPE OrderType;
   double          Volume;
   double          EntryPrice;
   double          CurrentPrice;
   double          StopLoss;
   double          TakeProfit;
   double          ProfitPoints;
   datetime        OpenTime;
   datetime        CloseTime;
   bool            Active;
   string          CloseReason;

   CShadowTrade()
     {
      Reset();
     }

   void Reset()
     {
      Ticket=0;
      Symbol="";
      Timeframe=PERIOD_CURRENT;
      OrderType=ORDER_TYPE_BUY;
      Volume=0.0;
      EntryPrice=0.0;
      CurrentPrice=0.0;
      StopLoss=0.0;
      TakeProfit=0.0;
      ProfitPoints=0.0;
      OpenTime=0;
      CloseTime=0;
      Active=false;
      CloseReason="";
     }
  };

#endif
