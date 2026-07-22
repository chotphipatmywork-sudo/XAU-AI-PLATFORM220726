//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ClosedBarObservationTime.mqh                           |
//| Layer   : Core / Brain                                           |
//| Version : 1.0.0                                                  |
//| Purpose : Resolve a completed bar's observation timestamp        |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_CLOSEDBAROBSERVATIONTIME_MQH
#define CORE_BRAIN_CLOSEDBAROBSERVATIONTIME_MQH

class CClosedBarObservationTime
  {
public:
   bool Resolve(const datetime bar_open,
                const ENUM_TIMEFRAMES timeframe,
                datetime &observation_time)
     {
      observation_time=0;
      const int period_seconds=PeriodSeconds(timeframe);
      if(bar_open<=0 || period_seconds<=0)
         return(false);

      observation_time=bar_open+period_seconds;
      return(observation_time>bar_open);
     }
  };

#endif
