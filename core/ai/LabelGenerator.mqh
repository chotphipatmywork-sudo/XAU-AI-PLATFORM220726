//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LabelGenerator.mqh                                     |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.1                                                  |
//| Purpose : Generate leakage-safe triple-barrier labels            |
//+------------------------------------------------------------------+

#ifndef CORE_AI_LABELGENERATOR_MQH
#define CORE_AI_LABELGENERATOR_MQH

#include "models/LabelConfig.mqh"

enum ENUM_AI_TRAINING_LABEL
  {
   AI_LABEL_SELL=-1,
   AI_LABEL_HOLD=0,
   AI_LABEL_BUY=1
  };

class CLabelGenerator
  {
private:
   CLabelConfig m_config;

public:
   bool Configure(const int horizon_bars,const int atr_period,const double barrier_atr_multiplier)
     {
      return(m_config.Configure(horizon_bars,atr_period,barrier_atr_multiplier));
     }

   // bars must be ordered from oldest to newest; entry_index is the feature bar.
   bool Generate(const MqlRates &bars[],const int entry_index,const double atr,ENUM_AI_TRAINING_LABEL &label) const
     {
      const int count=ArraySize(bars);
      if(entry_index<0 || entry_index>=count || atr<=0.0)
         return(false);
      const int last_index=entry_index+m_config.HorizonBars();
      // Label Schema 1.1.0 requires the complete future horizon. A shorter
      // tail window would create a different HOLD probability and target.
      if(last_index>=count)
         return(false);
      const double entry_price=bars[entry_index].close;
      const double barrier=atr*m_config.BarrierAtrMultiplier();
      const double upper=entry_price+barrier;
      const double lower=entry_price-barrier;

      for(int index=entry_index+1; index<=last_index; index++)
        {
         const bool hit_upper=(bars[index].high>=upper);
         const bool hit_lower=(bars[index].low<=lower);
         if(hit_upper && hit_lower)
            return(false);
         if(hit_upper)
           {
            label=AI_LABEL_BUY;
            return(true);
           }
         if(hit_lower)
           {
            label=AI_LABEL_SELL;
            return(true);
           }
        }

      label=AI_LABEL_HOLD;
      return(true);
     }
  };

#endif
