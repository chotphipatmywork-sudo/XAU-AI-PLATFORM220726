//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : VolatilityAnalyzer.mqh                                 |
//| Layer   : Brain                                                  |
//| Version : 1.1.0                                                  |
//| Purpose : Analyze runtime and AI volatility context              |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITYANALYZER_MQH
#define CORE_BRAIN_VOLATILITYANALYZER_MQH

#include "volatility/config/VolatilityConfig.mqh"

#include "volatility/models/VolatilityContext.mqh"
#include "volatility/models/VolatilityResult.mqh"
#include "volatility/models/ATRResult.mqh"

#include "volatility/engines/ATREngine.mqh"

//--------------------------------------------------

class CVolatilityAnalyzer
{
private:

   CVolatilityConfig m_config;

   CATREngine m_atrEngine;

public:

   void SetConfig(const CVolatilityConfig &config)
   {
      m_config = config;
      m_atrEngine.SetConfig(config);
   }

   //--------------------------------------------------

   CVolatilityResult Analyze(
      const CVolatilityContext &context)
   {
      CVolatilityResult result;

      CATRResult atr =
         m_atrEngine.Analyze(context);

      result.Reset();

      result.ATR = atr.Value;

      if(atr.Ratio >= 1.30)
      {
         result.State = VOLATILITY_HIGH;
      }
      else
      if(atr.Ratio <= 0.80)
      {
         result.State = VOLATILITY_LOW;
      }
      else
      {
         result.State = VOLATILITY_NORMAL;
      }

      result.Confidence = atr.Ratio;

      result.AIVolatilityChange=MathMax(0.0,MathMin(100.0,atr.Ratio*50.0));
      result.AIVolatilityRegime=MathMax(0.0,MathMin(100.0,atr.RegimeRatio*50.0));

      return result;
   }
};

#endif
