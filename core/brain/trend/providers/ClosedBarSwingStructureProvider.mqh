//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ClosedBarSwingStructureProvider.mqh                   |
//| Layer   : Brain / Trend / Providers                             |
//| Version : 1.0.0                                                  |
//| Purpose : Load confirmed swing evidence from completed bars      |
//+------------------------------------------------------------------+

#ifndef XAU_CLOSED_SWING_PROVIDER_MQH
#define XAU_CLOSED_SWING_PROVIDER_MQH

#include "../engines/ConfirmedSwingStructureEngine.mqh"

class CClosedBarSwingStructureProvider
  {
private:
   CConfirmedSwingStructureEngine m_engine;

public:
   CClosedBarSwingStructureProvider()
     {
      m_engine.Configure(2,2,64);
     }

   bool Analyze(const string symbol,
                const ENUM_TIMEFRAMES timeframe,
                const int shift,
                const datetime expectedBarOpen,
                const datetime observationTime,
                CConfirmedSwingStructureResult &result) const
     {
      result.Reset();
      if(symbol=="" || timeframe!=PERIOD_M5 || shift<1 ||
         expectedBarOpen<=0 || observationTime<=0 ||
         expectedBarOpen+PeriodSeconds(timeframe)!=observationTime)
         return(false);

      if(iTime(symbol,timeframe,shift)!=expectedBarOpen ||
         iTime(symbol,timeframe,shift-1)!=observationTime)
         return(false);

      const int count=m_engine.RequiredBars();
      double highs[];
      double lows[];
      double closes[];
      ArrayResize(highs,count);
      ArrayResize(lows,count);
      ArrayResize(closes,count);

      for(int index=0; index<count; index++)
        {
         const int sourceShift=shift+index;
         const datetime sourceOpen=iTime(symbol,timeframe,sourceShift);
         if(sourceOpen<=0 || sourceOpen>expectedBarOpen ||
            sourceOpen+PeriodSeconds(timeframe)>observationTime)
            return(false);
         highs[index]=iHigh(symbol,timeframe,sourceShift);
         lows[index]=iLow(symbol,timeframe,sourceShift);
         closes[index]=iClose(symbol,timeframe,sourceShift);
         if(!MathIsValidNumber(highs[index]) ||
            !MathIsValidNumber(lows[index]) ||
            !MathIsValidNumber(closes[index]) ||
            highs[index]<=0.0 || lows[index]<=0.0 || closes[index]<=0.0 ||
            highs[index]<lows[index])
            return(false);
        }

      result=m_engine.Analyze(highs,lows,closes);
      return(true);
     }
  };

#endif
