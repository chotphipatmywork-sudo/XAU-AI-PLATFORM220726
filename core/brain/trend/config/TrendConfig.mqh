//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TrendConfig.mqh                                        |
//| Layer   : Brain / Trend                                          |
//| Version : 1.1.0                                                  |
//| Purpose : Trend Intelligence Configuration                       |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_TRENDCONFIG_MQH
#define CORE_BRAIN_TREND_TRENDCONFIG_MQH

//--------------------------------------------------
// Trend Configuration
//--------------------------------------------------

class CTrendConfig
{
public:

   // EMA
   int FastEMAPeriod;
   int SlowEMAPeriod;

   // Higher Time Frame EMA
   int HTF_EMAPeriod;

   // ADX
   int ADXPeriod;
   double ADXTrendThreshold;

   // Momentum
   int MomentumPeriod;

   // ATR
   int ATRPeriod;

   int AITrendLookbackBars;

   // BOS
   int BOSLookback;

   // Swing
   int SwingStrength;

   //--------------------------------------------------

   CTrendConfig()
   {
      FastEMAPeriod     = 50;
      SlowEMAPeriod     = 200;

      HTF_EMAPeriod     = 200;

      ADXPeriod         = 14;
      ADXTrendThreshold = 25.0;

      MomentumPeriod    = 14;

      ATRPeriod         = 14;

      AITrendLookbackBars = 16;

      BOSLookback       = 20;

      SwingStrength     = 3;
   }
};

#endif
