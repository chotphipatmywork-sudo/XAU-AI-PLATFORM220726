//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeState.mqh                                         |
//| Layer   : Core / Trade / Models                                  |
//| Version : 1.0.0                                                  |
//| Purpose : Trade State Model                                      |
//+------------------------------------------------------------------+

#ifndef CORE_TRADE_MODELS_TRADESTATE_MQH
#define CORE_TRADE_MODELS_TRADESTATE_MQH

//--------------------------------------------------
// Trade State
//--------------------------------------------------

enum ENUM_TRADE_STATE
{
   TRADE_STATE_NONE = 0,

   TRADE_STATE_OPENING,

   TRADE_STATE_OPEN,

   TRADE_STATE_BREAK_EVEN,

   TRADE_STATE_TRAILING,

   TRADE_STATE_PARTIAL_CLOSE,

   TRADE_STATE_CLOSING,

   TRADE_STATE_CLOSED
};

//--------------------------------------------------
// Trade Snapshot
//--------------------------------------------------

class CTradeState
{
public:

   ENUM_TRADE_STATE State;

   ulong            Ticket;

   string           Symbol;

   double           EntryPrice;

   double           StopLoss;

   double           TakeProfit;

   double           Volume;

   double           Profit;

   bool             Active;

public:

   CTradeState()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      State       = TRADE_STATE_NONE;

      Ticket      = 0;

      Symbol      = "";

      EntryPrice  = 0.0;

      StopLoss    = 0.0;

      TakeProfit  = 0.0;

      Volume      = 0.0;

      Profit      = 0.0;

      Active      = false;
   }
};

#endif