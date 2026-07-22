//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MarketContext.mqh                                      |
//| Layer   : Market / Models                                        |
//| Version : 2.0.0                                                  |
//| Purpose : Shared Market Context                                  |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_MODELS_MARKETCONTEXT_MQH
#define CORE_MARKET_MODELS_MARKETCONTEXT_MQH

class CMarketContext
{
public:

   //--------------------------------------------------
   // Symbol
   //--------------------------------------------------

   string Symbol;
   ENUM_TIMEFRAMES Timeframe;

   //--------------------------------------------------
   // Current Price
   //--------------------------------------------------

   double Bid;
   double Ask;
   double Spread;

   //--------------------------------------------------
   // Symbol Properties
   //--------------------------------------------------

   double Point;
   int    Digits;

   double TickSize;
   double TickValue;

   //--------------------------------------------------
   // Candle
   //--------------------------------------------------

   double Open;
   double High;
   double Low;
   double Close;

   long   Volume;

   //--------------------------------------------------
   // Time
   //--------------------------------------------------

   datetime ServerTime;
   datetime BarTime;

   //--------------------------------------------------
   // Market State
   //--------------------------------------------------

   int TrendState;
   int StructureState;

   //--------------------------------------------------
   // Validation
   //--------------------------------------------------

   bool Valid;

public:

   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CMarketContext()
   {
      Reset();
   }

   //--------------------------------------------------
   // Reset
   //--------------------------------------------------

   void Reset()
   {
      Symbol = "";
      Timeframe = PERIOD_CURRENT;

      Bid = 0.0;
      Ask = 0.0;
      Spread = 0.0;

      Point = 0.0;
      Digits = 0;

      TickSize = 0.0;
      TickValue = 0.0;

      Open = 0.0;
      High = 0.0;
      Low = 0.0;
      Close = 0.0;

      Volume = 0;

      ServerTime = 0;
      BarTime = 0;

      TrendState = 0;
      StructureState = 0;

      Valid = false;
   }
};

#endif
//+------------------------------------------------------------------+