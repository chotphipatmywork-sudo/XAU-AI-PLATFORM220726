//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LabelConfig.mqh                                        |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.1.0                                                  |
//| Purpose : Configuration for historical training labels           |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_LABELCONFIG_MQH
#define CORE_AI_MODELS_LABELCONFIG_MQH

class CLabelConfig
  {
private:
   int    m_horizon_bars;
   int    m_atr_period;
   double m_barrier_atr_multiplier;

public:
   CLabelConfig(void)
     {
      m_horizon_bars=16;
      m_atr_period=14;
      m_barrier_atr_multiplier=1.5;
     }

   int HorizonBars(void) const { return(m_horizon_bars); }
   int AtrPeriod(void) const { return(m_atr_period); }
   double BarrierAtrMultiplier(void) const { return(m_barrier_atr_multiplier); }

   bool Configure(const int horizon_bars,const int atr_period,const double barrier_atr_multiplier)
     {
      if(horizon_bars<=0 || atr_period<=0 || barrier_atr_multiplier<=0.0)
         return(false);
      m_horizon_bars=horizon_bars;
      m_atr_period=atr_period;
      m_barrier_atr_multiplier=barrier_atr_multiplier;
      return(true);
     }
  };

#endif
