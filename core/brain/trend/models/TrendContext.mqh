//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TrendContext.mqh                                       |
//| Layer   : Brain / Trend / Models                                 |
//| Version : 2.0.0                                                  |
//| Purpose : Trend Analysis Context                                 |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_TRENDCONTEXT_MQH
#define CORE_BRAIN_TREND_MODELS_TRENDCONTEXT_MQH

//--------------------------------------------------
// Trend Context
//--------------------------------------------------

class CTrendContext
{
public:

   //==================================================
   // Market Identity
   //==================================================

   string Symbol;

   ENUM_TIMEFRAMES Timeframe;

   int Bars;

   int Shift;

   //==================================================
   // Current Timeframe
   //==================================================

   double Close;
   double Open;
   double High;
   double Low;

   //==================================================
   // Higher Timeframe
   //==================================================

   double HTFClose;
   double HTFHigh;
   double HTFLow;

   //==================================================
   // Market Information
   //==================================================

   double Spread;

   double ATR;

   double Volume;

   //--------------------------------------------------

   CTrendContext()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      Symbol = "";

      Timeframe = PERIOD_CURRENT;

      Bars = 0;

      Shift = 0;

      Close = 0.0;
      Open = 0.0;
      High = 0.0;
      Low = 0.0;

      HTFClose = 0.0;
      HTFHigh = 0.0;
      HTFLow = 0.0;

      Spread = 0.0;

      ATR = 0.0;

      Volume = 0.0;
   }
};

#endif
