//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ClosedBarFreshnessGuard.mqh                            |
//| Layer   : Core / Runtime                                         |
//| Version : 1.0.0                                                  |
//| Purpose : Reject delayed closed-bar decisions after restart      |
//+------------------------------------------------------------------+

#ifndef CORE_RUNTIME_CLOSEDBARFRESHNESSGUARD_MQH
#define CORE_RUNTIME_CLOSEDBARFRESHNESSGUARD_MQH

class CClosedBarFreshnessGuard
  {
public:
   bool IsFresh(const datetime closedBar,
                const ENUM_TIMEFRAMES timeframe,
                const datetime currentTime,
                const int maximumLagSeconds) const
     {
      const int periodSeconds=PeriodSeconds(timeframe);
      if(closedBar<=0 || currentTime<=0 ||
         periodSeconds<=0 || maximumLagSeconds<=0)
         return(false);
      const long lag=(long)currentTime-
                     ((long)closedBar+(long)periodSeconds);
      return(lag>=0 && lag<=maximumLagSeconds);
     }
  };

#endif

