//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestClosedBarSwingStructureProvider.mq5               |
//| Layer   : Tests / Brain / Trend                                  |
//| Version : 1.0.0                                                  |
//| Purpose : Verify actual completed-M5 swing source timing         |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/Brain.mqh"

int OnInit()
  {
   const datetime higherBarOpen=iTime(_Symbol,PERIOD_M15,1);
   const datetime observationTime=
      higherBarOpen+PeriodSeconds(PERIOD_M15);
   const datetime entryBarOpen=
      observationTime-PeriodSeconds(PERIOD_M5);
   const int entryShift=iBarShift(_Symbol,PERIOD_M5,entryBarOpen,true);

   CBrain brain;
   if(!brain.Initialize())
      return(INIT_FAILED);
   CConfirmedSwingStructureResult structure;
   const bool sourceValid=
      (higherBarOpen>0 && entryShift>=1 &&
       brain.ConfirmedSwingStructure(
          _Symbol,PERIOD_M5,entryShift,entryBarOpen,
          observationTime,structure));

   CConfirmedSwingStructureResult futureStructure;
   const bool futureRejected=
      !brain.ConfirmedSwingStructure(
         _Symbol,PERIOD_M5,entryShift,entryBarOpen,
         observationTime+PeriodSeconds(PERIOD_M5),futureStructure);
   const bool exactTiming=
      (entryShift>=1 && iTime(_Symbol,PERIOD_M5,entryShift)==entryBarOpen &&
       iTime(_Symbol,PERIOD_M5,entryShift-1)==observationTime);
   const bool valid=(sourceValid && futureRejected && exactTiming);

   Print("Closed-bar M5 swing source valid: ",sourceValid);
   Print("Closed-bar M5 swing future timing rejected: ",futureRejected);
   Print("Closed-bar M15/M5 exact alignment valid: ",exactTiming);
   Print("Closed-bar swing structure provider contract valid: ",valid);

   brain.Shutdown();
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
