//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SlopeEngine.mqh                                        |
//| Layer   : Brain / Trend / Engines                                |
//| Version : 3.0.0                                                  |
//| Purpose : EMA Slope Analysis Engine                              |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_ENGINES_SLOPEENGINE_MQH
#define CORE_BRAIN_TREND_ENGINES_SLOPEENGINE_MQH

#include "../config/TrendConfig.mqh"

#include "../../../indicators/providers/ProviderManager.mqh"

#include "../models/SlopeResult.mqh"

//--------------------------------------------------
// Slope Engine
//--------------------------------------------------

class CSlopeEngine
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

   CSlopeResult Analyze(CProviderManager &provider)
   {
      CSlopeResult result;

      //------------------------------------------------
      // Read EMA
      //------------------------------------------------

      double emaCurrent =
         provider.GetEMA(
            m_config.FastEMAPeriod,
            0);

      double emaPrevious =
         provider.GetEMA(
            m_config.FastEMAPeriod,
            1);

      //------------------------------------------------
      // Calculate Slope
      //------------------------------------------------

      result.Value =
         emaCurrent - emaPrevious;

      //------------------------------------------------

      result.Rising =
         (result.Value > 0.0);

      result.Falling =
         (result.Value < 0.0);

      return result;
   }
};

#endif