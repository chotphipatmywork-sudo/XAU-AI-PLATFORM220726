//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : IndicatorCache.mqh                                     |
//| Layer   : Indicators / Cache                                     |
//| Version : 1.0.0                                                  |
//| Purpose : Indicator Cache                                        |
//+------------------------------------------------------------------+

#ifndef CORE_INDICATORS_CACHE_INDICATORCACHE_MQH
#define CORE_INDICATORS_CACHE_INDICATORCACHE_MQH

#include "../models/EMAResult.mqh"
#include "../models/ATRResult.mqh"

class CIndicatorCache
{
public:

   CEMAResult EMA;

   CATRResult ATR;

   void Reset()
   {
      EMA = CEMAResult();
      ATR = CATRResult();
   }
};

#endif