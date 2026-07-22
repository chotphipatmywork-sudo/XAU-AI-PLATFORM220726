//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestClosedBarBrainContext.mq5                          |
//| Layer   : Tests / Brain / Runtime                                |
//| Version : 1.0.0                                                  |
//| Purpose : Verify Shadow Brain observes only the closed bar       |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/BrainContextBuilder.mqh"

int OnInit()
  {
   CBrainContextBuilder builder;
   const CTrendContext trend=builder.BuildTrendContext(_Symbol,_Period,1);
   const CLiquidityContext liquidity=builder.BuildLiquidityContext(_Symbol,_Period,1);
   const CSessionContext session=builder.BuildSessionContext(_Symbol,_Period,1);
   const datetime expectedClose=iTime(_Symbol,_Period,1)+PeriodSeconds(_Period);

   const bool trendValid=(trend.Shift==1 &&
                          trend.Open==iOpen(_Symbol,_Period,1) &&
                          trend.High==iHigh(_Symbol,_Period,1) &&
                          trend.Low==iLow(_Symbol,_Period,1) &&
                          trend.Close==iClose(_Symbol,_Period,1));
   const bool liquidityValid=(liquidity.Shift==1 &&
                              liquidity.High==iHigh(_Symbol,_Period,1) &&
                              liquidity.Low==iLow(_Symbol,_Period,1) &&
                              liquidity.Close==iClose(_Symbol,_Period,1));
   const bool sessionValid=(session.CurrentTime==expectedClose);

   Print("Closed-bar Trend context valid: ",trendValid);
   Print("Closed-bar Liquidity context valid: ",liquidityValid);
   Print("Closed-bar Session timing valid: ",sessionValid);
   Print("Closed-bar Brain context valid: ",
         trendValid && liquidityValid && sessionValid);
   ExpertRemove();
   return(trendValid && liquidityValid && sessionValid ?
          INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
