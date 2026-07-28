//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ADREngine.mqh                                          |
//| Layer   : Brain / Volatility / Engines                           |
//| Version : 1.0.0                                                  |
//| Purpose : Average Daily Range Analysis Engine                    |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITY_ENGINES_ADRENGINE_MQH
#define CORE_BRAIN_VOLATILITY_ENGINES_ADRENGINE_MQH

#include "../config/VolatilityConfig.mqh"
#include "../models/VolatilityContext.mqh"

class CADREngine
{
private:
   CVolatilityConfig m_config;

public:
   void SetConfig(const CVolatilityConfig &config)
   {
      m_config=config;
   }

   double Analyze(const CVolatilityContext &context)
   {
      if(context.Symbol=="" || m_config.ADRPeriod<=0)
         return 0.0;

      MqlRates rates[];
      const int copied=CopyRates(context.Symbol,PERIOD_D1,
                                  context.Shift+1,m_config.ADRPeriod,rates);
      if(copied!=m_config.ADRPeriod)
         return 0.0;

      double sum=0.0;
      for(int index=0; index<copied; index++)
         sum+=MathMax(0.0,rates[index].high-rates[index].low);
      return (copied>0 ? sum/copied : 0.0);
   }
};

#endif
