//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ATREngine.mqh                                          |
//| Layer   : Brain / Volatility / Engines                           |
//| Version : 2.1.0                                                  |
//| Purpose : ATR Analysis Engine                                    |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITY_ENGINES_ATRENGINE_MQH
#define CORE_BRAIN_VOLATILITY_ENGINES_ATRENGINE_MQH

#include "../config/VolatilityConfig.mqh"
#include "../models/VolatilityContext.mqh"
#include "../models/ATRResult.mqh"

#include "../../../indicators/models/IndicatorContext.mqh"
#include "../../../indicators/providers/ProviderManager.mqh"

//--------------------------------------------------

class CATREngine
{
private:

   CVolatilityConfig m_config;

public:

   //--------------------------------------------------

   void SetConfig(const CVolatilityConfig &config)
   {
      m_config = config;
   }

   //--------------------------------------------------

   CATRResult Analyze(const CVolatilityContext &context)
   {
      CATRResult result;

      if(context.Symbol=="" || context.Bars<=0 || context.Shift<0 ||
         m_config.ATRPeriod<=0 || m_config.AIRegimeLookback<=0)
         return result;

      //------------------------------------------
      // Build Indicator Context
      //------------------------------------------

      CIndicatorContext indicatorContext;

      indicatorContext.Symbol    = context.Symbol;
      indicatorContext.Timeframe = context.Timeframe;
      indicatorContext.Bars      = context.Bars;

      indicatorContext.Shift     = context.Shift;

      //------------------------------------------

      CProviderManager provider;

      provider.SetContext(indicatorContext);

      if(!provider.Update())
         return result;

      double atr_values[];
      if(!provider.GetATRValues(
            m_config.ATRPeriod,
            0,
            m_config.AIRegimeLookback+1,
            atr_values))
         return result;

      if(ArraySize(atr_values)<2 || atr_values[0]<=0.0 || atr_values[1]<=0.0)
         return result;

      result.Value=atr_values[0];
      const double previousATR=atr_values[1];

      //------------------------------------------
      // Simple Average
      //------------------------------------------

      result.Average =
         (result.Value + previousATR) * 0.5;

      //------------------------------------------
      // Ratio
      //------------------------------------------

      if(result.Average > 0.0)
         result.Ratio =
            result.Value / result.Average;
      else
         result.Ratio = 0.0;

      //------------------------------------------
      // Direction
      //------------------------------------------

      result.Increasing =
   (result.Value > previousATR);

      double regime_sum=0.0;
      int regime_count=0;
      for(int index=1; index<ArraySize(atr_values); index++)
      {
         if(atr_values[index]>0.0)
         {
            regime_sum+=atr_values[index];
            regime_count++;
         }
      }
      if(regime_count>0)
      {
         result.RegimeAverage=regime_sum/regime_count;
         if(result.RegimeAverage>0.0)
            result.RegimeRatio=result.Value/result.RegimeAverage;
      }

      return result;
   }
};

#endif
