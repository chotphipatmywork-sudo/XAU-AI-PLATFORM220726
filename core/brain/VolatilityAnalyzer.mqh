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
#include "volatility/engines/ADREngine.mqh"
#include "volatility/engines/ExpansionEngine.mqh"
#include "volatility/engines/CompressionEngine.mqh"

//--------------------------------------------------

class CVolatilityAnalyzer
{
private:

   CVolatilityConfig m_config;

   CATREngine m_atrEngine;
   CADREngine m_adrEngine;
   CExpansionEngine m_expansionEngine;
   CCompressionEngine m_compressionEngine;

public:

   void SetConfig(const CVolatilityConfig &config)
   {
      m_config = config;
      m_atrEngine.SetConfig(config);
      m_adrEngine.SetConfig(config);
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
      result.ADR = m_adrEngine.Analyze(context);

      if(atr.Value<=0.0 || atr.RegimeAverage<=0.0)
         return result;

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

      result.ExpansionScore=m_expansionEngine.Analyze(atr.RegimeRatio);
      result.CompressionScore=m_compressionEngine.Analyze(atr.RegimeRatio);

      if(result.ExpansionScore>result.CompressionScore &&
         result.ExpansionScore>=20.0)
         result.State=VOLATILITY_EXPANDING;
      else if(result.CompressionScore>result.ExpansionScore &&
              result.CompressionScore>=20.0)
         result.State=VOLATILITY_CONTRACTING;

      result.AIVolatilityChange=MathMax(0.0,MathMin(100.0,atr.Ratio*50.0));
      result.AIVolatilityRegime=MathMax(0.0,MathMin(100.0,atr.RegimeRatio*50.0));

      return result;
   }
};

#endif
