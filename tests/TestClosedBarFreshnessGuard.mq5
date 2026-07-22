//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestClosedBarFreshnessGuard.mq5                        |
//| Layer   : Tests / Runtime / Shadow                               |
//| Version : 1.0.0                                                  |
//| Purpose : Verify stale restart bars cannot reach Shadow Decision |
//+------------------------------------------------------------------+

#property strict

#include "../core/runtime/ClosedBarFreshnessGuard.mqh"

int OnInit()
  {
   CClosedBarFreshnessGuard guard;
   const datetime current=StringToTime("2026.07.13 00:01:00");
   const bool recent=guard.IsFresh(
      StringToTime("2026.07.13 00:00:00"),PERIOD_M1,current,120);
   const bool weekendRejected=!guard.IsFresh(
      StringToTime("2026.07.10 23:45:00"),PERIOD_M15,current,120);
   const bool futureRejected=!guard.IsFresh(
      StringToTime("2026.07.13 00:01:00"),PERIOD_M15,current,120);
   const bool valid=recent && weekendRejected && futureRejected;

   Print("Closed-bar recent decision valid: ",recent);
   Print("Closed-bar weekend decision rejected: ",weekendRejected);
   Print("Closed-bar future decision rejected: ",futureRejected);
   Print("Closed-bar freshness guard valid: ",valid);
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }

