//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : IndicatorContext.mqh                                   |
//| Layer   : Indicators / Models                                    |
//| Version : 1.0.0                                                  |
//| Purpose : Indicator Input Context                                |
//+------------------------------------------------------------------+

#ifndef CORE_INDICATORS_MODELS_INDICATORCONTEXT_MQH
#define CORE_INDICATORS_MODELS_INDICATORCONTEXT_MQH

class CIndicatorContext
{
public:

   string Symbol;

   ENUM_TIMEFRAMES Timeframe;

   int Bars;

   int Shift;

   CIndicatorContext()
   {
      Reset();
   }

   void Reset()
   {
      Symbol = "";

      Timeframe = PERIOD_CURRENT;

      Bars = 0;

      Shift = 0;
   }
};

#endif
