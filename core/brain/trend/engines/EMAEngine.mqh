//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : EMAEngine.mqh                                          |
//| Layer   : Brain / Trend / Engines                                |
//| Version : 3.0.0                                                  |
//| Purpose : EMA Engine                                             |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_ENGINES_EMAENGINE_MQH
#define CORE_BRAIN_TREND_ENGINES_EMAENGINE_MQH

#include "../config/TrendConfig.mqh"

#include "../../../indicators/models/EMAResult.mqh"
#include "../../../indicators/providers/ProviderManager.mqh"

//--------------------------------------------------
// EMA Engine
//--------------------------------------------------

class CEMAEngine
{
private:

   CTrendConfig m_config;

public:

   //--------------------------------------------------

   void SetConfig(const CTrendConfig &config)
   {
      m_config = config;
   }

   //--------------------------------------------------
   // Analyze
   //--------------------------------------------------

   CEMAResult Analyze(CProviderManager &provider)
   {
      CEMAResult result;

      result.FastEMA =
         provider.GetEMA(
            m_config.FastEMAPeriod,
            0);

      result.SlowEMA =
         provider.GetEMA(
            m_config.SlowEMAPeriod,
            0);

      result.Bullish =
         (result.FastEMA > result.SlowEMA);

      result.Bearish =
         (result.FastEMA < result.SlowEMA);

      return result;
   }
};

#endif